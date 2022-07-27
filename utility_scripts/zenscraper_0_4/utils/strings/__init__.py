import re
from ..logger import logger

def strip_html(value):
    """
    Strip HTML tags from string
    :param value: input a string
    :return:
    """
    logger.info('stripping HTML tags from string')
    string = re.compile(r"<.*?>|=")
    return string.sub("", value)


def remove_non_digits(value):
    """
    remove non digit character from a string
    :param value: string
    :return: string
    """
    output = ''.join(c for c in value if c.isdigit())
    return output


def remove_digits(value):
    """
    remove all digit character in a string
    :param value: string
    :return: string
    """
    output = ''.join(c for c in value if not c.isdigit())
    return output


def remove_non_alpha_char(value):
    """
    remove non letters
    :param value: string
    :return: string
    """
    value = value.lower()
    output = ''
    letter = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
              'q', 'r', 's', 't', 'u',
              'v', 'w', 'x', 'y', 'z']
    for char in value:
        if any(x == char for x in letter):
            output += char
    return output


def is_month(month):
    """
    Check if the string is a month
    :param month: month string 3 characters only
    :return: bool
    """
    if any(x == month.lower() for x in
           ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov',
            'dec']):
        return True
    return False


def spanish_months(month):
    """
    check for spanish month
    :param month: check month
    :return: return month equivalent in string 'jan, feb, mar'
    """
    spanish_months_dict = {
        'enero': 'jan', 'febrero': 'feb', 'marzo': 'mar',
        'abril': 'apr', 'mayo': 'may', 'junio': 'jun',
        'julio': 'jul', 'agosto': 'aug', 'septiembre': 'sep',
        'octubre': 'oct', 'noviembre': 'nov', 'diciembre': 'dec'
    }
    return spanish_months_dict[month.lower().strip()]


def quarter_to_month(month):
    """
    get quarter month based on quarter data
    :param month: input quarter e.g. q1 = mar
    :return: month string
    """
    quarter_dict = {
        'q1': 'mar',
        'q2': 'jun',
        'q3': 'sep',
        'q4': 'dec'
    }
    return quarter_dict[month.lower().strip()]


def contains_number(value):
    """check if a string contains number"""
    for character in value:
        if character.isdigit():
            return True
    return False