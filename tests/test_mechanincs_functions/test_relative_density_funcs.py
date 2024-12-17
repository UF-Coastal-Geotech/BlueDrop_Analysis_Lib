from lib.mechanics_functions.relative_density_funcs import (calc_Albatal_rel_density, 
                                                 calc_Jamiolkowski_relative_density)
# Standard imports
import numpy as np

# Lib imports
from lib.general_functions.global_constants import GRAVITY_CONST

def test_calc_Albatal_rel_density():
    """
    Test the Albatal relative density calculation for known values. This is test
    """

    # Given values

    max_deceleration = 55 #[g's]

    # Expected result
    expected_Albatal_density = 78.2128

    # Call the function
    result = calc_Albatal_rel_density(max_deceleration)

    # Check if the result is correct
    print("test_calc_Albatal_rel_density")
    np.testing.assert_almost_equal(result,expected_Albatal_density, decimal = 4)

def test_calc_Jamiolkowski_relative_density():
    """
    Test the Jamiolkowski relative density calculation for known values. This is test
    """

    # Given values

    qNet_dry = 100 #[kPa]
    depth = 1.5 #[m]
    soil_unit_wt = 17.81 #[kN/m^3]
    water_unit_wt = 9.81 #[kN/m^3]
    C0 = 300 
    C1 = 0.46 
    C2 = 2.96 
    k0 = 0.5

    # Expected result
    expected_Jamiolkowski_density =  -0.694309

    # Call the function
    result = calc_Jamiolkowski_relative_density(qNet_dry, depth, soil_unit_wt = 17.81, water_unit_wt = 9.81, C0 = 300, C1 = 0.46, C2 = 2.96, k0 = 0.5)

    # Check if the result is correct
    print("test_calc_Jamiolkowski_relative_density")
    np.testing.assert_almost_equal(result,expected_Jamiolkowski_density, decimal = 6)