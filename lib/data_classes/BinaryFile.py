import pandas as pd
import numpy as np

from lib.data_classes.fileClass import File
from lib.data_classes.Type_Mixin import TypeMixin


# Binary file class inherits the File class and the TypeMixin
class BinaryFile(File, TypeMixin):
    """
    Represents a binary file and provides functionality to read and convert the binary data into a Pandas DataFrame.

    Parameters
    ----------
    
    file_dir : str
        The directory of the binary file.
    """

    def __init__(self, file_dir):
        """
        Initializes the BinaryFile object.

        Parameters
        ----------

        file_dir : str
            The directory of the binary file.
        """

        File.__init__(self, file_dir) # inherit parent methods and store file dir
    
    # method to print info about the binary file
    def __str__(self):
        """
        Returns a string representation of the BinaryFile object.

        Returns
        -------

        str
            String containing the file directory.
        """
        return f"File Directory: {self.file_dir}"
    
    def read_binary(self, size_byte = 3):
        """
        Reads a binary file and stores the data in a list.

        Parameters
        ----------

        size_byte : int, optional
            Number of bytes to read at a time. Defaults to 3, which is typical for PFFP binary files.

        Returns
        -------

        list of bytes
            List containing chunks of binary data read from the file.
        
        Notes
        -----

        This method reads the binary data chunk by chunk, based on the specified byte size, until the end of the file is reached.
        """
        #TODO: maybe convert the binary right away. You have to unwrap the data again the way it is right now
        
        # Init the arr
        binary_arr = []

        with open(self.file_dir, 'rb') as file:
            while True:
                data_chunk = file.read(size_byte)
                if not data_chunk:
                    break  # break the loop if there is no more data
                binary_arr.append(data_chunk)

        return binary_arr

    def binary_file_2_df(self, column_names, num_columns, num_rows = -1, size_byte = 3, byte_order = "big", signed = True):
        """
        Reads a binary file, converts it to integers, and stores the data in a Pandas DataFrame.

        Parameters
        ----------

        column_names : list of str
            Names of the columns in the resulting DataFrame.
        num_columns : int
            Number of columns in the DataFrame.
        num_rows : int, optional
            Number of rows in the DataFrame. Defaults to -1, which infers the number of rows based on the data size.
        size_byte : int, optional
            Number of bytes to read at once for each value. Defaults to 3.
        byte_order : str, optional
            Byte order for reading binary data ('big' or 'little'). Defaults to 'big'.
        signed : bool, optional
            Whether the integers are signed or unsigned. Defaults to True.

        Returns
        -------

        pd.DataFrame
            DataFrame containing the binary data converted to integers.
        
        Notes
        -----

        The binary data is read and then converted into integers, which are arranged in a matrix format. 
        The resulting matrix is used to create a Pandas DataFrame.

        The byte order indicates the order in which the bytes are stored in memory. For PFFP binary files, the typical order is 'big'.
        """

        # Read the binary file
        binary_arr = self.read_binary(size_byte)
        
        # Convert the binary to an integer arr
        integer_arr = BinaryFile.binary_arr_2_integer_arr(binary_arr, byte_order, signed)

        # Reformat the arr
        integer_matrix = BinaryFile.arr_2_matrix(integer_arr, num_rows, num_columns)

        # return the df
        return pd.DataFrame(integer_matrix, columns = column_names)

if __name__ == "__main__":
    # Add some testing here
    pass

