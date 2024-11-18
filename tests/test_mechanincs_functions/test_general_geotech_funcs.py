from lib.mechanics_functions.general_geotech_funcs import (calc_consolidation_coeff, 
                                                 calc_dimensionless_velocity,
                                                 calc_cambridge_mean_eff_stress,
                                                 calc_white_failure_mean_eff_stress,
                                                 calc_mohr_coulomb_su,calc_Jaky_at_rest)
# Standard imports
import numpy as np

# Lib imports
from lib.general_functions.global_constants import GRAVITY_CONST

def test_calc_consolidation_coeff():
    """
    Test the consolidation coefficient calculation for known values. This is test
    """

    # Given values

    diameter = 0.2 #[m]
    t_50 = 3 #[s]
    T_50 = 0.6 #[s]

    # Expected result
    expected_consolidation_coefficient = 0.008 # [m^2]

    # Call the function
    result = calc_consolidation_coeff(diameter, t_50, T_50 = 0.6)

    # Check if the result is correct
    print("test_calc_consolidation_coefficient")
    np.testing.assert_almost_equal(result,expected_consolidation_coefficient, decimal = 6)

def test_calc_dimensionless_velocity():
    """
    Test the dimensionless velocity calculation for known values. This is test
    """

    # Given values

    v = 7 #[m/s]
    D = 0.2 #[m]
    coeff_consolidation = 0.008


    # Expected result
    expected_dimensionless_velocity = 175

    # Call the function
    result = calc_dimensionless_velocity(v, D, coeff_consolidation)

    # Check if the result is correct
    print("test_calc_dimensionless_velocity")
    np.testing.assert_almost_equal(result,expected_dimensionless_velocity, decimal = 6)

def test_calc_cambridge_mean_eff_stress():

    """
    Test the Cambridge mean effective stress (p'). This is test
    """

    # Given values

    sigma_1 = 155 #[kPa]
    sigma_2 = 1892 #[kPa]
    sigma_3 = 836 #[kPa]

    # Expected result
    expected_cambridge = 961 #[kPa]

    # Call the function
    result = calc_cambridge_mean_eff_stress(sigma_1,sigma_2,sigma_3)

    # Check if the result is correct
    print("test_calc_cambridge_mean_eff_stress")
    np.testing.assert_almost_equal(result,expected_cambridge, decimal = 6)

def test_calc_mohr_coulomb_su():
    """
    Test the undrained strength (s_{u}) assuming a Mohr-Coulomb failure envelope. This is test
    """

    # Given values

    Q = 10 
    relative_density = 70 #[%]

    # Expected result
    expected_white_failure = 21714.0389 #[kPa]

    # Call the function
    result = calc_white_failure_mean_eff_stress(relative_density,Q)

    # Check if the result is correct
    print("test_calc_white_failure_mean_eff_stress")
    np.testing.assert_almost_equal(result,expected_white_failure, decimal = 4)


def test_calc_white_failure_mean_eff_stress():
    """
    Test the White Failure mean effective stress. This is test
    """

    # Given values

    phi_cv = 32 #[degrees]
    failure_mean_eff_stress = 986 #[kPa]

    # Expected result
    expected_mohr_coulomb_su = 634.6 #[kPa]

    # Call the function
    result = calc_mohr_coulomb_su(failure_mean_eff_stress,phi_cv)

    # Check if the result is correct
    print("test_calc_white_failure_mean_eff_stress")
    np.testing.assert_almost_equal(result,expected_mohr_coulomb_su, decimal = 1)

def test_Jaky_at_rest(): 
    """
    Test the Jaky equation. This is test
    """

    # Given values

    phi_prime = 32 #[degrees]

    # Expected result
    expected_Jaky = 0.47 #[kPa]

    # Call the function
    result = calc_Jaky_at_rest(phi_prime)

    # Check if the result is correct
    print("test_calc_white_failure_mean_eff_stress")
    np.testing.assert_almost_equal(result,expected_Jaky, decimal = 2)

