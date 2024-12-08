from lib.mechanics_functions.fluid_funcs import (calc_drag_force, 
                                                 calc_buoyant_force, 
                                                 calc_corrected_water_depth)

# Standard imports
import numpy as np

def test_calc_drag_force():
    """
    Test the drag force calculation for known values. This is test
    """

    # Given values

    rho_fluid    = 1.0 #[kg/m^3]
    drag_coeff   = 2.0 #[?]
    velocity     = 3.0 #[m/s]
    frontal_area = 4.0 # [m^2]

    # Expected result
    expected_drag_force = 36 # [N]

    # Call the function
    result = calc_drag_force(rho_fluid, drag_coeff, velocity, frontal_area)

    # Check if the result is correct
    print("test_calc_drag_force")
    np.testing.assert_almost_equal(result,expected_drag_force, decimal = 6)

def test_calc_buoyant_force():
    # Given values
    rho_fluid = 1.0 #[kg/m^3]
    displaced_volume = 2.0 #[m^3]

    g = 10.0

    expected_buoyancy_force = 20.0 #[N]

    result = calc_buoyant_force(rho_fluid, displaced_volume, g)
    np.testing.assert_almost_equal(result,expected_buoyancy_force, decimal = 6)

def test_calc_corrected_water_depth():
    pass