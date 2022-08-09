import os
import sys
import shutil
import fileinput
import logging
import requests
sys.path.append('../../../scripts')
from ms_projects.utility_scripts.zenscraper_0_3 import ZenScraper
from jil_maker import JILCreate

def replace_text(text_file, to_replace, will_replace):
    """ Python program to replace text in a file """
    text_to_search = to_replace
    text_to_replace = will_replace
    file_to_search = text_file
    temp_file = open(text_file, 'r+')

    for line in fileinput.input(file_to_search):
        temp_file.write(line.replace(text_to_search, text_to_replace))
    temp_file.close()

def delete_lines(fname = 'test.txt', x = 8):
    with open(fname, "r") as f:
        lines = f.readlines()
    with open(fname, "w") as f:
        for line in lines:
            if len(line) <= x:
                f.write(line)

def create_files(input_dict):
    ZenScraper().utils.files.create_directory(input_dict['name'])
    python_file = f"{input_dict['name']}/{input_dict['python_file']}"
    shutil.copy('base_template.base', python_file)
    replace_text(python_file, '@@@description@@@', input_dict['description'])
    replace_text(python_file, '@@@class_name@@@', input_dict['python_file'].replace('.py', '').title())
    replace_text(python_file, '@@@python_file@@@',input_dict['python_file'].replace('.py', ''))
    # test_file = f"{input_dict['name']}/test_{input_dict['python_file']}"
    # shutil.copy('test_template.base', test_file)
    # replace_text(test_file, '@@@class_name@@@', input_dict['python_file'].replace('.py', '').title())
    # replace_text(test_file, '@@@dir_name@@@', input_dict['name'])
    # replace_text(test_file, '@@@file_name@@@', input_dict['python_file'].replace('.py', ''))
    # replace_text(test_file, '@@@python_file@@@', input_dict['python_file'])
    # jil = JILCreate(**input_dict)
    # jil.generate_jil()

if __name__ == '__main__':
    input_dict = {
        'name': 'us_usedphones',
        'description': 'Gazelle Website',
        'python_file': 'gazelle.py',
        'output_dir': 'us_usedphones/',
        # 'date_to_run': 'run_calendar: 5thDayOfEveryQuarter',
        'date_to_run': 'days_of_week: all',
        'qa_start_time': '1:00',
        'prod_start_time': '1:30'
    }

    create_files(input_dict)

