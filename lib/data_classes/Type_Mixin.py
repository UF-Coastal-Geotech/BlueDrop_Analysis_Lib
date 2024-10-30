import numpy as np
import pandas as pd

class TypeMixin:
    """
    A mixin class providing various static methods for data conversion and output operations.

    Methods
    -------

    array_2_df(array, column_names)
        Convert a numpy array to a pandas DataFrame with specified column names.
    binary_arr_2_integer_arr(binary_arr, byte_order, signed_flag)
        Convert an array of binary data to an array of integers.
    arr_2_matrix(arr, num_rows, num_cols)
        Reshape a numpy array into a 2D matrix with specified number of rows and columns.
    output_df_2_excel(df, file_dir, sheet_name)
        Output a DataFrame to an Excel sheet.
    """
    @staticmethod
    def array_2_df(array, column_names):
        """
        Convert a numpy array to a pandas DataFrame with the given column names.

        Parameters
        ----------

        array : numpy.ndarray
            A numpy array to be converted into a DataFrame.
        column_names : list of str
            A list of column names for the DataFrame.

        Returns
        -------

        pandas.DataFrame
            The resulting DataFrame with the specified column names.
        """
        df = pd.DataFrame(array)  # Convert the numpy array to a DataFrame
        df.columns = column_names  # Set the column names of the DataFrame
        return df  # Return the resulting DataFrame

    @staticmethod
    def binary_arr_2_integer_arr(binary_arr, byte_order, signed_flag):
        """
        Convert an array of binary data to an array of integers.

        Parameters
        ----------

        binary_arr : list of bytes
            A list of byte sequences (binary data).
        byte_order : str
            A string indicating the byte order ('big' or 'little').
        signed_flag : bool
            A boolean indicating whether the integers are signed (True) or unsigned (False).

        Returns
        -------

        numpy.ndarray
            A numpy array of integers converted from the binary data.
        """
        # Convert each byte sequence in binary_arr to an integer using the specified byte order and signed flag
        integer_arr = [int.from_bytes(b, byteorder=byte_order, signed=signed_flag) for b in binary_arr]
    
        # Convert the list of integers to a numpy array and return it
        return np.array(integer_arr)
    
    @staticmethod
    def arr_2_matrix(arr, num_rows, num_cols):
        """
        Reshape a numpy array into a matrix (2D array) with the specified number of rows and columns.

        Parameters
        ----------

        arr : numpy.ndarray
            A numpy array to be reshaped.
        num_rows : int
            The number of rows for the resulting matrix.
        num_cols : int
            The number of columns for the resulting matrix.

        Returns
        -------

        numpy.ndarray
            The reshaped matrix (2D array).
        """
        # Reshape the numpy array into a matrix with the specified dimensions and return it
        return np.reshape(arr, (num_rows, num_cols))
    
    @staticmethod
    def output_df_2_excel(df, file_dir, sheet_name):
        """
        Output a DataFrame to an Excel sheet.

        Parameters
        ----------
        
        df : pandas.DataFrame
            The DataFrame to be written to an Excel file.
        file_dir : str
            The file path of the Excel file to write to.
        sheet_name : str
            The name of the sheet where the data should be written.

        Notes
        -----

        Error handling should be added to ensure the file can be written correctly.
        """
        # TODO: Add error handling to ensure the file can be written correctly
        # Write the DataFrame to the specified Excel file and sheet
        df.to_excel(file_dir, sheet_name)

if __name__ == "__main__":
    # Add some testing here
    pass