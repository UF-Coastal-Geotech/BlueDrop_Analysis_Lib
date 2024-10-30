# Make this into a class that handles the IO of arrays
from lib.data_classes.exceptions import zeroLenError


def check_arr_zero_length(arr, err_message):
    """
    Check if an array has a length of zero and raise an error if it does.

    This function verifies whether the provided array is empty (i.e., its length is zero).
    If the array is empty, it raises a `zeroLenError` with a specified error message.

    Parameters:
        arr (list, numpy.ndarray, or similar): The array or sequence to be checked.
        err_message (str): The error message to be included in the `zeroLenError` exception if the array is empty.

    Raises:
        zeroLenError: If the length of `arr` is zero, an exception is raised with the provided error message.
    """

    if len(arr) ==0:
        raise zeroLenError(err_message)