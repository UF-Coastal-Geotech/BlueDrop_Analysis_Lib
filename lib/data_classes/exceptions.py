# Exception in case no point is found for some test
class zeroLenError(Exception):
    """
    Exception raised for errors related to zero-length data or input.

    This custom exception is used to indicate that an operation or function
    encountered data or input of zero length, which is not permissible for
    the operation to proceed correctly.

    Attributes:
        message (str): Explanation of the error.
    """
    pass

if __name__ == "__main__":
    # Add some testing here
    pass