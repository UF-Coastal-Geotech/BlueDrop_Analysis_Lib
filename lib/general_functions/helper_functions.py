import os
import numpy as np
import pandas as pd
import shutil
import sys
from lib.general_functions.global_constants import GRAVITY_CONST

# File Purpose: Store general purpose functions - I will organize this better later
def create_folder_if_not_exists(folder_path):
    """
    Create a folder if it does not already exist.

    Parameters
    ----------
    
    folder_path : str
        The path to the folder to be created.

    Notes
    -----

    If the folder already exists, a message is printed indicating so.
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created successfully.")
    else:
        print(f"Folder '{folder_path}' already exists.")



def apply_mask_to_list(values, mask):
    """
    Apply a mask to a list of values.

    Parameters
    ----------
    
    values : list
        The list of values to be masked.
    mask : list of bool
        The mask to apply. Each element of the mask corresponds to an element in `values`.

    Returns
    -------
    
    list
        A new list containing only the values where the mask is True.
    """
    return [value for value, m in zip(values, mask) if m]

def progress_bar(iterations, total, time_left):
    """
    Display a progress bar in the console.

    Parameters
    ----------
    
    iterations : int
        The current iteration.
    total : int
        The total number of iterations.
    time_left : float
        Estimated time left in seconds.

    Notes
    -----
    
    The progress bar shows the completion percentage and the estimated time left in minutes.
    """
    progress = iterations / total
    bar_length = 50
    completed_length = int(bar_length * progress)
    remaining_length = bar_length - completed_length

    bar = "[" + "=" * completed_length + "-" * remaining_length + "]"
    percentage = "{:.2%}".format(progress)
    time_est = "{:.2}".format(time_left/60)
    sys.stdout.write("\r" + bar + " " + percentage + " ETA (min): " + time_est)
    sys.stdout.flush()

def convert_time_units(val, input_unit, output_unit):
    #Purpose: Convert one time unit to another
    # Fist convert everything to seconds
    """
    Convert a time value from one unit to another.

    Parameters
    ----------
    
    val : float
        The time value to be converted.
    input_unit : str
        The unit of the input value. Must be one of "min", "hour", "s".
    output_unit : str
        The desired output unit. Must be one of "min", "hour", "s".

    Returns
    -------
    
    float
        The converted time value.

    Notes
    -----
    
    The function first converts the input value to seconds and then to the desired output unit.
    """
    input_to_standard = {
        "min" : 60.0,
        "hour": 3600.0,
        "s"   : 1.0
    }
    
    standard_to_output = {
        "min" : 1/input_to_standard["min"],
        "hour": 1/input_to_standard["hour"],
        "s"   : input_to_standard["s"]
    }
    
    # Convert the val to seconds (s)
    standard = val * input_to_standard[input_unit]
    # Convert the standard value to the desired value
    output_val = standard * standard_to_output[output_unit]
    
    return output_val
    

def convert_accel_units(val, input_unit, output_unit):
    # Purpose: Convert one acceleration unit to another
    # First convert everything to m/s^2
    """
    Convert an acceleration value from one unit to another.

    Parameters
    ----------
    
    val : float
        The acceleration value to be converted.
    input_unit : str
        The unit of the input value. Must be one of "g", "m/s^2".
    output_unit : str
        The desired output unit. Must be one of "g", "m/s^2".

    Returns
    -------
    
    float
        The converted acceleration value.

    Notes
    -----
    
    The function first converts the input value to meters per second squared and then to the desired output unit.
    """
    input_to_standard ={
        "g": GRAVITY_CONST,
        "m/s^2":1
    }
    standard_to_output = {
        "g": 1/GRAVITY_CONST,
        "m/s^2":1
    }
    
    # Convert the val to m/s^2 (standard value)
    standard = val * input_to_standard[input_unit]
    # Convert the standard value to the desired value
    output_val = standard * standard_to_output[output_unit]
    # Return the value
    return output_val

def convert_length_units(val, input_unit, output_unit):
    # Purpose: Convert one length unit to another
    """
    Convert a length value from one unit to another.

    Parameters
    ----------
    
    val : float
        The length value to be converted.
    input_unit : str
        The unit of the input value. Must be one of "cm", "mm", "m".
    output_unit : str
        The desired output unit. Must be one of "cm", "mm", "m".

    Returns
    -------
    
    float
        The converted length value.

    Notes
    -----
    
    The function first converts the input value to meters and then to the desired output unit.
    
    """

    input_to_standard = {
        "cm":1e-2,
        "mm":1e-3,
        "m" : 1.0
    }
    standard_to_output = {
        "cm":1/input_to_standard["cm"],
        "mm":1/input_to_standard["mm"],
        "m" :1/input_to_standard["m"]
    }

    # Convert the val to standard value
    standard = val * input_to_standard[input_unit]

    # Conver the standard valuye to the desired output
    output_val = standard * standard_to_output[output_unit]

    return output_val

def convert_mass_units(val, input_unit, output_unit):
    # Purpose: Convert one mass unit to another
    """
    Convert a mass value from one unit to another.

    Parameters
    ----------
    
    val : float
        The mass value to be converted.
    input_unit : str
        The unit of the input value. Must be one of "g", "lb", "kg".
    output_unit : str
        The desired output unit. Must be one of "g", "lb", "kg".

    Returns
    -------
    
    float
        The converted mass value.

    Notes
    -----
    
    The function first converts the input value to kilograms and then to the desired output unit.
    """

    # Convert everything to kg
    input_to_standard = {
        "g" :1e-3,
        "lb":0.453592,
        "kg":1
    }
    standard_to_output = {
        "g":1/input_to_standard["g"],
        "lb":1/input_to_standard["lb"],
        "kg" :1/input_to_standard["kg"]
    }

    # Convert the val to standard value
    standard = val * input_to_standard[input_unit]

    # Conver the standard valuye to the desired output
    output_val = standard * standard_to_output[output_unit]

    return output_val

if __name__ == "__main__":
    # Add some testing here
    pass
