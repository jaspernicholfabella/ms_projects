"""zenscraper.utils.data module"""

class Data:
    """Data Class for manipulating data sets like list string and dataframe"""
    logger = None

    def __init__(self, logger):
        self.logger = logger

    @staticmethod
    def split_list(alist, wanted_parts=1):
        """
        split list into several parts
        :param alist: list of values
        :param wanted_parts: how parts should the list have
        :return: list of lists
        """
        chunk_size = wanted_parts
        chunked_list = [alist[i:i + chunk_size] for i in range(0, len(alist), chunk_size)]
        return chunked_list

    @staticmethod
    def df_delete_col_except(dataframe, list_of_col, exception_list=None):
        """
        :param dataframe: dataframe to modify
        :param list_of_col: list of all column to remove
        :param exception_list: list of all exceptions
        :return:
        """
        temp_df = dataframe
        if exception_list is None:
            exception_list = []

        for col in list_of_col:
            if any(x == str(col) for x in exception_list):
                pass
            else:
                try:
                    temp_df.drop(str(col), inplace=True, axis=1)
                except Exception:  # pylint: disable=broad-except
                    pass

        return temp_df

    @staticmethod
    def df_col_pop(dataframe, col_name, is_int=False):
        """
        pop column(header) to the top of all column
        :param df: dataframe
        :param col_name: column to pop on top of all column
        :param is_int: is the value of the column int?
        :return:
        """
        cols = list(dataframe)
        cols.insert(0, cols.pop(cols.index(col_name)))
        # us ix to reorder (loc for str or boolean, iloc for int)
        if not is_int:
            dataframe = dataframe.loc[:, cols]
            return dataframe
        dataframe = dataframe.iloc[:, cols]
        return dataframe

    @staticmethod
    def df_sort_row(dataframe, col_name):
        """
        sort dataframe row based on column name
        :param dataframe: dataframe to sort
        :param col_name: column name to sort every value with
        :return: return dataframe with sorted value
        """
        return dataframe.sort_values(by=col_name, key=lambda col: col.str.lower())
