import numpy as np
from scipy.signal import find_peaks

def find_drops(accel_data, impact_time_tol = 0.015, sample_freq = 120_000, min_peak_height = 2.8):
    """
    Detects the number of drops in the acceleration data by identifying peaks.

    Parameters
    ----------

    accel_data : np.ndarray
        Array of acceleration data.
    impact_time_tol : float, optional
        The assumed minimum time between drops, in seconds. Default is 0.015.
    sample_freq : int, optional
        Number of samples collected per minute. Default is 120,000.
    min_peak_height : float, optional
        Minimum acceleration measurement to be considered a drop, measured in g's. Default is 2.8.

    Returns
    -------

    tuple
        A tuple containing:
        - drop_indexs (np.ndarray): Indices of detected drops in the acceleration data.
        - drop_info (dict): Information about the detected drops, including peak heights.
        - num_drops (int): The number of detected drops.

    Notes
    -----

    The function uses the `find_peaks` method from `scipy.signal` to identify peaks in the acceleration data.
    The impact window is calculated based on the `impact_time_tol` and `sample_freq`.
    """
        
    # Calc assumed tolerance for the length of impact
    impact_window = impact_time_tol * sample_freq

    drop_indexs, drop_info = find_peaks(accel_data, height = min_peak_height, distance = impact_window)
        
    num_drops = len(drop_indexs)

    return drop_indexs, drop_info, num_drops

def check_peaks_in_data(accel_data, height_range = 2.8):
    """
    Checks if there are peaks in the acceleration data based on the specified height range.

    Parameters
    ----------

    accel_data : np.ndarray
        Array of acceleration data.
    height_range : float or list, optional
        Can be a single value representing the minimum peak height, or a list with two values representing the minimum and maximum peak heights. Default is 2.8.

    Returns
    -------

    list
        A list containing:
        - A boolean indicating if peaks were found.
        - If peaks were found, a list of peak indices and a dictionary with peak information.

    Notes
    -----

    The function uses the `find_peaks` method from `scipy.signal` to identify peaks based on the `height_range`.
    """
    peaks_indices, peak_dict_info = find_peaks(accel_data, height = height_range)
    
    if len(peaks_indices) > 0:
        # Check if there are peaks in the data, if yes return the data about the peaks
        return [True, peaks_indices, peak_dict_info]
    else:
        # If no peaks return false and don't return anymore information
        return [False]
    
# Function to do a moving average
def moving_average(data, window_size):
    """
    Calculates the moving average of the data using a specified window size.

    Parameters
    ----------
    
    data : array-like
        The array for which the moving average is to be calculated.
    window_size : int
        The width of the window in indices of the array.

    Returns
    -------

    np.ndarray
        The moving average of the input data.

    Notes
    -----

    The function uses cumulative sums to compute the moving average efficiently.
    """

    # Convert the data to np array
    data = np.array(data)
    
    averaged_data = np.cumsum(data)
    averaged_data[window_size:] = averaged_data[window_size:] - averaged_data[:-window_size]
    return averaged_data[window_size-1:]/window_size

def find_deriv_change(x, y, cutoff, greater = True):
    """
    Finds the locations where the derivative of the data reaches a specified threshold.

    Parameters
    ----------

    x : np.ndarray
        Array of independent data.
    y : np.ndarray
        Array of dependent data.
    cutoff : float
        The threshold value for the derivative.
    greater : bool, optional
        If True, finds locations where the derivative is greater than the cutoff. If False, finds locations where the derivative is less 
        than the cutoff. Default is True.

    Returns
    -------

    tuple
        Indices where the derivative meets the specified condition.

    Notes
    -----

    The function calculates the derivative of the data using `np.gradient`, which employs second-order central differencing for the i
    nterior and first-order differencing for the boundaries.
    """
    # Calc the derivative
    derivative = np.gradient(y, x)
    
    if greater:
        # Find where the value of the derivative is greater than the cutoff
        criteria_indices = np.nonzero(derivative > cutoff)
    else:
        # Find where the value of the derivative is less than the cutoff
        criteria_indices = np.nonzero(derivative < cutoff)

    return criteria_indices