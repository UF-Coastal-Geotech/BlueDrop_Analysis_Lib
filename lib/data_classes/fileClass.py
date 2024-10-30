import datetime  # Import the datetime module
import os  # Import the os module for operating system functions

class File:
    """
    Define a class that holds general file properties.

    This class represents a file by storing its directory and provides basic functionality to manage file-related properties.

    Attributes
    ----------
    
    file_dir : str
        The directory of the file.
    file_name : str
        The name of the file. Initialized to an empty string.
    datetime : datetime.datetime
        The date and time the file was last modified, initialized in :meth:`get_file_datetime`.

    Methods
    -------

    __init__(file_dir)
        Initialize a File object with the provided file directory.
    get_file_datetime()
        Get the date and time the file was last modified (assumed to be the drop date).
    get_file_name()
        Extract and store the file name from the directory path.
    new_file_name(new_name)
        Update the file name and rename the physical file on the file system.
        
    """
    def __init__(self, file_dir):
        """
        Initialize a File object with the file directory.

        Parameters
        ----------
        file_dir : str
            The directory of the file to be associated with this File object.
        """
        self.file_dir = file_dir  # Store the file directory
        
        # Initialize variable to store the file name
        self.file_name = ""

    def get_file_datetime(self):
        """
        Get the date and time the file was last modified (assumed to be the drop date).

        This method updates the `datetime` attribute with the last modification time of the file.
        
        """
        modification_time = os.path.getmtime(self.file_dir)  # Get file modification time
        
        # Convert modification time to datetime object and store it
        self.datetime = datetime.datetime.fromtimestamp(modification_time)
    
    def get_file_name(self):
        """
        Extract and store the file name from the directory path.

        This method updates the `file_name` attribute with the base name of the file.
        """
        self.file_name = os.path.basename(self.file_dir)  # Get file name from directory path

    def new_file_name(self, new_name):
        """
        Update the file name and physically rename the file on the file system.

        Parameters
        ----------
        new_name : str
            The new name for the file.

        Raises
        ------
        FileNotFoundError
            If the original file does not exist.
        OSError
            If renaming the file fails.
        """
        # Store the old file name and directory
        old_name = self.file_name
        old_dir = self.file_dir

        # Update the file directory with the new file name
        self.file_dir = self.file_dir.replace(old_name, new_name)

        # Update the stored file name
        self.file_name = new_name

        # Actually rename the physical file
        os.rename(old_dir, self.file_dir)


if __name__ == "__main__":
    # Add some testing here
    pass
