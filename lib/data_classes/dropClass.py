from scipy.signal import find_peaks
import numpy as np
from scipy.integrate import cumulative_trapezoid
import pandas as pd
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import datetime

from lib.data_classes.exceptions import zeroLenError
from lib.signal_processing.signal_function import moving_average
from lib.general_functions.helper_functions import convert_accel_units, convert_time_units, convert_mass_units, convert_length_units
from lib.general_functions.global_constants import GRAVITY_CONST, ALLOWED_TIP_TYPES_LIST
from lib.mechanics_functions.bearing_capacity_funcs import calc_dyn_bearing_capacity, calc_qs_bearing_capacity
from lib.pffp_functions.cone_area_funcs import calc_pffp_contact_area
from lib.general_functions.arrayIO import check_arr_zero_length

# TODO: In the future add a bearing capacity class to store all of the information about a bearing capacity calculation
# TODO: make a pffp class that store all of the information about the pffp

class Drop:
    """
    Stores information about a PFFP drop, including peak information, processing status,
    indices, and other relevant properties.
    ...
    """

    def __init__(self, containing_file, peak_index, file_drop_index, peak_info, pressure_check = False):
        """
        Initializes the drop and sets the intial values

        Attributes
        ----------

        containing_file : str
            The file in which the drop is located.
        peak_index : int
            Index of the peak within the containing file.
        file_drop_index : int
            The index of the drop within the file.
        peak_info : dict
            Information related to the peak of the drop.
        pressure_check : bool, optional
            Whether the drop undergoes a pressure check (default is False).
        water_drop : bool or None
        Indicates if the drop is a water drop.
        """
        # Store the inputs
        self.containing_file   = containing_file   # Store which file the drop is in 
        self.file_drop_index   = file_drop_index   # Tracks which drop this is in the file e.g. the first drop when there are 5 in the folder
        self.peak_info         = peak_info         # Store some information on the peak
        self.peak_index = peak_index
        self.water_drop = None                    # Store if the drop is a water drop
        self.processed = False                    # Tracks if the drop was processed (ie. all the information to resolve it's start and end was collected)
        self.manually_processed = False           # Tracks if the drop was processed manually
        self.indices_found = False                # Tracks if the indices were all found
        self.only_impulse  = False                # Use impulse integration (old method of integrating the function)
        
        # Init dict to hold the bearing dfs
        self.bearing_dfs = {
            "projected": None,
            "mantle": None
        }

        #TODO: In the future store the projected and mantle dfs in a dict then just reference them using the area type
        # Init dict to hold the unit properties
        self.units = {
                      "mass": "kg",
                      "Time": None,
                      "displacement":None,
                      "velocity": None, 
                      "accel": None
        }

        # init Dict to hold drop indices
        self.drop_indices = {
                "release_index"      : None,
                "start_impulse_index": None,
                "end_impulse_index"  : None
            }
        self.ref_velocities = {}                 # Init dict to hold the reference velocities for qsbc calculations for output to meta data
        
        # Init 
        # Init dict to hold pffp config information
        self.pffp_config = {
                            "tip_type": None,
                            "tip_props": None,
                            "tip_col_name": None
            }
        
    def __str__(self):
        """
        Returns a formatted string containing detailed information about the drop.

        The string includes the containing file, file drop index, whether the drop is a water drop, 
        drop indices, and the processing status of the drop.

        Returns
        -------

        str
            A string providing information about the drop, including:

            - Containing file
            - File drop index
            - Water drop status
            - Drop indices (e.g., release index, impulse indices)
            - Whether the drop has been processed
            - Whether the drop has been manually processed
        """

        # Purpose: Outputs information about the drops
        return f"----- Drop Info ----- \nContaining file: {self.containing_file} \nFile Drop Index: {self.file_drop_index} \nWater Drop: {self.water_drop}\
            \nDrop indices: {self.drop_indices} \nProcessed: {self.processed} \nManually Processed: {self.manually_processed}"
    
    @staticmethod
    def make_qDyn_name(area_type):
        # TODO: Generalize this function in the future
        """Make the qDyn column name"""
        return "qDyn_{}".format(area_type)
    
    def get_drop_datetime(self, file):
        """
        Calculate and set the datetime of the drop based on the file's datetime and the time of impact.

        This method uses the start impulse index of the drop to calculate the time difference (`delta_t`) from the start of the file 
        and adds this time difference to the file's datetime to determine the drop's datetime. The time unit is taken into account 
        when computing the datetime.

        Parameters
        ----------

        file : object
            The file object containing the `datetime` attribute, which represents the start time of the file.

        Raises
        ------

        ValueError
            If the time unit stored in `self.units["Time"]` is not supported (only "s" for seconds and "min" for minutes are implemented).z
            impulse_index = self.drop_indices["start_impulse_index"]
        """
        impulse_index = self.drop_indices["start_impulse_index"]

        # Get the delta_t from the start of the file
        delta_t = self.time[impulse_index]
        
        units = self.units["Time"]
        match units:
            case "s":
                self.datetime = file.datetime + datetime.timedelta(seconds=delta_t)
            case "min":
                self.datetime = file.datetime + datetime.timedelta(minutes=delta_t)
            case _:
                raise ValueError("Only min and s time implemented")
            
    def make_drop_name(self):
        """
        Generate a unique name (ID) for the drop based on the containing file's name and the drop's index.

        This method creates the drop's name by removing the `.bin` extension from the containing file's name and appending the drop's index within the file. The resulting name is stored in the `self.name` attribute.

        Returns
        -------

        None
            This method modifies the `self.name` attribute in place.

        Notes
        -----

        The generated name follows the format:
        
        .. code-block:: text

            <file_name>_index_<file_drop_index>

        where:
            - `<file_name>` is the name of the file without the `.bin` extension.
            - `<file_drop_index>` is the index of the drop within the file.

        Example
        -------
        If the containing file is `sample_drop_data.bin` and the drop's index is `3`, the resulting drop name will be:

        >>> drop.make_drop_name()
        >>> print(drop.name)
        sample_drop_data_index_3
        """

        # Remove .bin
        file_name = self.containing_file.replace(".bin", "")
        self.name = "{}_index_{}".format(file_name, self.file_drop_index)

    def get_peak_impulse_deceleration(self):
        """
        Calculate and store the peak impulse deceleration for the drop.

        This method determines the maximum deceleration (negative acceleration) from the `impulse_df` DataFrame, converts it to a
          standard unit (meters per second squared, "m/s^2"), and stores the value in the `self.peak_deceleration` attribute.

        Returns
        -------

        None
            This method modifies the `self.peak_deceleration` attribute in place.

        Notes
        -----

        The deceleration is calculated from the "accel" column of `self.impulse_df`, which contains the acceleration data. The peak 
        deceleration is then converted to the standard unit of "m/s^2" using the `convert_accel_units` function, ensuring consistent units.

        Example
        -------

        After calling the method, the peak deceleration will be available as an attribute:

        >>> drop.get_peak_impulse_deceleration()
        >>> print(drop.peak_deceleration)
        -9.81  # (example value, in m/s^2)
        """

        peak = self.impulse_df["accel"].max()

        # Force it to be in the standard unit just in case
        peak = convert_accel_units(peak, self.units["accel"], "m/s^2")
        
        self.peak_deceleration = peak 

    def find_release(self, accel, accel_offset = 1, height_tol=0.6, lower_accel_bound = 0.95, upper_accel_bound = 1.15):
        """
        Identify the release point of the drop from acceleration data.

        This method determines the release point of the drop by first flipping the acceleration data to find peaks where the acceleration approaches free fall. It then finds the closest peak to the drop's main peak and locates the index in the original acceleration data where the acceleration is within the specified bounds.

        Parameters
        ----------

        accel : numpy.ndarray
            Array of acceleration values.
        accel_offset : float, optional
            Offset to be subtracted from the acceleration data before flipping. Default is 1.
        height_tol : float, optional
            Threshold height for detecting peaks in the flipped acceleration data. Default is 0.6.
        lower_accel_bound : float, optional
            Lower bound for the acceleration to be considered close to 1. Default is 0.95.
        upper_accel_bound : float, optional
            Upper bound for the acceleration to be considered close to 1. Default is 1.15.

        Returns
        -------

        int
            The index of the release point in the acceleration data.

        Raises
        ------

        ValueError
            If no valid peak or release point is found that meets the criteria.

        Notes
        -----

        - The acceleration data is first flipped to find peaks where the data is closest to free fall conditions.
        - Peaks are identified that occur before the main drop peak.
        - The release point is determined based on the acceleration values being close to 1 within the specified bounds.

        Example
        -------

        Given an array of acceleration values and the parameters, this method returns the index of the release point:

        >>> accel = np.array([0.5, 0.6, 1.2, 1.1, 0.9, 1.0, 1.3])
        >>> drop.find_release(accel)
        5
        """
        # Flip the accel data so the point closest to free fall becomes a peak
        flip_accel = -1 * (accel - accel_offset)
        
        # Find the peaks of the flipped data
        index, _ = find_peaks(flip_accel, height = height_tol)

        # Get the peak free fall indices before the actual peak of the drop
        smaller_indices = np.where(index<self.peak_index)[0]
        
        check_arr_zero_length(smaller_indices, {"message":"Point meeting criteria not found", "criteria":"peak before impulse (release point)", \
                                                     "source":f"drop id: {self.file_drop_index} in {self.containing_file}"})

        # Get the closest "free fall index" before the peak of the drop
        closest_index = self.peak_index - np.min(self.peak_index - index[smaller_indices])
        
        # Find where the original data is close to 1
        release_index = np.where((accel[:closest_index] >lower_accel_bound) & (accel[:closest_index] < upper_accel_bound))[0]

        # Catch if there isn't a release
        check_arr_zero_length(release_index, {"message":"Point meeting criteria not found", "criteria":"release point", \
                                                    "source":f"drop id: {self.file_drop_index} in {self.containing_file}"})

        #Otherwise Store the release index
        return release_index[-1]

    def get_impulse_start(self, accel, time, time_tol = 0.005, sample_frq = 120_000, gradient_tol = 400, accel_lim = [5.8, 25],
                          window_size = 100, debug = False):
        """
        Determine the start of the impulse based on acceleration data.

        This method identifies the start of the impulse by analyzing the gradient of the smoothed acceleration data within a 
        specified time window. It adjusts the gradient tolerance based on the maximum acceleration value and performs additional 
        smoothing to improve accuracy.

        Parameters
        ----------

        accel : numpy.ndarray
            Array of acceleration values.
        time : numpy.ndarray
            Array of time values corresponding to the acceleration data.
        time_tol : float, optional
            Time tolerance (in seconds) used to search for the start of the impulse before the peak. Default is 0.005.
        sample_frq : int, optional
            Sampling frequency of the data in 1/min. Default is 120,000.
        gradient_tol : float, optional
            Initial gradient tolerance for detecting the impulse start. Default is 400.
        accel_lim : list of float, optional
            List of two floats specifying the lower and upper bounds for acceleration limits used to adjust gradient tolerance. Default is [5.8, 25].
        window_size : int, optional
            Window size for smoothing the acceleration and time data. Default is 100.
        debug : bool, optional
            If True, enables debugging output and plots. Default is False.

        Returns
        -------

        int
            The index of the start of the impulse in the original acceleration data.

        Raises
        ------

        ValueError
            If no valid start point for the impulse is found that meets the criteria.

        Notes
        -----

        - The method first adjusts the gradient tolerance based on the maximum acceleration value.
        - It then smooths the acceleration and time data using a moving average and calculates the jerk (the rate of change of acceleration).
        - The method identifies the start of the impulse as the point where the jerk exceeds the gradient tolerance.
        - If the `debug` parameter is set to True, additional information and plots are displayed.

        Example
        -------

        Given acceleration and time arrays, this method returns the index of the impulse start:

        >>> accel = np.array([0.1, 0.2, 1.0, 2.0, 3.0, 2.5, 2.0, 1.0, 0.5])
        >>> time = np.arange(len(accel)) / 120_000
        >>> drop.get_impulse_start(accel, time)
        2
        """
        # Purpose: Get the start of the impulse

        # Using the gradient of the acceleration to find the location of impact
        # Search time tolerance minutes before the impact for the start of the impulse
        
        # Make sure that the start index doesn't go below zero
        start_index = max(self.peak_index - int(time_tol * sample_frq), 0)

        if debug:
            store_time = time
            store_accel = accel
            # print(self.containing_file)
            # print("accel", accel)
            # print("time", time)
            # plt.plot(time, accel)

        # Only search from the time tolerance to the peak
        # time = np.array(time[start_index:self.peak_index])
        # accel = np.array(accel[start_index:self.peak_index])

        time = time[start_index:self.peak_index]
        accel = accel[start_index:self.peak_index]

        max_val = accel.max()

        # In the case of really high accelerations the smoothig done below bleads over and a higher gradient tolerance is needed
        if max_val > accel_lim[0] and max_val < accel_lim[1]:
            window_size = 7
            scale =  250 #1000
            gradient_tol = accel.max() * scale

        elif max_val >= accel_lim[1]: # Conditions for higher accelerations
            window_size = 7
            scale =  1000
            gradient_tol = accel.max() * scale 

        # Window average the acceleration and the time
        smoothed_time= moving_average(time, window_size)
        smoothed_accel = moving_average(accel, window_size)

        jerk = np.gradient(smoothed_accel, smoothed_time)

        if debug:
            plt.plot(smoothed_time, smoothed_accel, label = "smoothed")
            plt.plot(time, accel, label = "original")
            plt.legend()
            plt.show()

        # Get the points where the gradient meets this criteria
        smoothed_index =  np.where(jerk>gradient_tol)[0]
        check_arr_zero_length(smoothed_index, {"message":"Point meeting criteria not found", "criteria":"start impulse point", \
                                                    "source":f"drop id: {self.file_drop_index} in {self.containing_file}"})
        smoothed_index = smoothed_index[0]
        # Convert the index of the smoothed data back to the index of the original data

        # Selecting the last index where time is less than the selected smooth time
        index = np.where(time < smoothed_time[smoothed_index])[0][-1]
        # accel_cutoff_index = np.where()

        # Offset the index for the initial arr cut
        index = index + start_index 

        if debug:
            print("start accel value", accel[index])

            # fig, axs = plt.subplots(ncols = 1, nrows = 2)
            # print(index)
            # axs[0].plot(time, accel)
            # axs[0].scatter(time[index-start_index], accel[index-start_index], s=10, color = "red")
            # axs[1].plot(smoothed_time, jerk)
            # plt.show()

        # Return the first index that meets that criteria
        return index

    def get_impulse_end(self, accel, high_tol=1.05):
        """
        Determine the end point of the impulse based on acceleration data.

        This method identifies the end of the impulse by finding the point where the acceleration data falls below a specified
        high tolerance after the peak. It ensures that the criteria for detecting the end of the impulse are 
        met and returns the index of the end point.

        Parameters
        ----------

        accel : numpy.ndarray
            Array of acceleration values.
        high_tol : float, optional
            Upper bound tolerance for acceleration values to be considered near the end of the impulse. Default is 1.05.

        Returns
        -------

        int
            The index of the end of the impulse in the original acceleration data.

        Raises
        ------

        ValueError
            If no valid end point for the impulse is found that meets the criteria.

        Notes
        -----

        - The method searches for acceleration values that fall below the specified high tolerance after the peak.
        - It returns the index of the end point by considering the second occurrence of acceleration values below the high tolerance.
        """

        index = np.where(accel[self.peak_index:] < high_tol)[0]

        check_arr_zero_length(index, {"message":"Point meeting criteria not found", "criteria":"peak at impulse end", \
                                                     "source":f"drop id: {self.file_drop_index} in {self.containing_file}"})
        # Choose the second point
        point_index = 1

        return self.peak_index + index[point_index]
    
    def cut_accel_data(self, accel, time, input_units = {"accel":"g", "Time":"min"}):
        """
        Store and process sensor data for the selected drop region.

        This method updates the units of acceleration and time, converts time units to seconds, and extracts relevant segments of acceleration data for the selected drop. It also calculates and stores indices for the release, start, and end of the impulse. If the release point cannot be found, it raises an error.

        Parameters
        ----------

        accel : numpy.ndarray
            Array of acceleration values.
        time : numpy.ndarray
            Array of time values.
        input_units : dict, optional
            Dictionary specifying the units for acceleration and time. Default is {"accel": "g", "Time": "min"}.
            - "accel": Unit of acceleration, e.g., "g" (gravity).
            - "Time": Unit of time, e.g., "min" (minutes).

        Notes
        -----

        - The method performs the following steps:
            1. Updates the units of acceleration and time.
            2. Converts the time units to seconds.
            3. Computes the indices for the start and end of the impulse.
            4. Attempts to find the release index; raises an error if not found.
            5. Stores the indices and calculated data for further processing.
        - The time units are converted to seconds regardless of the input unit.
        - If the release index cannot be found due to proximity to the start of the file, an error is caught and re-raised after processing the available indices.

        Raises
        ------

        zeroLenError
            If the release index cannot be found and causes an error during processing.

        Example
        -------

        Given acceleration and time data, this method processes and stores the data for the selected drop region:

        >>> accel = np.array([0.1, 0.2, 9.8, 9.7, 9.6])
        >>> time = np.array([0, 1, 2, 3, 4])
        >>> drop.cut_accel_data(accel, time, {"accel": "g", "Time": "min"})
        """

        # Store the units of the acceleration and time
        self.units.update(input_units)

        # Store the time in the drop
        self.time = convert_time_units(time, input_unit = self.units["Time"], output_unit = "s")

        # Change the time units
        self.units["Time"] = "s"

        if not self.manually_processed:
            # Get the end of the impulse
            end_drop_index = self.get_impulse_end(accel, high_tol = 1.05)

            # Get the start of the impulse
            start_drop_index = self.get_impulse_start(accel, time)

            # Get the release index of the impulse
            # This often fails becasue drops are too close the beginning of the file, so try it 
            try: 
                release_index = self.find_release(accel, accel_offset =1, height_tol = 0.6, lower_accel_bound=0.95, upper_accel_bound=1.15)
            
            # If it fails due to not being found, catch the error the other indices then raise the error again
            except zeroLenError as err:
                release_index = None

                # df's store using the original indices. ie. the times and accelerations have the same indices as they had in the full arrays
                # Store the indices for later use (Stored in sequential order)
                self.drop_indices["release_index"] = release_index
                self.drop_indices["start_impulse_index"] = start_drop_index
                self.drop_indices["end_impulse_index"] = end_drop_index

                print("Release not found ")
                raise err
            
            # In the case finding thee results doesn't fail set the points
            self.drop_indices["release_index"] = release_index
            self.drop_indices["start_impulse_index"] = start_drop_index
            self.drop_indices["end_impulse_index"] = end_drop_index

        # Store the time that's been calculted in seconds
        time = self.time

        # Track that the indices were found
        self.indices_found = True

        # Make and store the relase df
        self.make_release_df(accel, time)

        # Make and store the impulse df
        self.make_impulse_df(accel, time)

    def make_impulse_df(self, accel, time):
        """
        Create and store a DataFrame for the impulse segment of the drop.

        This method extracts the segment of acceleration and time data corresponding to the impulse of the drop, based on the previously determined indices. It then creates a DataFrame with this data and stores it as an instance attribute.

        Parameters
        ----------

        accel : numpy.ndarray
            Array of acceleration values.
        time : numpy.ndarray
            Array of time values.

        Notes
        -----

        - The impulse segment is defined between the indices of the start and end of the impulse, which are stored in `self.drop_indices`.
        - The resulting DataFrame, `self.impulse_df`, contains two columns:
            - "Time": Time values for the impulse segment.
            - "accel": Acceleration values for the impulse segment.
        """

        # Store the impulse either way
        impulse_accel = accel[self.drop_indices["start_impulse_index"]:self.drop_indices["end_impulse_index"]]
        impulse_time  = time[self.drop_indices["start_impulse_index"]:self.drop_indices["end_impulse_index"]]
        
        # Store the impulse time and acceleration
        self.impulse_df = pd.DataFrame(data = {
            "Time": impulse_time,
            "accel": impulse_accel
        })

    def make_release_df(self, accel, time):
        """
        Create and store a DataFrame for the release segment of the drop.

        This method extracts the segment of acceleration and time data corresponding to the release of the drop, from the release point until the end of the impulse. It then creates a DataFrame with this data and stores it as an instance attribute.

        Parameters
        ----------

        accel : numpy.ndarray
            Array of acceleration values.
        time : numpy.ndarray
            Array of time values.

        Notes
        -----

        - The release segment is defined between the release index and the end impulse index, which are stored in `self.drop_indices`.
        - The resulting DataFrame, `self.release_df`, contains two columns:
            - "Time": Time values for the release segment.
            - "accel": Acceleration values for the release segment.
        """

        # Store from the release point until the end of the drop
        whole_drop_accel= accel[self.drop_indices["release_index"]:self.drop_indices["end_impulse_index"]]
        whole_drop_time =  time[self.drop_indices["release_index"]:self.drop_indices["end_impulse_index"]]

        # Store the drop from the release to the end
        self.release_df = pd.DataFrame(data = {
            "Time": whole_drop_time,
            "accel": whole_drop_accel
        })

    def integrate_accel_data(self):
        """
        Integrate acceleration data for the drop, from the release point to the end of the impulse.

        This method performs integration on the acceleration data to compute velocity and displacement from the release point to the end of the impulse. It also handles the case where only impulse integration is required.

        The method updates the `impulse_df` DataFrame with the calculated velocity and displacement, adjusts units, and marks the drop as processed.

        Notes
        -----

        - If `self.only_impulse` is `True`, only the impulse integration is performed using the `impulse_integration()` method.
        - If `self.only_impulse` is `False`, the method first performs release integration using the `release_integration()` method. It then extracts and adjusts the impulse data from the `release_df` DataFrame:
            - Velocity values are flipped in sign.
            - Displacement values are flipped in sign and adjusted to start at zero.
        - The units for acceleration, velocity, and displacement are updated to "m/s^2", "m/s", and "m", respectively.
        - The `processed` attribute is set to `True` upon completion.
        """

        if self.only_impulse:
            # Likely was a manaually selected drop only do the impulse integration
            self.impulse_integration()
        else:
            # Integrate the release
            self.release_integration()

            # Then get the impulse data from that
            col_names = ["accel", "velocity", "displacement"]
            
            # TODO: here is the problem something is going wrong with this slicing. Check this tomorrow
            # Just select the part of the release df that is needed
            self.impulse_df[col_names] = self.release_df[col_names].loc[self.drop_indices["start_impulse_index"]:self.drop_indices["end_impulse_index"]]

            # Flip the sign of velocity column
            self.impulse_df[col_names[1]] = -1 * self.impulse_df[col_names[1]]
            
            # Flip the sign of displacement column and make it zero at the start
            self.impulse_df[col_names[2]] = -1 * (self.impulse_df[col_names[2]] - self.impulse_df[col_names[2]].iloc[0])

        # Update the units
        self.units["accel"] = "m/s^2"
        self.units["velocity"] = "m/s"
        self.units["displacement"] = "m" 

        self.processed = True

    def release_integration(self):
        """
        Perform integration of acceleration data for the release phase.

        This method integrates acceleration data to compute velocity and displacement for the release phase of the drop. 
        It updates the `release_df` DataFrame with the integrated velocity and displacement values.

        The method follows these steps:
        1. Converts the acceleration units to "m/s^2".
        2. Applies an offset to the acceleration to account for gravitational effects.
        3. Computes velocity and displacement using cumulative integration.
        4. Updates the `release_df` DataFrame with the processed acceleration, velocity, and displacement values.

        Notes
        -----

        - The acceleration data is adjusted by subtracting the gravitational constant (`GRAVITY_CONST`) to account for gravity.
        - Velocity and displacement are calculated using the cumulative trapezoid rule applied to the acceleration and velocity data, respectively.
        - Ensure that `self.release_df` contains valid data before calling this method.
        """

        # Temp storage for the df
        df = self.release_df.copy()
            
        # Convert the acceleration units
        df["accel"] = convert_accel_units(val = df["accel"], input_unit = self.units["accel"], output_unit = "m/s^2")

        # Apply the offset
        df["accel"] = df["accel"] - GRAVITY_CONST

        # Calc the velocity and the displacement
        # Cummulative integration takes "y" then "x" -> cummulative_trapezoid(y, x)
        velocity = cumulative_trapezoid(df["accel"], df["Time"], initial = 0.0)

        displacement = cumulative_trapezoid(velocity, df["Time"], initial = 0.0)
        
        # Update the accel columns and add the new velocity and displacement columns
        self.release_df["accel"] = df["accel"]
        self.release_df["velocity"] = velocity
        self.release_df["displacement"] = displacement

    def impulse_integration(self, init_velocity = 0.0):
        """
        Integrate acceleration data for the impulse phase.

        This method performs integration on the acceleration data specifically for the impulse phase of the drop. It updates the `impulse_df` DataFrame with computed velocity and displacement values. The method accounts for initial velocity and gravitational effects.

        Parameters
        ----------

        init_velocity : float, optional
            The initial velocity to use for integration. Default is 0.0. If `self.impulse_integration` is `True`, the release DataFrame is not used to calculate the initial velocity.

        Notes
        -----

        - The acceleration data is adjusted by subtracting the gravitational constant (`GRAVITY_CONST`) to account for gravity.
        - The velocity is computed by cumulative integration of the adjusted acceleration and then inverted because the probe is decelerating. The maximum value of the computed velocity is subtracted from the velocity to reflect the impact velocity at the beginning.
        - Displacement is computed by integrating the velocity data.
        - The method assumes that the `impulse_df` DataFrame already contains the relevant data for the impulse phase.
        """

        # Temp storage for the df
        df = self.impulse_df.copy()       

        # Convert the units to m/s^2
        df["accel"] = convert_accel_units(val = df["accel"], input_unit = self.units["accel"], output_unit = "m/s^2")

        df["accel"] = df["accel"] - GRAVITY_CONST
        
        
        # Cummulative integration takes "y" then "x" -> cummulative_trapezoid(y, x)
        velocity = cumulative_trapezoid(df["accel"], df["Time"], initial = 0) + init_velocity

        # Flip the velocity because the probe is deaccelerting and you need the impact velocity at the beginning 
        velocity = velocity.max() - velocity

        # Need to cutoff the first time index
        displacement = cumulative_trapezoid(velocity, df["Time"], initial = 0.0)
        
        # Store the calculated values
        self.impulse_df["accel"]        = df["accel"] 
        self.impulse_df["velocity"]     = velocity
        self.impulse_df["displacement"] = displacement
    
    def calc_drop_qs_bearing(self, area_type, strain_rate_correc_type = "log", k_factor = 0.1, ref_velocity = 0.02, bearing_name = None, 
                             use_k_name = True, other_name = ""):
        """
        Calculate the quasi-static bearing capacity (qsbc) for the drop and store it in the selected bearing DataFrame.

        This method computes the quasi-static bearing capacity using a given k-factor or a user-defined name. The result is stored in the appropriate DataFrame within `bearing_dfs` with a unique column name. The function supports strain rate correction and allows customization of the column name.

        Parameters
        ----------

        area_type : str
            The type of bearing area to use. Determines which DataFrame in `bearing_dfs` to store the result.
        strain_rate_correc_type : str, optional
            The type of strain rate correction to apply. Default is "log". Options may include different types of strain rate corrections.
        k_factor : float, optional
            The k-factor to use for the calculation. Default is 0.1. This value is used to make the column name unique if `use_k_name` is `True`.
        ref_velocity : float, optional
            The reference velocity for the calculation. Default is 0.02 m/s. Stored for later use in metadata.
        bearing_name : str, optional
            An optional name to use for the bearing. If not provided, a default name is generated.
        use_k_name : bool, optional
            Whether to append the k-factor to the column name for uniqueness. Default is `True`. If `False`, the column name is set to `other_name`.
        other_name : str, optional
            An alternative name to use for the column if `use_k_name` is `False`. Default is an empty string.

        Notes
        -----

        - The quasi-static bearing capacity is calculated using the `calc_qs_bearing_capacity` function.
        - The `bearing_dfs` dictionary should be properly initialized with DataFrames for different `area_type` values.
        - Ensure that `impulse_df` contains velocity data and `bearing_dfs` has the necessary dynamic bearing data for the specified `area_type`.
        """

        velocity = self.impulse_df["velocity"]
        bearing_name = self.make_qDyn_name(area_type)
        
        dynamic_bearing = self.bearing_dfs[area_type][bearing_name]
            
        quasi_static_bearing = calc_qs_bearing_capacity(velocity=velocity, strainrateCorrectionType=strain_rate_correc_type,
                                                        qDyn = dynamic_bearing, k_factor=k_factor, ref_velocity= ref_velocity)
        
        # Construct the name 
        if use_k_name:
            # Construct the column name appending the k factor to make it unique 
            col_name = "qsbc_{}_{}".format(area_type[:4], k_factor)
        else:
            col_name = "qsbc_" + str(other_name)
        
        # Store the reference velocity for later output to metadata and reference velocity should be store for each calculation
        self.ref_velocities[col_name] = ref_velocity

        # Store the column in the df
        self.bearing_dfs[area_type][col_name] = quasi_static_bearing
    
    def calc_drop_dynamic_bearing(self, area_type, gravity = GRAVITY_CONST, rho_water = 1020, rho_air = 1.293, drag_coeff = 1.0):
        """
        Calculate the dynamic bearing capacity (qsbc) for the drop and store it in the selected bearing DataFrame.

        This method computes the dynamic bearing capacity based on various parameters related to the drop and the environment. The result is stored in the appropriate DataFrame within `bearing_dfs`, identified by a unique column name.

        Parameters
        ----------

        area_type : str
            The type of area calculation to use, such as "mantle" or "projected". Determines which DataFrame in `bearing_dfs` to store the result.
        gravity : float, optional
            The gravitational constant to use in the calculations. Default is `GRAVITY_CONST`.
        rho_water : float, optional
            The density of water in kg/m³. Default is 1020 kg/m³.
        rho_air : float, optional
            The density of air in kg/m³. Default is 1.293 kg/m³.
        drag_coeff : float, optional
            The drag coefficient of the probe. Default is 1.0.

        Raises
        ------

        ValueError
            If `self.water_drop` is not set, indicating whether the drop is in water or not.

        Notes
        -----

        - The `bearing_dfs` dictionary should be properly initialized with DataFrames for different `area_type` values.
        - The `pffp_config` should contain the necessary properties for calculating dynamic bearing capacity.
        - Ensure that the `impulse_df` DataFrame contains acceleration and velocity data.
        """

        # Temp store the necessary parameters
        accel = self.impulse_df["accel"]
        velocity = self.impulse_df["velocity"]
        pffp_props = self.pffp_config["tip_props"]
        tip_val_col = self.pffp_config["tip_col_name"]

        mass = pffp_props.loc[pffp_props["Properties"] == "pffp_mass"][tip_val_col].iloc[0]
        volume = pffp_props.loc[pffp_props["Properties"] == "pffp_volume"][tip_val_col].iloc[0]
        
        # Using tha base radius as the frontal area for the drag force calc
        pffp_frontal_area = pffp_props.loc[pffp_props["Properties"] == "base_radius"][tip_val_col].iloc[0]

        contact_area_col_name = "{}_{}".format("contact_area", area_type)
        bearing_col_name = self.make_qDyn_name(area_type)

        # Check that the water drop value is set
        if not isinstance(self.water_drop, bool):
            raise ValueError("To calculate the dynamic bearing capacity the flag for deciding if the drop is in water or not must be set\n \
                             The possible Values are True (for water drop) and False (for not a water drop)")
        
        contact_area = self.bearing_dfs[area_type][contact_area_col_name]
        
        qDyn = calc_dyn_bearing_capacity(pffp_accel = accel, pffp_velocity = velocity, pffp_mass = mass, 
                                         pffp_frontal_area = pffp_frontal_area, soil_contact_area = contact_area,
                                         pffp_volume = volume, water_drop = self.water_drop, drag_coeff = drag_coeff, 
                                         gravity = gravity, rho_water = rho_water, rho_air = rho_air)
        
        # Store the dynamic bearing capcity result
        self.bearing_dfs[area_type][bearing_col_name] = qDyn
        
    def get_pffp_tip_values(self, pffp_id, tip_type, date_string, file_dir):
        """
        Read and store the tip values for a given probe.

        This method reads the tip values from an Excel file based on the provided `pffp_id`, `tip_type`, and `date_string`. It checks if the `tip_type` is allowed, retrieves the relevant sheet from the file, and stores the tip values in the configuration dictionary.

        Parameters
        ----------

        pffp_id : str
            The identifier for the probe. Used to determine the specific sheet in the Excel file to read from.
        tip_type : str
            The type of tip values to retrieve. Must be one of the allowed types specified in `ALLOWED_TIP_TYPES_LIST`.
        date_string : str
            The date string to construct the column name for the tip values.
        file_dir : str
            The directory or path to the Excel file containing the tip values.

        Raises
        ------

        ValueError
            If the `tip_type` is not in the list of allowed tip types (`ALLOWED_TIP_TYPES_LIST`).

        Notes
        -----

        - The method assumes that the Excel file contains a sheet named according to the format `bluedrop_<pffp_id>`.
        - The Excel sheet must contain columns labeled `"Properties"`, `"units"`, and a column named according to the constructed `col_name`.
        - The `pffp_config` dictionary is updated with the tip type, column name, and a DataFrame containing the tip properties.
        """

        # Check that the tip type is allowed
        if not tip_type in ALLOWED_TIP_TYPES_LIST:
            raise ValueError("Tip type of {} is not allowed".format(tip_type))
        
        sheet_name = "bluedrop_{}".format(pffp_id)
        self.pffp_config["tip_type"] = tip_type

        tip_table = pd.read_excel(file_dir, sheet_name)

        # Construct the column name
        col_name = "{}_{}".format(tip_type, date_string)
        
        # Store the name of the column that the values live in
        self.pffp_config["tip_col_name"] = col_name

        self.pffp_config["tip_props"] = tip_table[["Properties", "units", col_name]]

    def convert_tip_vals(self):
        """
        Convert the units of the tip properties to the units used in the analysis.

        This method updates the units of the tip properties in the `pffp_config` dictionary to match the units used in the analysis. Specifically, it converts mass and length units to the units specified in the `self.units` dictionary.

        The method performs the following steps:
        - Retrieves and converts the mass value from the tip properties.
        - Updates the units of mass in the DataFrame.
        - Identifies the properties that require length unit conversion based on the tip type.
        - Converts and updates the length values and their units in the DataFrame.

        Raises
        ------

        KeyError
            If required keys are missing from `self.pffp_config` or `self.units`.

        Notes
        -----

        - The `convert_mass_units` and `convert_length_units` functions are used to perform the unit conversions.
        - The tip properties DataFrame (`self.pffp_config["tip_props"]`) must include columns for properties, units, and the tip values.
        """

        # Store the names of the columns need for relabelling
        val_col_name = self.pffp_config["tip_col_name"]
        properties_col_name = "Properties"

        # Temp storage of the df
        df = self.pffp_config["tip_props"]

        # Get the mass row and the row index
        row = df.loc[df[properties_col_name] == "pffp_mass"]
        row_index = df.index[df['Properties'] == "pffp_mass"].tolist()

        # Store the value
        mass_val = row[val_col_name]

        # Store the unit
        mass_unit = row["units"].iloc[0]

        # Convert the unit and store the value back in the df
        # df[val_col_name][row_index] = convert_mass_units(mass_val, mass_unit, self.units["mass"])
        
        df.loc[row_index, val_col_name] = convert_mass_units(mass_val, mass_unit, self.units["mass"])

        df.loc[row_index, "units"] = self.units["mass"]
        
        # List of props that may need to have there units converted
        match self.pffp_config["tip_type"]:
            case "parabola":
                lengths_need_conversion = ["tip_height", "base_radius"]  
            case "blunt":
                lengths_need_conversion = ["tip_height", "base_radius"]  
            case "cone":
                lengths_need_conversion = ["tip_height", "base_radius", "tip_radius"]

        # Loop over the lengths that need to be converted
        for label in lengths_need_conversion:
             row = df.loc[df[properties_col_name] == label]
             row_index = df.index[df['Properties'] == label].tolist()
     
             # Store the value (using iloc so val isn't a series)
             val = row[val_col_name].iloc[0]
        
             # Store the unit
             length_unit = row["units"].iloc[0]
     
             # Convert the unit and store the value back in the df
             self.pffp_config["tip_props"].loc[row_index, val_col_name] = convert_length_units(val, length_unit, self.units["displacement"])
     
             self.pffp_config["tip_props"].loc[row_index, "units"] = self.units["displacement"]
            
    def calc_drop_contact_area(self, area_type):
        """
        Calculate the contact area for bearing capacity calculations based on the specified area type.

        This method computes the contact area for the drop based on the type of area calculation (either 'projected' or 'mantle') and stores the result in the appropriate DataFrame.

        Parameters
        ----------

        area_type : str
            The type of area calculation to perform. Must be one of the following:
            - "projected"
            - "mantle"

        Raises
        ------

        ValueError
            If `area_type` is not one of the allowed values ("projected" or "mantle").
        
        Notes
        -----

        - The method initializes the DataFrame for the specified `area_type` if it is not already present.
        - The contact area is calculated using the `calc_pffp_contact_area` function, which takes into account the displacement, tip type, and tip properties.
        - The resulting contact area is stored in a DataFrame with a column name formatted as `"contact_area_{area_type}"`.
        """

        if not area_type in ["projected", "mantle"]:
            # Raise an error if an erroneuos input
            raise ValueError("Area type {} is not implemented".format(area_type))

        if self.bearing_dfs[area_type] is None:
            # Init the df
            self.bearing_dfs[area_type] = pd.DataFrame()
        
        # Temp storage of the df
        tip_props = self.pffp_config["tip_props"]
        
        # Add cases here so that the correct values can be passed 
        # Unpack some values
        displacement = self.impulse_df["displacement"]
        tip_type = self.pffp_config["tip_type"]

        # Calc the contact area
        contact_area = calc_pffp_contact_area(penetrationDepth=displacement, areaCalcType= area_type, tipType= tip_type, tipProps= tip_props, 
                                              tip_val_col= self.pffp_config["tip_col_name"])
        # make the contact area column name
        col_name = "{}_{}".format("contact_area", area_type)

        # Add the data to the df
        self.bearing_dfs[area_type][col_name] = contact_area
    
    # Plotting functions
    def quick_view_impulse(self, interactive = True, figsize= [12, 8], legend = False):
        """
        Provide a quick view of impulse data through visualizations.

        This method generates a plot of impulse data, displaying acceleration, velocity, and displacement over time. It offers two visualization options: interactive plots using Plotly or static plots using Matplotlib.

        Parameters
        ----------
        
        interactive : bool, optional
            If True, generates interactive plots using Plotly. If False, generates static plots using Matplotlib. Default is True.
        figsize : list of int, optional
            Specifies the dimensions of the figure. The list should contain two values: width and height. Default is [12, 8].
        legend : bool, optional
            If True, adds legends to the plots. Default is False.

        Notes
        -----

        - The method uses the units specified in `self.units` for labeling the axes.
        - For interactive plots, the method uses Plotly's `make_subplots` to create a multi-row subplot for acceleration, velocity, and displacement.
        - For static plots, the method uses Matplotlib to generate a three-row subplot.
        - The figure's title includes the file drop index from `self.file_drop_index`.
        
        """
 
        # Temp df storage
        df = self.impulse_df
        time = df["Time"]
        accel = df["accel"]
        vel = df["velocity"]
        displacement = df["displacement"]

        accel_units = self.units["accel"]
        vel_units = self.units["velocity"]
        disp_units = self.units["displacement"]
        time_units=  self.units["Time"]

        if interactive:
            fig = make_subplots(rows = 3, cols = 1, shared_xaxes = True)

            fig.add_trace(
                go.Scatter(x = time, y= accel, mode = "lines", name = "Acceleration"),
                row = 1, col = 1
            )

            fig.add_trace(
                go.Scatter(x= time, y= vel, mode = "lines", name = "Velocity"),
                row = 2, col = 1
            )

            fig.add_trace(
                go.Scatter(x = time, y = displacement, mode = "lines", name = "Displacement"),
                row = 3, col = 1
            )
            
            # Update xaxis properties
            fig.update_xaxes(title_text="Time (s)", row=3, col=1)



            # Update yaxis properties
            fig.update_yaxes(title_text=f"Acceleration ({accel_units})", row=1, col=1)
            fig.update_yaxes(title_text=f"Velocity ({vel_units})", row=2, col=1)
            fig.update_yaxes(title_text=f"Displacement ({disp_units})", row=3, col=1)

            # Update figure title
            fig.update_layout(height = figsize[1] *100, width = figsize[0] *100,
                            title_text=f"File Drop index: {self.file_drop_index}")

            # Turn off interactivity
            fig.show()
        else:
            # Use matplotlib
            fig, axs = plt.subplots(ncols = 1, nrows = 3, figsize = (figsize[0], figsize[1]))

            axs[0].plot(time, accel, label = f"acceleration {accel_units}")
            axs[1].plot(time, vel, label = f"velocity {vel_units}")
            axs[2].plot(time, displacement, label = f"Displacement {disp_units}")

            
            # Turn on the legends
            if legend:
                axs[0].legend()
                axs[1].legend()
                axs[2].legend()

            # Label the y-axis
            axs[0].set_ylabel(f"Acceleration [{accel_units}]")
            axs[1].set_ylabel(f"Velocity [{vel_units}]")
            axs[2].set_ylabel(f"Displacement [{disp_units}]")

            # Label the x-axis
            axs[0].set_xlabel(f"Time [{time_units}]")
            axs[1].set_xlabel(f"Time [{time_units}]")
            axs[2].set_xlabel(f"Time [{time_units}]")
            print(time_units)

            # Give the entire figure a label
            fig.suptitle(f"File drop index: {self.file_drop_index}")

            plt.tight_layout()

            plt.show()
            
    def quick_view_release(self, interactive = True, figsize = [12, 8], legend = False):
        """
        Provide a quick view of the full release data through visualizations.

        This method generates a plot of the release data, displaying acceleration, velocity, and displacement over time. It offers two visualization options: interactive plots using Plotly or static plots using Matplotlib.

        Parameters
        ----------

        interactive : bool, optional
            If True, generates interactive plots using Plotly. If False, generates static plots using Matplotlib. Default is True.
        figsize : list of int, optional
            Specifies the dimensions of the figure. The list should contain two values: width and height. Default is [12, 8].
        legend : bool, optional
            If True, adds legends to the plots. Default is False.

        Notes
        -----

        - The method uses the units specified in `self.units` for labeling the axes.
        - For interactive plots, the method uses Plotly's `make_subplots` to create a multi-row subplot for acceleration, velocity, and displacement.
        - For static plots, the method uses Matplotlib to generate a three-row subplot.
        - The figure's title includes the file drop index from `self.file_drop_index`.
        """

        # Temp df storage
        df = self.release_df
        time = df["Time"]
        accel = df["accel"]
        vel = df["velocity"]
        displacement = df["displacement"]

        accel_units = self.units["accel"]
        vel_units = self.units["velocity"]
        disp_units = self.units["displacement"]
        time_units=  self.units["Time"]

        if interactive:
            fig = make_subplots(rows = 3, cols = 1, shared_xaxes = True)

            fig.add_trace(
                go.Scatter(x = time, y= accel, mode = "lines", name = "Acceleration"),
                row = 1, col = 1
            )

            fig.add_trace(
                go.Scatter(x= time, y= vel, mode = "lines", name = "Velocity"),
                row = 2, col = 1
            )

            fig.add_trace(
                go.Scatter(x = time, y = displacement, mode = "lines", name = "Displacement"),
                row = 3, col = 1
            )
            
            # Update xaxis properties
            fig.update_xaxes(title_text="Time (s)", row=3, col=1)



            # Update yaxis properties
            fig.update_yaxes(title_text=f"Acceleration ({accel_units})", row=1, col=1)
            fig.update_yaxes(title_text=f"Velocity ({vel_units})", row=2, col=1)
            fig.update_yaxes(title_text=f"Displacement ({disp_units})", row=3, col=1)

            # Update figure title
            fig.update_layout(height = figsize[1] *100, width = figsize[0] *100,
                            title_text=f"File Drop index: {self.file_drop_index}")

            # Turn off interactivity
            fig.show()
        else:
            # Use matplotlib
            fig, axs = plt.subplots(ncols = 1, nrows = 3, figsize = (figsize[0], figsize[1]))

            axs[0].plot(time, accel, label = f"acceleration {accel_units}")
            axs[1].plot(time, vel, label = f"velocity {vel_units}")
            axs[2].plot(time, displacement, label = f"Displacement {disp_units}")

            
            # Turn on the legends
            if legend:
                axs[0].legend()
                axs[1].legend()
                axs[2].legend()

            # Label the y-axis
            axs[0].set_ylabel(f"Acceleration [{accel_units}]")
            axs[1].set_ylabel(f"Velocity [{vel_units}]")
            axs[2].set_ylabel(f"Displacement [{disp_units}]")

            # Label the x-axis
            axs[0].set_xlabel(f"Time [{time_units}]")
            axs[1].set_xlabel(f"Time [{time_units}]")
            axs[2].set_xlabel(f"Time [{time_units}]")

            # Give the entire figure a label
            fig.suptitle(f"File drop index: {self.file_drop_index}")

            plt.tight_layout()
            plt.show()

    def quick_view_impulse_selection(self, offset = 20, legend = True, draw_line = True, line_val = 0):
        """
        Provide a quick view of the impulse selection data, comparing release data with impulse data.

        This method plots a segment of the release data alongside the impulse data, allowing for visual comparison. It includes options 
        to adjust the plot appearance, such as drawing a horizontal line and displaying a legend.

        Parameters
        ----------

        offset : int, optional
            The number of data points to include before the start of the impulse data. Default is 20.
        legend : bool, optional
            If True, displays a legend on the plot. Default is True.
        draw_line : bool, optional
            If True, draws a horizontal line at the specified `line_val`. Default is True.
        line_val : float, optional
            The y-value at which to draw the horizontal line, if `draw_line` is True. Default is 0.

        Notes
        -----

        - The method uses data from `self.release_df` and `self.impulse_df`.
        - The `start` and `end` indices for the plot are determined based on the impulse start and end indices from `self.drop_indices`,
          adjusted by the `offset`.
        - The plot uses Matplotlib to show the release data as a line plot and the impulse data as a scatter plot.
        """
        
        start = self.drop_indices["start_impulse_index"] - offset
        end = self.drop_indices["end_impulse_index"]

        plt.plot(self.release_df["Time"].loc[start:end], self.release_df["accel"].loc[start:end], color = "blue", label= "release")
        plt.scatter(self.impulse_df["Time"], self.impulse_df["accel"], color = "red", label = "impulse")

        time_units = self.units["Time"]
        accel_units = self.units["accel"]

        plt.xlabel(f" Time ({time_units}) ")
        plt.ylabel(f"Acceleration ({accel_units})")

        if draw_line:
            plt.axhline(y = line_val)
        if legend:
            plt.legend()
        
        plt.show()

    # Outputting functions
    def output_impulse_data(self, folder_dir = "", file_name = None, index = False):
        """
        
        Output impulse data to a CSV file.

        This method exports the impulse data to a CSV file. The file is named based on the drop index and containing file, unless a custom file 
        name is provided.

        Parameters
        ----------

        folder_dir : str, optional
            The directory where the CSV file will be saved. If not provided, the file will be saved in the current directory. Default is an empty string.
        file_name : str, optional
            The name of the file to which the data will be saved. If not provided, a default name based on the drop index and containing file is used. 
            If provided, custom naming is not currently supported and will raise an exception. Default is None.
        index : bool, optional
            If True, includes the DataFrame index in the CSV file. If False, does not include the index. Default is False.

        Raises
        ------

        ValueError
            If a custom file name is provided, an exception is raised as custom naming is not supported.

        Notes
        -----

        - The file name is constructed using the `folder_dir`, `self.file_drop_index`, and the base name of `self.containing_file` (with the ".bin" extension removed).
        - The method uses Pandas' `to_csv` function to write the DataFrame to a CSV file.

        """

        # If no file name was inputted
        if file_name is None:
            containing_file = self.containing_file.replace(".bin", "")

            # Get the output name and folder
            name = "{}/impulse_drop_id_{}_{}.csv".format(folder_dir, self.file_drop_index, containing_file)
        else:
            raise ValueError("Inputting an alternate name for this file is not implemented at this time")

        # Temp storage of the df
        df = self.impulse_df

        df.to_csv(name, index = index)

    def output_release_data(self, folder_dir = "", file_name = None, index = False):
        """
        Output release data to a CSV file.

        This method exports the release data to a CSV file. The file is named based on the drop index and containing file, unless a custom file name is provided.

        Parameters
        ----------

        folder_dir : str, optional
            The directory where the CSV file will be saved. If not provided, the file will be saved in the current directory. Default is an empty string.
        file_name : str, optional
            The name of the file to which the data will be saved. If not provided, a default name based on the drop index and containing file is used. If provided, custom naming is not currently supported and will raise an exception. Default is None.
        index : bool, optional
            If True, includes the DataFrame index in the CSV file. If False, does not include the index. Default is False.

        Raises
        ------

        ValueError
            If a custom file name is provided, an exception is raised as custom naming is not supported.

        Notes
        -----

        - The file name is constructed using the `folder_dir`, `self.file_drop_index`, and the base name of `self.containing_file` (with the ".bin" extension removed).
        - The method uses Pandas' `to_csv` function to write the DataFrame to a CSV file.
        """

        # TODO: Add a condition here that if the release data doesn't exist a warning is printed to the screen

        # If no file name was inputted
        if file_name is None:
            containing_file = self.containing_file.replace(".bin", "")

            # Get the output name and folder
            name = "{}/release_drop_id_{}_{}.csv".format(folder_dir, self.file_drop_index, containing_file)
        else:
            raise ValueError("Inputting an alternate name for this file is not implemented at this time")

        # Temp storage of the df
        df = self.release_df

        df.to_csv(name, index = index)

    def output_bearing_data(self, df, folder_dir = "", file_name = None, index = False):
        """
        Output bearing capacity data to a CSV file.

        This method exports bearing capacity data to a CSV file. The file is named based on the drop index and containing file, unless a custom file name is provided.

        Parameters
        ----------

        df : pandas.DataFrame
            The DataFrame containing the bearing capacity data to be exported.
        folder_dir : str, optional
            The directory where the CSV file will be saved. If not provided, the file will be saved in the current directory. Default is an empty string.
        file_name : str, optional
            The name of the file to which the data will be saved. If not provided, a default name based on the drop index and containing file is used. If provided, custom naming is not currently supported and will raise an exception. Default is None.
        index : bool, optional
            If True, includes the DataFrame index in the CSV file. If False, does not include the index. Default is False.

        Raises
        ------

        ValueError
            If a custom file name is provided, an exception is raised as custom naming is not supported.

        Notes
        -----
        
        - The file name is constructed using the `folder_dir`, `self.file_drop_index`, and the base name of `self.containing_file` (with the ".bin" extension removed).
        - The method uses Pandas' `to_csv` function to write the DataFrame to a CSV file.
        """

        # If no file name was inputted
        if file_name is None:
            containing_file = self.containing_file.replace(".bin", "")

            # Get the output name and folder
            name = "{}/bearing_drop_id_{}_{}.csv".format(folder_dir, self.file_drop_index, containing_file)
        else:
            raise ValueError("Inputting an alternate name for this file is not implemented at this time")

        # Store the passed df
        df.to_csv(name, index = index)

if __name__ == "__main__":
    # Add some testing here
    pass