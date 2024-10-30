# import datetime
import numpy as np
from lib.data_classes.BinaryFile import BinaryFile
from lib.signal_processing.signal_function import find_drops, moving_average
from lib.data_classes.dropClass import Drop # Class that is used to represent drops
from lib.general_functions.helper_functions import convert_accel_units, convert_time_units, convert_length_units
from lib.data_classes.exceptions import zeroLenError

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from operator import itemgetter
import time

class pffpFile(BinaryFile):
    """
    Purpose: To store information and modify a PFFP binary file.

    Inherits
    --------

    BinaryFile
        A base class for handling binary file operations.

    Attributes
    ----------

    calibration_params : DataFrame
        Parameters for converting sensor readings from volts to engineering units.
    sensor_units : dict, optional
        Units used for different sensors. Defaults to {"accel": "g", "pressure": "kPa", "Time": "min"}.
    num_drops : str
        Number of drops in the file. Defaults to "Not Checked".
    df_stored : bool
        Flag indicating whether the DataFrame has been stored.
    stored_concat_accel : bool
        Flag indicating whether concatenated acceleration data has been stored.
    """
        
    # TODO: Add a time zone category and add that data to the datetime
    def __init__(self, file_dir, calibration_params, sensor_units = {"accel":"g", "pressure":"kPa", "Time":"min"}):
        """
        Initialize the pffpFile instance.

        Parameters
        ----------

        file_dir : str
            The directory of the binary file.
        calibration_params : DataFrame
            Calibration parameters for converting sensor readings.
        sensor_units : dict, optional
            Units used for different sensors. Defaults to {"accel": "g", "pressure": "kPa", "Time": "min"}.
        """
        BinaryFile.__init__(self, file_dir)

        # Store the calibration params fro converting from volts to engineering units
        self.calibration_params = calibration_params
        
        # Get the file name
        self.get_file_name()

        # Get the file drop date
        self.get_file_datetime()

        # Init variables for later storage
        self.num_drops = "Not Checked" 
        
        self.df_stored = False
        self.stored_concat_accel = False
        self.sensor_units = sensor_units

    def __str__(self):
        """
        Return a string representation of the pffpFile instance.

        Returns
        -------

        str
            A formatted string with information about the file, number of drops, and other attributes.
        """
        return f"File Directory: {self.file_dir} \nNum Drops in file: {self.num_drops} \
                \nDrop Date: {self.datetime.date()} \nDrop Time: {self.datetime.time()} \
                \ndf stored: {self.df_stored}\
                \nConcat accel stored: {self.stored_concat_accel}"
        
    @staticmethod
    def get_tightest_sensor(row, resolutions, labels):
        """
        Determine the sensor with the closest resolution to the maximum value in the row.

        Parameters
        ----------

        row : Series
            The data row containing sensor values.
        resolutions : list of float
            List of possible sensor resolutions.
        labels : list of str
            List of sensor labels corresponding to the resolutions.

        Returns
        -------

        float
            The value from the row that corresponds to the closest resolution.
        """
         
        value = row.max()

        # Filter out resolutions smaller than the value
        valid_resolutions = [res for res in resolutions if res >= value]

        # If all resolutions are greater than the value, use the smallest resolution
        if not valid_resolutions:
            closest_resolution = min(resolutions)
        else:
            closest_resolution = min(valid_resolutions, key=lambda x: abs(x - value))
        
        # Get the index of the closest resolution
        index = resolutions.index(closest_resolution)

        # Get the column the closest data is in
        col = labels[index] 
            
        return row[col]
    
    def new_pffp_file_name(self, survey_id, num_char_from_end = 8, use_default = True, other_name = None):
        """
        Update the name of the pffp file.

        Parameters
        ----------

        survey_id : str
            The survey identifier to include in the new file name.
        num_char_from_end : int, optional
            Number of characters to keep from the end of the current file name. Defaults to 8.
        use_default : bool, optional
            Whether to use the default naming format. Defaults to True.
        other_name : str, optional
            A custom name to use instead of the default format. Not implemented yet.

        Raises
        ------

        ValueError
            If `use_default` is False and `other_name` is None.
        """

        # TODO: Need to make sure this works
        # If the default
        if use_default:
            # Get the base name which is the hex number and the file extension
            base_name = self.file_name[-num_char_from_end:]

            new_pffp_name = "{}_{}".format(survey_id, base_name)
            
            # Rename the file and update the properties of the file class to track that info
            self.new_file_name(new_name=new_pffp_name)
        
        # In case a name other than the default format is wanted
        elif not other_name is None:
            raise ValueError("Using a name other than the default is not implemented at this time")

        # Rename the containing file name for the drops
        for drop in self.drops:
            drop.containing_file = self.file_name

    def binary_2_sensor_df(self, size_byte = 3, byte_order = "big", signed = True, acceleration_unit = "g", pressure_unit = "kPa", time_unit = "min"):
        """
        Read a binary file and transform it into a Dataframe that has the sensor values converted to engineering units of interest.

        Parameters
        ----------

        size_byte : int, optional
            The size of each data element in bytes. Defaults to 3.
        byte_order : str, optional
            The byte order of the binary file. Defaults to "big".
        signed : bool, optional
            Whether the data is signed. Defaults to True.
        acceleration_unit : str, optional
            The unit to convert acceleration values to. Defaults to "g".
        pressure_unit : str, optional
            The unit to convert pressure values to. Defaults to "kPa".
        time_unit : str, optional
            The unit for time values. Defaults to "min".

        Returns
        -------

        DataFrame
            The processed DataFrame with converted sensor readings and time steps.
        """

        column_names = ["Count", 'Unknown', "2g_accel", "18g_accel", "50g_accel", "pore_pressure", "200g_accel", 
                                                                "55g_x_tilt","55g_y_tilt", "250g_accel"]
        num_columns = len(column_names)

        num_rows = -1

        df = self.binary_file_2_df(column_names, num_columns, num_rows, size_byte, byte_order, signed)

        # Apply the offset to the df
        
        # NOTE: Assumes the columns of the df are IN EXACT ORDER (names can be differnt but values must be the same):
        # [Count, Unknown, 2g_accel, 18g_accel, 50g_accel, pore_pressure, 200g_accel, 55g_x_tilt, 55g_y_tilt, 250g_accel]

        # Drop the count and unknown columns
        columns_2_drop = [0, 1]
        
        columns_header_2_drop = df.columns[columns_2_drop]
        
        # df now has values:
        # [2g_accel, 18g_accel, 50g_accel, pore_pressure, 200g_accel, 55g_x_tilt, 55g_y_tilt, 250g_accel]
        df.drop(columns_header_2_drop, axis = 1, inplace = True)

        # Local variable for the calibration factors
        params = self.calibration_params

        # Search through the senor names and get the offset and scale for that sensor
        for value in params['Sensor']:
            offset = params[params['Sensor'] == value].iloc[0, 1]
            scale = params[params['Sensor'] == value].iloc[0, 2]

            # Scale the df columns, Formula is (sensor_value + offset)/scale
            df[value] = (df[value] +offset)/scale

        # Get the number of entries in a column
        num_entries = len(df.iloc[:, 0])
        
        # Get the time steps and convert the time to minutes
        time = np.linspace(0, 1, num_entries)
        
        # Store the time in minutes in the df
        df.insert(0, "Time", time)

        # Acceleration scaling
        acceleration_sensor_names = ["2g_accel", "18g_accel", "50g_accel","200g_accel", "55g_x_tilt","55g_y_tilt", "250g_accel"]
        df[acceleration_sensor_names] = convert_accel_units(df[acceleration_sensor_names], "g", acceleration_unit)
        
        # Dictionary with conversion from psi to other sets of units
        pressure_conversion_dict = {
                                    "kPa": 6.89476
        }

        if pressure_unit == "psi":
            pass
        elif pressure_unit == "kPa":
            # Convert the pressure to kPa
            df["pore_pressure"] = df["pore_pressure"] * pressure_conversion_dict["kPa"]
        else:
            raise ValueError("Onnly converison from psi to kPa implemented")
        return df
    
    # TODO: Need to modularize this function. This thing is too big
    def analyze_file(self, use_pore_pressure = True, store_df = True, overide_water_drop = False, 
                     select_accel = ["2g_accel", "18g_accel", "50g_accel", "250g_accel"]):
        """
        Analyze the binary file to identify and process drops based on sensor data.

        Parameters
        ----------

        use_pore_pressure : bool, optional
            Whether to use pore pressure data to help identify drops. Defaults to True.
        store_df : bool, optional
            Whether to store the DataFrame in the class attribute for later use. Defaults to True.
        overide_water_drop : bool, optional
            Flag to override the default water drop detection. Defaults to False.
        select_accel : list of str, optional
            List of accelerometer labels to use for drop analysis. Defaults to ["2g_accel", "18g_accel", "50g_accel", "250g_accel"].

        Notes
        -----

        This method performs the following actions:
        - Loads and processes the binary file into a DataFrame.
        - Stitches accelerometer data together, excluding certain sensors if needed.
        - Identifies drop locations based on peak accelerations and optionally pore pressure data.
        - Creates `Drop` objects for each identified drop and stores them in the `drops` attribute.
        - Optionally stores the DataFrame if `store_df` is True.
        
        TODO:
        - Add inputs for drop detection tolerances and sampling rate.
        """
        
        # Set the flag that keeps track if the df is stored

        # TODO: Add inputs for the find drops, this will be the tolerances and the info about the sampling rate

        # Init list to store the drop objects
        self.drops = []
         
        self.funky = False

        # Load the file df - Might be able to only load the part of the files I want in the future
        # Skip some sections of the binary file and only load the sensor that I need
        # Need to convert to gravity units because that's what the find_drops is expecting
        df = self.binary_2_sensor_df(acceleration_unit = self.sensor_units["accel"], pressure_unit = self.sensor_units["pressure"], time_unit= self.sensor_units["Time"])

        # Stitch the accelerometers and store the values
        # Don't use the 200g accel it's kind of sketchy sometimes
        self.stitch_accelerometers(df, accel_labels = select_accel)

        # Init flag to track if the drop was checked using pressure sensor
        pressure_check = None

        # TODO: Need to turn this into multiple functions
        # if use_pore_pressure and np.max(df["pore_pressure"] > 1):
        # TODO: The tolerances set in this function are unit dependent. Need to set a constant for the tolerance and scale 
        # them based on the units being used for the analysis

        if use_pore_pressure and np.max(df["pore_pressure"] > 0.5):
            
            # Set the flag that says pressure check is being done
            pressure_check = True

            # Init list to store accel indices that need to be deleted
            index_2_delete = []

            # Get the max deceleration so that a guess of the selected peak height can be choosen
            max_accel = np.max(self.concat_accel)
            tol_5g = 6.0

            # Min height that's considered a drop
            min_2g = 2

            if max_accel < tol_5g:
                percentage_tol = 0.6
                min_height = max(percentage_tol * max_accel, min_2g)
            else:
                # For the drops that have a higher max acceleration use a lower proportion of max acceleration
                percentage_tol = 0.4
                min_height = max(percentage_tol * max_accel, min_2g)
                
            # Check the concanted accelerations for a drop
            peak_indexs, peak_info, num_accel_drops = find_drops(self.concat_accel, min_peak_height=min_height, impact_time_tol = 0.03)

            # Select the times where the peak acceleration thinks drops occured
            time_peak_acceleration = np.array(df["Time"])[peak_indexs]
                
            # Get where the pressure derivative thinks the drops are
            time_peak_pressure_deriv, num_pressure_drops = self.check_pore_pressure_4_drop(df, window = 2500)

            # Loop over the acceleration times and see if there's a pressure sensor time close by
            # I have more faith in the pressure sensor at detecting drops 
            for i, accel_time in enumerate(time_peak_acceleration):

                if len(time_peak_pressure_deriv) > 0:
                    time_diff = np.abs(time_peak_pressure_deriv - accel_time)
                    # print(time_peak_pressure_deriv)
                    matching_index = np.where(time_diff<0.02)[0]
                else:
                    # Catch the case where no pore pressures are returned
                    matching_index = []

                # print(matching_index)
                if len(matching_index) == 0:
                    # If there are no matching time indexs remove that value from the accleration peak_indexs
                    index_2_delete.append(i)
                    num_accel_drops -= 1

                elif len(matching_index) > 1:
                    print(f"Warning: Multiple acceleration evaluated to the same pore pressure drop predictor {self.file_name}")
                    self.funky = True

            # Delete the indices
            peak_indexs = np.delete(peak_indexs, index_2_delete)

            if num_accel_drops != num_pressure_drops:
                print("\nNum accel drops:", num_accel_drops)
                print("Num pressure drops: ", num_pressure_drops)
                print(f"Warning: Number of predicted drops should match {self.file_name}")
                self.funky = True
            
        else:
            # Pressure check isn't being used
            pressure_check = False

            # Use the concatenated accleration sensor data to fund the drops
            peak_indexs, peak_info, num_accel_drops = find_drops(self.concat_accel)

            # Select the times where the peak acceleration thinks drops occured
            time_peak_acceleration = np.array(df["Time"])[peak_indexs]

        # Init the number of drops to zero
        self.num_drops = 0

        for i, index in enumerate(peak_indexs):
            drop = Drop(containing_file= self.file_name, peak_index = index, file_drop_index= i+1, peak_info = peak_info, pressure_check = pressure_check)
            self.insert_drop(drop)

        # Check if the df should be stored
        if  store_df:
            # Remove the df reference to allow the garbage collector to free up the memory
            self.df = df

            # Set the tracker flag to false
            self.df_stored = True
    
    def insert_drop(self, drop, index = None):
        """
        Add a drop to the file object. This is useful for the automatic process and manually adding a drop
        """

        # Increment the number of drops
        self.num_drops += 1

        # If no index is set, append the drop to the end of the list
        if index is None:
            # Store the drop object in the file's list
            self.drops.append(drop)
        elif isinstance(index, int):
            # Add the drop to a specific location in the list
            # If the index is greater than the length of the list python just adds the element to the end of the list.
            # eg. if index is 100 and the length of the list is 2, the drop will be added at drop_list[2] making the length of the list 3
            self.drops.insert(index, drop)
        else:
            raise TypeError(f"The type of index is {type(index)}. The type should be None or int")
        
    def manually_add_drop(self, peak_index, file_drop_index, peak_info, pressure_check):
        """
        Function to manually add a drop to the file object. This covers all the initialization steps that are necessary to make sure the drop has all of the information it needs to work
        """

        # Check if the df is stored
        if self.df_stored:
            # Temporarily store the df
            df = self.df
        else: 
            # Load the df
            df = self.binary_2_sensor_df(acceleration_unit = self.sensor_units["accel"], pressure_unit = self.sensor_units["pressure"], time_unit= self.sensor_units["Time"])

        # Create the drop
        drop = Drop(containing_file= self.file_name, peak_index = peak_index, file_drop_index= file_drop_index, peak_info = peak_info, pressure_check = pressure_check)


        # Need to add the time data so that the manual selection works
        drop.time= df["Time"]

        # Update the drop units
        drop.units.update(self.sensor_units)

        # Make sure the drop is is set to being not processed
        drop.processed = False

        # Create the drop, increment the number of drops and add it to the list
        self.insert_drop(drop, index = file_drop_index -1)

        # Loop over the drops and make sure the drop index is set to the right order
        self.reset_drop_index()

    def reset_drop_index(self, reset_type = "normal"):
        """
        Loop over the drops and reset the file indices
        """
        allowed_reset_types = ["normal"]

        # check if the 
        if reset_type in allowed_reset_types:
            match reset_type:
                case "normal":
                    for i, drop in enumerate(self.drops):
                        drop.file_drop_index = i+1
                case _:
                    raise IndexError(f"Don't know how you made it here but the reset_type value is {reset_type}")
        else: 
            raise ValueError(f"Allowed reset types are {allowed_reset_types}")
        
    def process_drops(self):
        """
        Process the identified drops in the file by integrating acceleration data.

        Notes
        -----

        This method processes each drop by:
        - Trimming the acceleration data around the drop events.
        - Integrating the trimmed acceleration data to obtain meaningful metrics.
        - Handling any errors that occur during processing, including moving files to a "funky" folder if errors are encountered.

        Raises
        ------

        zeroLenError
            If any error occurs during the processing of drops.
        """
        # Check if the df is stored
        if self.df_stored:
            # Temporarily store the df
            df = self.df
        else: 
            # Load the df
            df = self.binary_2_sensor_df(acceleration_unit = self.sensor_units["accel"], pressure_unit = self.sensor_units["pressure"], time_unit= self.sensor_units["Time"])
        
        # display(df.head())
        # loop over the drops in the file
        accel = self.concat_accel
        time = df["Time"]

        raise_error = False
        
        for drop in self.drops:  
            skip_integration = False
            # Try to trim the acceleration data and integrate it
            # Do the try here than pass the error back up
            try:
                # Trim the acceleration data
                drop.cut_accel_data(accel, time, input_units = {"accel":"g", "Time":"min"} )

            except zeroLenError as err:
                # Print the error message
                details= err.args[0]

                # Print the error details
                print("\n" + details["message"])
                print("Criteria not met:", details["criteria"])
                print(details["source"])
                print("Moving file to funky folder")

                # set error flag but try to process other drops
                raise_error = True
                skip_integration = True

            if not skip_integration:
                # If no error caught for this drop do the integration
                drop.integrate_accel_data()

                # Set the flag 
                drop.processed = True 

        # Raise error so the file gets moved into the funky folder
        if raise_error:
            raise zeroLenError

    def manually_process_drops(self, interactive_plot = True, figsize = [6,4]):
        """
        Manually process drops by allowing the user to select drop indices and perform integration interactively.

        Parameters
        ----------

        interactive_plot : bool, optional
            Whether to use interactive plotting for manual index selection. Defaults to True.
        figsize : list of int, optional
            The size of the figures for interactive plots. Defaults to [6, 4].

        """
        # Loop over the drops in the file
        for drop in self.drops: 
            # If the drop isn't processed
            if not drop.processed:
                # Do the manual indices selction
                self.manual_indices_selection(drop, interactive = interactive_plot, figsize = figsize)

                # And do the integration
                self.manually_integrate_drop(drop)

    def manually_integrate_drop(self, drop):
        """
        Integrate acceleration data for a drop that was manually processed.

        Parameters
        ----------

        drop : Drop
            The `Drop` object representing the manually processed drop.

        Notes
        -----

        This method performs the integration of acceleration data for a drop whose indices were selected manually.
        It assumes that the indices have been found and the drop has been marked as manually processed.

        Raises
        ------

        IndexError
            If the indices for the drop are not found.
        ValueError
            If the drop is not marked as manually processed.
        """
        # Check if the df is stored
        if self.df_stored:
            # Temporarily store the df
            df = self.df
        else: 
            # Load the df
            df = self.binary_2_sensor_df(acceleration_unit = self.sensor_units["accel"], pressure_unit = self.sensor_units["pressure"], time_unit= self.sensor_units["Time"])
        
        # display(df.head())
        # loop over the drops in the file
        accel = self.concat_accel
        time = df["Time"]

        if not drop.indices_found:
            raise IndexError("Indices aren't all found yet")
        
        if not drop.manually_processed:
            raise ValueError("Only use this function for drops that had there indices manually selected")
        
        drop.cut_accel_data(accel, time, input_units = {"accel":"g", "Time":"min"} )
        drop.integrate_accel_data()

        # Set the flag 
        drop.processed = True 
        
    def check_drop_in_file(self):
        """
        Check if there are any drops detected in the file.

        Returns
        -------

        bool
            True if there are drops detected, False otherwise.
        """
        if self.num_drops > 0:
            return True
        else:
            return False

    def check_pore_pressure_4_drop(self, df, window = 2500):
        """
        Use pore pressure data to check if there are drops in the file.

        Parameters
        ----------

        df : DataFrame
            DataFrame containing sensor data with columns 'Time' and 'pore_pressure'.
        window : int, optional
            Window size for smoothing the pressure data (default is 2500).

        Returns
        -------

        tuple
            - numpy.ndarray: Array of times where pressure gradient peaks occur.
            - int: Number of drops detected based on pressure derivative.
        """
        # Store the df in a temp variable
        time = np.array(df["Time"])
        pressure = np.array(df["pore_pressure"])

        # Smooth the pressure and time - time smoothing is done so both arrays have the same num values
        smoothed_pressure = moving_average(pressure, window)
        smoothed_time = moving_average(time, window)

        # Calc the pressure derivative
        pressure_deriv = np.gradient(smoothed_pressure, smoothed_time)

        # Get the min peak height to consider for the derivative 10 * the max pressure has worked well
        # TODO: See if there's a good argument for why 10 seems to work well or if it's just chance
        max_pressure_scaling = 12
        min_height = np.max(smoothed_pressure) * max_pressure_scaling


        pressure_indexs, pressure_peak_info, num_drops = find_drops(pressure_deriv, impact_time_tol=0.08, min_peak_height=min_height )

        # Get the time that the pressure gradient peaks occur
        time_peak_pressure_deriv = smoothed_time[pressure_indexs]

        return time_peak_pressure_deriv, num_drops
    
    def stitch_accelerometers(self, accel_df, accel_labels):
        """
        Stitch accelerometer data together to get the most resolved accelerations.

        Parameters
        ----------

        accel_df : DataFrame
            DataFrame containing accelerometer data.
        accel_labels : list of str
            List of accelerometer labels to be used for stitching.

        Notes
        -----

        Assumes that the accel labels and the max sensor values are in the same order.
        """        
        res_dict = {"2g_accel":1.7, "18g_accel": 18, "50g_accel":50, "200g_accel":200, "250g_accel":250}
        
        resolutions = itemgetter(*accel_labels)(res_dict)
        df = accel_df[accel_labels]

        # NOTE: Assumes that the accel labels and the max sensor values are in the same order
        series = df.apply(self.get_tightest_sensor, axis = 1, args = (resolutions,accel_labels,))
        self.concat_accel = series
        self.stored_concat_accel = True
    
    def manual_indices_selection(self, drop, debug = False, interactive = True, figsize = [12,8], legend = False, lag = 0.1):
        """
        Manually select indices for drops. Allows users to enter time or index values.

        Parameters
        ----------

        drop : Drop
            The `Drop` object for which indices are to be manually selected.
        debug : bool, optional
            Flag to enable debugging information (default is False).
        interactive : bool, optional
            Flag to enable interactive plotting (default is True).
        figsize : list of int, optional
            Figure size for plotting (default is [12, 8]).
        legend : bool, optional
            Flag to show legend on the plot (default is False).
        lag : float, optional
            Time delay before accepting user input (default is 0.1 seconds).

        Notes
        -----

        Prompts the user to specify time, index, or skip the drop. Provides options for impulse integration and updates the drop object accordingly.
        """
        
        # TODO: Add an option so in case the detected drop isn't a real drop, but there are other real drops in the file
        
        # Print information about the drop
        print(drop)

        print("\nPlotting file data...")
        # Plot the data
        self.quick_view(interactive=interactive, figsize= figsize, legend = legend)
        
        time.sleep(lag)                            

        allowed_input_type = ["Time", "index", "skip"]
        allowed_overwrite_inputs = ["y", "n"]

        index_dict = drop.drop_indices.copy()      
        
        for key, value in index_dict.items():
            # If there is an index stored
            if not value is None:
                index_time = self.df["Time"][value]

                print("Index label: {}".format(key),
                      "\nCurrent Index value: {}".format(value),
                      "\nCurrent Time value: {}\n".format(index_time)
                      )


                # Make a string for overwriting
                overwrite_str = ("Would you like to overwrite the index?"
                                "\nEnter {} (for yes) or {} (for no).".format(allowed_overwrite_inputs[0],
                                                                                                          allowed_overwrite_inputs[1])
                                )

                # Take in the input
                overwrite_input = input(overwrite_str)

                # Check if it's the enter character. If it is escape from this analysis
                if overwrite_input == "":
                    print("Escaping from overwriting without completion")

                # Check that the 
                while not overwrite_input.lower() in allowed_overwrite_inputs:
                    print("{} is not an allowed input. Only {} or {} allowed".format(allowed_overwrite_inputs[0],
                                                                                     allowed_overwrite_inputs[1])
                         )
                    
                    # Read the input again
                    overwrite_input = input(overwrite_str)
                
                # If no need to overwrite skip the rest of the for loop
                if overwrite_input == "n":
                    print("Continuing to the next index...")
                    continue

            # Otherwise just continue
        
            print("--------- Need {} ---------".format(key))
            # Get the type of the input allow users to enter a time or a index
            input_type_string ="Enter {} or {} or {}\n".format(allowed_input_type[0],
                                                                allowed_input_type[1],
                                                                allowed_input_type[2])
            
            input_type = input(input_type_string)
            
            if input_type == "":
                print("Escaping from manual_indices_selection without completion")
                return
            
            while not input_type in allowed_input_type:
                input_type = input(input_type_string)
                print("{} is not an allowed input. Only {}, {} or {} is allowed\n".format(input_type, allowed_input_type[0], allowed_input_type[1], allowed_input_type[2]))
                if input_type == "":
                    print("Escaping from function")
                    return None
            
            if input_type == allowed_input_type[0]:
                
                # Get the limiting time by converting the max time to the file units so it matches the figure
                limit = convert_time_units(drop.time.max(), drop.units["Time"], self.sensor_units["Time"] ) 
                
                if debug:
                    print("time limit", limit)
                
                # Flag to track if the input is good
                good_input = False
                
                # Check that the val is a float
                while not good_input:
                    print("\nInput must be a decimal number and less than {}\
                        \nFunction assumes the time is in {}".format(limit, self.sensor_units["Time"]))
                    
                    # Get the string input and convert it to a float
                    try:
                        input_val = input("Enter a time:\n")
                        
                        if input_val == "":
                            print("Escaping from manual_indices_selection without completion")
                            return None
                        
                        val = float(input_val)
                    except ValueError as err:
                        print(err)
                        good_input = False
                    
                        # Go to the next iteration because input wasn't valid
                        continue
                    
                    # Check that the entered time is within bounds
                    if val >= 0 and val < limit:
                        good_input = True
                    
                # Convert the units back to the drop time units
                val = convert_time_units(val, self.sensor_units["Time"], drop.units["Time"])
                
                # Find the index that corresponds to the time closest to the input time
                index = np.where(val <= drop.time)[0][0]

            elif input_type == allowed_input_type[1]:
                index =0.0
                good_input= False
                while not good_input:
                    print("\nInput must be an integer number (no decimal points) and less than {} and greater than or equal to 0".format(0, len(drop.time)-1))
                    try:
                        # Try to convert the input to an integer
                        index = input("Enter an integer index")
                        if index == "":
                            print("Escaping from manual_indices_selection without completion")
                            return None 
                        index = int(index)
                    except ValueError as err:
                        print(err)
                        good_input = False
                        
                        continue
                    # Check that the integer is positive and inside the bounds of the arr
                    if index <=len(drop.time)-1 and index >=0:
                        good_input = True
            
            elif input_type == allowed_input_type[2]:
                # If the file can be left as move to the next drop
                continue
            
            # Checking if 
            integration_type = "None"
            integration_ans = ["y", "n"]

            while not integration_type in integration_ans:
                integration_type = input("Impulse Integration? (y or n)")
                
                if integration_type == "":
                    print("Escaping from the manual_indices_selection without completion" )
                    return
                
                if integration_type == integration_ans[0]:
                    drop.only_impulse = True
                elif integration_type == integration_ans[1]:
                    drop.only_impulse = False
                
            # set the value into the dict
            drop.drop_indices[key] = index

        drop.indices_found = True
        drop.manually_processed = True

    # Plotting functions
    def quick_view(self, fig = None, axs = None, interactive = False, figsize = [12, 8], legend = False, show = True, **kwargs):
        """
        Provide a quick view of the file data by plotting accelerometer, pore pressure, and tilt sensor data.

        Parameters
        ----------

        interactive : bool, optional
            Flag to enable interactive plotting with Plotly (default is False).
        figsize : list of int, optional
            Figure size for plotting (default is [12, 8]).
        legend : bool, optional
            Flag to show legend on the plot (default is False).

        Notes
        -----
        
        If `interactive` is True, plots are created using Plotly for interactive viewing. Otherwise, matplotlib is used for static plots.
        """
        # if the df isn't stored load it for plotting don't store it though
        if not self.df_stored:
            df = self.binary_2_sensor_df(acceleration_unit="g", pressure_unit= "kPa")
        else:
            # Otherwise use the stored df
            df = self.df

        # generate the figure object
        time = df["Time"]
        
        accel_labels = ["2g_accel", "18g_accel", "50g_accel", "200g_accel", "250g_accel"]
        tilt_labels = ["55g_x_tilt", "55g_y_tilt"]
        pressure_label = "pore_pressure"

        time_unit = self.sensor_units["Time"]
        accel_unit = self.sensor_units["accel"]
        pressure_unit = self.sensor_units["pressure"]
        
        if interactive:
            # Create the figure if no figure is passed
            if fig is None: 
                fig = make_subplots(rows = 3, cols = 1, shared_xaxes = True, **kwargs)

            # Accelerometer plots
            for label in accel_labels:
                fig.add_trace(
                    go.Scatter(x = time, y = df[label], mode = "lines", name = label),
                    row = 1, col = 1
                )

            # Pore pressure sensor
            fig.add_trace(
                go.Scatter(x = time, y = df[pressure_label], mode = "lines", name = "pore pressure"),
                row = 2, col = 1
            )
            
            # Tilt sensors
            for label in tilt_labels:
                fig.add_trace(
                    go.Scatter(x = time, y = df[label], mode = "lines", name = label),
                    row = 3, col = 1
                )

            # Update xaxis properties
            fig.update_xaxes(title_text=f"Time {time_unit}", row=3, col=1)

            # Update yaxis properties
            fig.update_yaxes(title_text="Acceleration (g)", row=1, col=1)
            fig.update_yaxes(title_text="Pressure (kPa)", row=2, col=1)
            fig.update_yaxes(title_text="Acceleration (g)", row=3, col=1)

            # Update figure title
            fig.update_layout(height = figsize[1] *100, width = figsize[0] *100,
                            title_text=f"File Name: {self.file_name}")

            # Show the plot interactivity
            if show:
                fig.show()
        else:
            if fig is None and axs is None:
                # Use matplotlib
                fig, axs = plt.subplots(ncols = 1, nrows = 3, figsize = (figsize[0], figsize[1]), **kwargs)
            elif fig is None or axs is None:
                # Raise an error if figure or axs is set to None. This means that the user set one but not the other.
                raise ValueError("Both figure and axs must be set to matplotlib objects or None")
            

            # Accelerometers
            for label in accel_labels:
                axs[0].plot(time, df[label], label = label)
            
            # Pressure sensor
            axs[1].plot(time, df[pressure_label], label = pressure_label)

            # Tilt sensors
            for label in tilt_labels:
                axs[2].plot(time, df[label], label = label)
            
            # Turn on the legends
            if legend:
                axs[0].legend()
                axs[1].legend()
                axs[2].legend()

            # Label the y-axis
            axs[0].set_ylabel(f"Acceleration [{accel_unit}]")
            axs[1].set_ylabel(f"Pressure [{pressure_unit}]")
            axs[2].set_ylabel(f"Acceleration [{accel_unit}]")

            # Label the x-axis
            axs[0].set_xlabel(f"Time [{time_unit}]")
            axs[1].set_xlabel(f"Time [{time_unit}]")
            axs[2].set_xlabel(f"Time [{time_unit}]")

            # Give the entire figure a label
            fig.suptitle(f"File Name: {self.file_name}")

            plt.tight_layout()
            
            # Flag for showing the figure. This means that the figure isn't available for saving
            if show:
                plt.show()

    def plot_drop_impulses(self, figsize = [4,6], save_figs = False, hold = False, legend = True,
                            colors = ["black", "blue", "green", "orange", "purple", "brown"],
                            units = {"Time":"s", "accel":"g", "velocity":"m/s", "displacement":"cm"},
                            line_style = ["solid", "dashed"]):        
        """
        Plot the standard velocity and acceleration versus displacement plots for all processed drops.

        Parameters
        ----------

        figsize : list of int, optional
            Size of the figure in inches (default is [4, 6]).
        save_figs : bool, optional
            Flag to save the figures (default is False).
        hold : bool, optional
            Flag to hold the figure open and plot on the same figure (default is False). If True, all drops will be plotted on the same figure.
        legend : bool, optional
            Flag to show the legend on the plot (default is True).
        colors : list of str, optional
            List of colors to use for plotting each drop (default is ["black", "blue", "green", "orange", "purple", "brown"]).
        units : dict, optional
            Dictionary specifying the units for time, acceleration, velocity, and displacement (default is {"Time": "s", "accel": "g", "velocity": "m/s", "displacement": "cm"}).
        line_style : list of str, optional
            List of line styles to use for plotting (default is ["solid", "dashed"]).

        Notes
        -----

        - If `hold` is True, all processed drops will be plotted on the same figure using the first color specified in the `colors` list.
        - Each processed drop will be plotted with acceleration and velocity versus displacement.
        - The `units` dictionary is used to convert the units of the data to match the specified units.
        - The `save_figs` flag is not implemented in this version of the method.
        - If `legend` is True, a legend will be added to the plot to differentiate between acceleration and velocity.
        """
        # TODO: Move this to the drop level and call the drop function here
        # Set all of the line colors to black if hold is on
        if not hold:
            colors = ["black"] * self.num_drops
            
        # Loop over the drops and plot them

        first_processed_drop = -1
        for i, drop in enumerate(self.drops):
            
            # If the processing for the drop is not done
            if not drop.processed:
                # Print the drop information
                print(drop, "not finished being processed")

                # Go to the next drop
                continue
            
            # Increment the tracker for plotting
            first_processed_drop+=1

            if not hold:
                # Make a new figure every time
                fig, axs = plt.subplots(nrows = 1, ncols = 1, figsize = (figsize[0], figsize[1]))
            elif hold and first_processed_drop ==0:
                fig, axs = plt.subplots(nrows = 1, ncols = 1, figsize = (figsize[0], figsize[1]))

            drop_units = drop.units

            time = drop.impulse_df["Time"]
            accel = drop.impulse_df["accel"]
            vel = drop.impulse_df["velocity"]
            disp = drop.impulse_df["displacement"]

            # Convert the units
            time = convert_time_units(time, drop_units["Time"], units["Time"])
            accel = convert_accel_units(accel, drop_units["accel"], units["accel"])
            disp = convert_length_units(disp, drop_units["displacement"], units["displacement"])

            if drop_units["velocity"] != units["velocity"]:
                raise ValueError("Conversion for velocity not implemented")
            
            axs.plot(accel, disp, color = colors[i], label= "acceleration", linestyle = line_style[0])
            axs.plot(vel, disp, color = colors[i], label = "velocity", linestyle = line_style[1])

            # label the axes
            if hold and first_processed_drop == 0 or not hold:
                accel_unit = units["accel"]
                vel_unit = units["velocity"]
                disp_unit = units["displacement"]

                axs.set_xlabel(f"Acceleration ({accel_unit})/Velocity ({vel_unit})")
                axs.set_ylabel(f"Displacement ({disp_unit})")
                
                # Label the plot only with the file name if hold is on
                if hold:
                    axs.set_title(f"File: {self.file_name} Num Drops: {self.num_drops}")
                else: 
                    axs.set_title(f"File: {self.file_name} Drop id: {drop.file_drop_index}")
                axs.invert_yaxis()

            if legend:
                axs.legend()

if __name__ == "__main__":
    # Add some testing here
    pass