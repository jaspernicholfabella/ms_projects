""" Common utils"""
import os
import re
import logging
from pathlib import Path
import getpass
import pickle
import smtplib
import mimetypes
from email.message import EmailMessage
from email.mime.text import MIMEText
import csv
import functools
import time
import datetime
import argparse
import pandas as pd
import sys
sys.path.append('../scripts')
from pyersq.zenscraper import UtilFunctions

def send_email(to,subject,body=None,files=None,cc=None):
    """
    Send email with attachment
    msg = send_email(getpass.getuser(), 'test', body='body', files=['out/test.csv'],cc=getpass.getuser())
    msg = send_email(getpass.getuser(), 'test', body='<html><body>body</body></html>', files=['out/test.csv'],cc=getpass.getuser())
    """
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = getpass.getuser()
    msg['To'] = to
    if cc:
        msg['Cc'] = cc
    msg.make_mixed()

    logging.info('Add body')
    if body is None:
        pass
    if re.search(r'^\s*<html', body, re.IGNORECASE):
        msg.attach(MIMEText(body,"html"))
    else:
        msg.attach(MIMEText(body,"plain"))

    logging.info('Add attachments')
    for file in files or []:
        logging.info(f'Attach file: %s',file)
        attach_file(msg,file)

    #Send out Email
    logging.info(f'Sending email: %s', msg.items())
    with smtplib.SMTP('msa-hub') as f:
        f.send_message(msg)

    return msg

def attach_file(msg: EmailMessage, file) -> EmailMessage:
    """
    :param msg: Email Message
    :param file: full file path to be attached
    """
    file = Path(file)
    ctype, encoding = mimetypes.guess_type(file)
    if ctype is None or encoding is not None:
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)

    logging.info(f'Add attachment: file ={file}, maintype={maintype}, subtype={subtype}')
    with open(file, 'rb') as fp:
        msg.add_attachment(fp.read(), maintype=maintype, subtype=subtype, filename=file.name)

    return msg

def mkdir(file):
    '''
    Make Directory based on filename
    '''
    UtilFunctions().create_directory(file)

def check_dir_writable(outdir, exception=Exception) -> str:
    """ Return the outdir if it is writable, otherwise raise an exception"""
    mkdir(f'{outdir}/t')
    if os.access(outdir, os.W_OK) and os.path.isdir(outdir):
        return outdir
    raise exception(f"{outdir} is not writable or does not exist.")

class Checkpoint:
    """Save and load checkpoint """
    def __init__(self,writable_dir,filename='checkpoint'):
        self._dir = check_dir_writable(writable_dir)
        self._file = Path(writable_dir, filename + '.pickle')

    def save(self,data):
        """ Save data into pickle file for resuming the flow """
        logging.info("Save checkpoint to : %s", self._file)
        pickle.dump(data, open(self._file, 'wb'))

    def load(self):
        """Load checkpoint from pickle file if exists, to resume the flow"""
        data = None
        if self._file.is_file():
            logging.info("Load checkpoint from : %s",self._file)
            try:  # Overcome pandas 1.3.0 bug
                data = pickle.load(open(self._file, 'rb'))
            except TypeError:
                data = pd.read_pickle(self._file)
            return data

    def clean(self):
        """Remove checkpoint file"""
        if self._file.is_file():
            self._file.unlink()


def timer(func):
    """Decorator the print the runtime of a function"""
    @functools.wraps(func)
    def wrapper_timer(*args,**kwargs):
        start_time = time.perf_counter()
        value = func(*args,**kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(f'Finished {func.__name__!r} in {run_time:.6f} secs')
        return value
    return wrapper_timer

def retry(exception=Exception, tries=1, init_wait=60, factor=2):
    """ Decorator to retry a function

    :param exception: Exception(s) that trigger a retry, can be a tuple.
    :param tries: Total tries
    :param init_wait: Seconds to firs retry
    :param factor: Backoff Multiplier
    :return:
    """
    def retry_decorator(func):
        @functools.wraps(func)
        def retry_wrapper(*args,**kwargs):
            fmsg = f"args={args if args else ''}, kwargs = {kwargs}"

            for _try in range(tries):
                try:
                    logging.info("Trying(%s): func=%s", _try+1, func.__name__)
                    logging.debug(fmsg)
                    return func(*args, **kwargs)
                except Exception as e:
                    _delay = (factor**_try) * init_wait
                    if _try == tries - 1:
                        raise
                    logging.exception(e)
                    logging.info("Retrying on: func=%s, delay=%s seconds, exception=%s", func.__name__, _delay, repr(e))
                    time.sleep(_delay)
            return retry_wrapper
        return retry_decorator


def get_parser(description='Collect data from websites',formatter_class=argparse.ArgumentDefaultsHelpFormatter):
    """ Create a common parser for input arguments"""
    parser = argparse.ArgumentParser(description=description,formatter_class=formatter_class)
    parser.add_argument("-r","--run",action='store_true', help='Run the whole process, otherwise do dryrun only')
    parser.add_argument("-o","--outdir", type=check_dir_writable,help='Output directory to store the results', required=True)
    return parser

def csv_write_dict(rows: list, csvfile, header:list=None, mode: str='w', encoding: str='utf8',
                   extrasaction: str='raise', date_field: str = 'FetchDate') -> None:
    """
    Write a list of dict to the csv file. The date_field will be inserted as the 1st field in the file, and take the date today.
    :param rows: List of dicts, e.g. [{'A':1, 'B':10}, {'A':2, 'B': 20}]
    :param csvfile: CSV file path
    :param header: a list for field names, If ignored, it will take the keys of the 1st row.
    :param mode: same to open()
    :param encoding: same to open()
    :param extrasaction: for extra fields in dict, 'raise' a ValueError, 'ignore'
    :param date_field: the field name for the date when the data are collected
    :return:
    """
    with open(csvfile,mode,newline='',encoding=encoding) as file:
        if header:
            fields = list(header)
        else:
            fields = list(rows[0].keys())
        date_field = f'_{date_field}' if date_field in fields else date_field
        fields = [date_field] + fields #if name clash

        #Add the date today when data are collected
        _date = str(datetime.date.today())
        logging.info('Writing to: csvfile=%s, fields=%s',csvfile,fields)
        with open(csvfile, mode, newline='',encoding=encoding) as file:
            writer = csv.DictWriter(file,fieldnames=fields,extrasaction=extrasaction)
            writer.writeheader()
            writer.writerows(rows)


def save_excel(df,prefix:str, index: bool = False, **kwargs):
    """
    Save pandas.DataFrame to an output Excel
    :param df: pandas.DataFrame
    :param prefix: path + file name prefix
    :param index: Write row names (index)
    :return:
    """
    file = prefix + '.xlsx'
    logging.info("Save output to: file=%s",file)
    df.to_excel(file,index=index,**kwargs)
    return file
