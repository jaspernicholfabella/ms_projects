import os
import shutil
import csv
import pickle
from pathlib import Path

class Checkpoint:
    pickle_file = None
    pickle_path = None
    list_file = None

    def __init__(self, pickle_file):
        self.pickle_file = pickle_file
        self.pickle_path = '/'.join(pickle_file.split('/')[:-1])
        self.list_file = pickle_file.replace('.pickle', '_list_data.csv')


    def save_checkpoint(self, list_data):
        """
        save data on a list as checkpoints
        :param list_data: the data you want to save mostly string (url, or plain string)
        :return: None, Generate .csv data on the pickling folder
        """
        field_names = ['ListData']
        dict_data = {"ListData": list_data}

        with open(self.list_file, 'a') as csv_file:
            dict_object = csv.DictWriter(csv_file, fieldnames=field_names)
            dict_object.writerow(dict_data)

    def load_checkpoint(self, filter_from_list=None):
        """
        load checkpoint as (filtered list return all values that are not on checkpoint list)
        or return the checkpoint list value if "filter_from_list" param is none
        :param filter_from_list: liste value to compare with the checkpoint list
        :return: list
        """

        file_exists = os.path.isfile(self.list_file)

        if file_exists:
            saved_list = []
            with open(self.list_file, 'r') as f:
                reader = csv.reader(f)
                for data in reader:
                    saved_list.append(data[0])

            if filter_from_list is not None:
                new_list = [val for val in filter_from_list if val not in saved_list]
                return new_list

            return saved_list

        return filter_from_list

    def save_data(self, object_to_save):
        """
        save data type values to a pickle file
        :param object_to_save: any python data type
        :return: None, Generate Pickle file
        """
        print(self.pickle_path)
        Path(self.pickle_path).mkdir(parents=True, exists_ok=True)
        with open(self.pickle_file, 'wb') as handle:
            pickle.dump(object_to_save, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def load_data(self):
        """ load pickle file data"""
        if os.path.exists(self.pickle_file):
            with open(self.pickle_file, 'rb') as handle:
                return pickle.load(handle)
        return None

    def clean(self):
        """ delete pickle file directory """
        shutil.rmtree(self.pickle_path)