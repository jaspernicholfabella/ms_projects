<<<<<<< HEAD
import logging
from pathlib import Path
from datetime import datetime
import sys
sys.path.append('../')
import pyersq.utils as squ
import time

class Runner:
    """For data collectionn""" #pylint: disable=too-many-instance-attributes
    def __init__(self,argv,output_prefix='',output_subdir=None,output_type='csv',**kwargs):
        self.args = self.parse_args(argv,**kwargs)
        self.outdir = Path(self.args.outdir)
        self.timestamp = datetime.now().strftime('%Y%m%d')
        self.prefix = f"{output_prefix}_{self.timestamp}"
        self.output_subdir = output_subdir
        self.checkpoint = None
        self.__argv = argv
        self.__output_type = output_type

    def run(self, **kwargs):
        """ Run the process """
        start_time = time.time()

        logging.info("Making Directory if directory empty")
        Path(f'{self.outdir}/{self.output_subdir}').mkdir(parents=True, exist_ok=True)
        Path(f'{self.outdir}/t').rmdir()

        logging.info("Get raw data")
        raw = self.get_raw(**kwargs)

        logging.info("Save raw data")
        self.save_raw(raw,**kwargs)

        logging.info("Normalize data")
        data = self.normalize(raw, **kwargs)

        logging.info("Save normalized data to output")
        self.save_output(data, **kwargs)

        logging.info("Notify downstream or send email")
        self.notify(data, **kwargs)

        logging.info("Clean up")
        self.cleanup()

        print("--- %s seconds ---" % (time.time() - start_time))
        return data

    def run2(self, **kwargs):
        """ Run the process """
        logging.info("Get raw data")
        raw = self.get_raw(**kwargs)

        logging.info("Clean up")
        self.cleanup()


    def get_raw(self, **kwargs):
        """Get raw data from the source"""
        raise ImplementationException('get_raw')

    def normalize(self,raw,**kwargs):
        """Normalize raw and return final result"""
        logging.info('Implement normalize() in your sub-class if needed, otherwise return raw: raw=%s, kwargs=%s',type(raw),kwargs)

    def save_raw(self,raw,**kwargs):
        """Save raw data to file"""
        logging.info('Implement save_raw() yourself if needed: raw=%s, kwargs=%s', type(raw),kwargs)

    def save_output(self, data, **kwargs):
        """Save final data to output file"""
        if self.__output_type == 'csv':
            func = self.save_output_csv
        elif self.__output_type == 'excel':
            func = self.save_output_excel
        else:
            raise UnsupportedOutputTypeException(self.__output_type)
        return func(data,**kwargs)

    def save_output_csv(self,data,index=False,**kwargs):
        """Save data into csv file
        :param data: pandas DataFrame
        """
        file = self.get_output_file('csv')
        logging.info("Save final output: file=%s, index=%s, kwargs=%s",file,index,kwargs)
        data.to_csv(file,index=index,**kwargs)
        return file

    def save_output_excel(self,data, index=False, **kwargs):
        """ Save final data to output file
        :param data: pandas DataFrame
        """
        file = self.get_output_file('xlsx')
        logging.info("Save final output: file=%s, index=%s, kwargs=%s", file,index,kwargs)
        data.to_excel(file,index=index,**kwargs)
        return file

    def get_output_file(self,suffix):
        """Return output file path"""
        _path = self.outdir / self.output_subdir if self.output_subdir else self.outdir
        _path = f'{_path}/{self.prefix}.{suffix}'
        return _path

    def notify(self, data, **kwargs):
        """Notify downstream or send email"""
        logging.info("Override to add customized feature: data=%s, kwargs=%s, args=%s",type(data),kwargs,self.args)

    def cleanup(self):
        """Clean up"""
        if self.checkpoint:
            self.checkpoint.clean()

    def parse_args(self,argv,description="Collect data from websites",**kwargs):
        """Parse command line arguments"""
        parser = squ.get_parser(description)
        parser.add_argument("--to",help='Send DQ output to email group')
        parser.add_argument("--cc",help='cc DQ output to email group')

        logging.info("Parse input arguments: argv=%s",argv)
        args, unknown = parser.parse_known_args(argv[1:])
        logging.info("args=%s, unknown=%s",args,unknown)
        return args

    @staticmethod
    def set_parser(parser, **kwargs):
        """
        Override this method to add or modify more input arguments. E.g.:
        """
        return parser

class UnsupportedOutputTypeException(Exception):
    '''Exception raised for unsupported file type'''
    def __init__(self,output_type):
        self.output_type = output_type
        super().__init__(f'Supported output types are [csv,excel]: output_type={self.output_type}'
                         'Implement save_output() in your sub-class')

class ImplementationException(Exception):
    """Exception raised for implementing a method"""
    def __init__(self,method):
        self.method = method
        super().__init__(f'Please implement {self.method}() in your sub-class')


=======
import logging
from pathlib import Path
from datetime import datetime
import sys
sys.path.append('../')
import pyersq.utils as squ
import time

class Runner:
    """For data collectionn""" #pylint: disable=too-many-instance-attributes
    def __init__(self,argv,output_prefix='',output_subdir=None,output_type='csv',**kwargs):
        self.args = self.parse_args(argv,**kwargs)
        self.outdir = Path(self.args.outdir)
        self.timestamp = datetime.now().strftime('%Y%m%d')
        self.prefix = f"{output_prefix}_{self.timestamp}"
        self.output_subdir = output_subdir
        self.checkpoint = None
        self.__argv = argv
        self.__output_type = output_type

    def run(self, **kwargs):
        """ Run the process """
        start_time = time.time()

        logging.info("Making Directory if directory empty")
        Path(f'{self.outdir}/{self.output_subdir}').mkdir(parents=True, exist_ok=True)
        Path(f'{self.outdir}/t').rmdir()

        logging.info("Get raw data")
        raw = self.get_raw(**kwargs)

        logging.info("Save raw data")
        self.save_raw(raw,**kwargs)

        logging.info("Normalize data")
        data = self.normalize(raw, **kwargs)

        logging.info("Save normalized data to output")
        self.save_output(data, **kwargs)

        logging.info("Notify downstream or send email")
        self.notify(data, **kwargs)

        logging.info("Clean up")
        self.cleanup()

        print("--- %s seconds ---" % (time.time() - start_time))
        return data

    def run2(self, **kwargs):
        """ Run the process """
        logging.info("Get raw data")
        raw = self.get_raw(**kwargs)

        logging.info("Clean up")
        self.cleanup()


    def get_raw(self, **kwargs):
        """Get raw data from the source"""
        raise ImplementationException('get_raw')

    def normalize(self,raw,**kwargs):
        """Normalize raw and return final result"""
        logging.info('Implement normalize() in your sub-class if needed, otherwise return raw: raw=%s, kwargs=%s',type(raw),kwargs)

    def save_raw(self,raw,**kwargs):
        """Save raw data to file"""
        logging.info('Implement save_raw() yourself if needed: raw=%s, kwargs=%s', type(raw),kwargs)

    def save_output(self, data, **kwargs):
        """Save final data to output file"""
        if self.__output_type == 'csv':
            func = self.save_output_csv
        elif self.__output_type == 'excel':
            func = self.save_output_excel
        else:
            raise UnsupportedOutputTypeException(self.__output_type)
        return func(data,**kwargs)

    def save_output_csv(self,data,index=False,**kwargs):
        """Save data into csv file
        :param data: pandas DataFrame
        """
        file = self.get_output_file('csv')
        logging.info("Save final output: file=%s, index=%s, kwargs=%s",file,index,kwargs)
        data.to_csv(file,index=index,**kwargs)
        return file

    def save_output_excel(self,data, index=False, **kwargs):
        """ Save final data to output file
        :param data: pandas DataFrame
        """
        file = self.get_output_file('xlsx')
        logging.info("Save final output: file=%s, index=%s, kwargs=%s", file,index,kwargs)
        data.to_excel(file,index=index,**kwargs)
        return file

    def get_output_file(self,suffix):
        """Return output file path"""
        _path = self.outdir / self.output_subdir if self.output_subdir else self.outdir
        _path = f'{_path}/{self.prefix}.{suffix}'
        return _path

    def notify(self, data, **kwargs):
        """Notify downstream or send email"""
        logging.info("Override to add customized feature: data=%s, kwargs=%s, args=%s",type(data),kwargs,self.args)

    def cleanup(self):
        """Clean up"""
        if self.checkpoint:
            self.checkpoint.clean()

    def parse_args(self,argv,description="Collect data from websites",**kwargs):
        """Parse command line arguments"""
        parser = squ.get_parser(description)
        parser.add_argument("--to",help='Send DQ output to email group')
        parser.add_argument("--cc",help='cc DQ output to email group')

        logging.info("Parse input arguments: argv=%s",argv)
        args, unknown = parser.parse_known_args(argv[1:])
        logging.info("args=%s, unknown=%s",args,unknown)
        return args

    @staticmethod
    def set_parser(parser, **kwargs):
        """
        Override this method to add or modify more input arguments. E.g.:
        """
        return parser

class UnsupportedOutputTypeException(Exception):
    '''Exception raised for unsupported file type'''
    def __init__(self,output_type):
        self.output_type = output_type
        super().__init__(f'Supported output types are [csv,excel]: output_type={self.output_type}'
                         'Implement save_output() in your sub-class')

class ImplementationException(Exception):
    """Exception raised for implementing a method"""
    def __init__(self,method):
        self.method = method
        super().__init__(f'Please implement {self.method}() in your sub-class')


>>>>>>> 9c7a2ecb38c8c26c66a48d4e0105990ca3cfbfd4
