""" utils.parse v0_1 , responsible for parser scripts"""
from ..logger import logger


def is_partial_run(parser):
    """ Create a Partial run based on an argument """
    logger.info('Executing Code on Partial Run')
    return parser.parse_args().run


def end_partial_run(fetch, header=None):  # pylint: disable=unused-argument
    """ End Partial Run based on an argument """
    logger.info('Ending Partial Run')
    fetch_arr = fetch
    fetch_arr.append(['#----------------------End of Partial Run---------------------#'])
    return fetch_arr