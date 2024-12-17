from lib.mechanics_functions.soil_characteristic_funcs import (calc_firmness_factor)
                                                 
# Standard imports
import numpy as np

# Lib imports
from lib.general_functions.global_constants import GRAVITY_CONST

def test_calc_firmness_factor():
    """
    Test the firmness factor calculation for known values. This is test
    """

    # Given values

    gravity = GRAVITY_CONST #[9.80655 m/s^2]
    max_deceleration = 148 #[m/s^2]
    total_penetration_time = 30 #[s]
    impact_velocity = 48 #[m/s]

    # Expected result
    expected_firmness_factor =  0.010481

    # Call the function
    result = calc_firmness_factor(gravity, max_deceleration, total_penetration_time, impact_velocity)

    # Check if the result is correct
    print("test_calc_firmness_factor")
    np.testing.assert_almost_equal(result,expected_firmness_factor, decimal = 6)