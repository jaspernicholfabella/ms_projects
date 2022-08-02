""" utils.files v_0_1 - functions to manipulate files"""
import os
from os.path import dirname, join, abspath
import sys
import glob
import shutil
from pathlib import Path
import pandas as pd
from ..logger import logger

sys.path.insert(0, abspath(join(dirname(__file__), "../../..")))
from pyersq.requests_wrapper import RequestsWrapper


def create_directory(dir_name):
    """ Create a directory """
    logger.info('Creating Directory')
    Path(dir_name).mkdir(parents=True, exist_ok=True)

def download_file(url, destination_path=""):
    """
    :param url: url to download file
    :param destination_path: directory with file name to store image data
    :return:
    """
    req = RequestsWrapper()
    response = req.get(url)
    logger.info(f"downloading: {url}")  # pylint: disable=logging-fstring-interpolation
    filename = url.split("/")[-1]
    if destination_path == "":
        file_destination = filename
    else:
        create_directory(destination_path)
        file_destination = f"{destination_path}/{filename}"

    with open(file_destination, "wb") as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

    logger.error('error on file download')

def get_input_file(input_path, header='', sheet_number=0, to_dict_val=''):
    """
    :param input_path: path of input file
    :param header: the name of the header to scrape
    :param has_sheet: check if csv or excel file input
    :param to_dict_val: if this has value this will serve as the dictionary value and
    header is the dictionary key
    :return: list or dictionary if to_dict_val is not ''
    """
    logger.warning('importing file from %s', input_path)
    if 'xlsx' in input_path:
        to_find_data = pd.read_excel(os.path.abspath(input_path), sheet_name=sheet_number)
    else:
        to_find_data = pd.read_csv(os.path.abspath(input_path))

    if to_dict_val == '':
        return to_find_data[header].drop_duplicates().to_list()

    return to_find_data.set_index(header).to_dict()[to_dict_val]

def get_file_list(file_dir='.', file_extension='txt', is_latest_only=False):
    """
    get list of all file in the directory
    :param file_dir: file directory string
    :param file_extension: file extension ('txt') is the default
    :param is_latest_only: if this is True, then return only the latest file in the directory
    :return: list of directory , or a single directory
    """
    try:
        list_of_files = glob.glob(
            f'{file_dir}/*.{file_extension}')  # * means all if need specific format then *.csv
        if is_latest_only:
            return max(list_of_files, key=os.path.getctime)
    except ValueError:
        logger.error('No %s files found', file_extension)
        return []
    return list_of_files
