class Parse:
    logger = None

    def __init__(self, logger):
        self.logger = logger


    def is_partial_run(self, parser):
        """ Create a Partial run based on an argument """
        self.logger.info('Executing Code on Partial Run')
        return parser.parse_args().run


    def end_partial_run(self, fetch, header=None):  # pylint: disable=unused-argument
        """ End Partial Run based on an argument """
        self.logger.info('Ending Partial Run')
        fetch_arr = fetch
        fetch_arr.append(['#----------------------End of Partial Run---------------------#'])
        return fetch_arr