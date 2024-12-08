from lib.mechanics_functions.friction_angle_funcs import (calc_Duncan_friction_angle, 
                                                 calc_Alabatal_friction_angle)
import numpy as np

def test_calc_Duncan_friction_angle():
    """
    Test the Duncan friction angle calculation for known values. This is test
    """

    # Given values

    relative_density    = 60 #%]
    unit_weight   = 1120 #[kg/m^3]
    max_depth     = 0.25 #[m]
    coeff = [34, 10, 3, 2]
    atmospheric_pressure = 101.325 #[kPa]

    # Expected result
    expected_Duncan_friction_angle = 38.1459 # [N]

    # Call the function
    result = calc_Duncan_friction_angle(relative_density, unit_weight, max_depth, coeff, atmospheric_pressure)

    # Check if the result is correct
    print("test_calc_Duncan_friction_angle")
    np.testing.assert_almost_equal(result,expected_Duncan_friction_angle, decimal = 6)

def test_calc_Alabatal_friction_angle():
    # Given values
    relative_density    = 60 #[%]
    unit_weight   = 1120 #[kg/m^3]
    max_depth     = 0.25 #[m]
    atmospheric_pressure = 101.325 #[kPa]


    expected_Alabatal_friction_angle = 37.7928 #[N]

    result = calc_Alabatal_friction_angle(relative_density, unit_weight, max_depth, atmospheric_pressure)
    print("test_calc_Alabatal_friction_angle")
    np.testing.assert_almost_equal(result,expected_Alabatal_friction_angle, decimal = 6)

