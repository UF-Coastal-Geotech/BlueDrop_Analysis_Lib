from lib.mechanics_functions.white_bearing_capacity import (calc_qNet_dyn_at_vel,
                                                            calc_dimensionless_velocity,
                                                            calc_white_qNet_dyn,
                                                            calc_qNet_undrained,
                                                            find_qNet_dry,
                                                            find_qNet_dry_2)

import numpy as np
import scipy
from scipy.optimize import fsolve

# Libary imports
from lib.general_functions.global_constants import GRAVITY_CONST, DEBUG
from lib.mechanics_functions.general_geotech_funcs import calc_dimensionless_velocity, calc_white_failure_mean_eff_stress, calc_mohr_coulomb_su
from lib.mechanics_functions.relative_density_funcs import calc_Jamiolkowski_relative_density                                             
# Standard imports
import numpy as np

# Lib imports
from lib.general_functions.global_constants import GRAVITY_CONST

def test_calc_qNet_dyn_at_vel():
    """
    
    """
    #NOT CURRENTLY SETUP/WORKING

def test_calc_white_qNet_dyn():
    '''Test the net dynamic bearing resistance q_{net, dyn}, also referred to as the "backbone curve" equation. This is a test.'''

    #Given Values
    qNet_ud = 105 #[kPa]
    qNet_d = 230 #[kPa] 
    V = 5.6 #[m/s]
    V_50 = 1.0 #[m/s]

    # Expected result
    expected_white_qNet_dyn =  123.939

    # Call the function
    result = calc_white_qNet_dyn(qNet_ud,qNet_d,V,V_50)

    # Check if the result is correct
    print("test_calc_white_qNet_dyn")
    np.testing.assert_almost_equal(result,expected_white_qNet_dyn, decimal = 3)

def test_calc_qNet_undrained():
    '''Test the Net undrained bearing resistance from Undrained strength (Su) and a cone factor (Nkt) equation. This is a test.'''

    #Given Values
    undrained_strength = 250 #[kPa]
    Nkt = 12 #[cone factor default value]

    # Expected result
    expected_qNet_undrained = 3000 

    # Call the function
    result = calc_qNet_undrained(undrained_strength,Nkt)

    # Check if the result is correct
    print("test_calc_qNet_undrained")
    np.testing.assert_almost_equal(result,expected_qNet_undrained, decimal = 6)

def test_find_qNet_dry():
    '''Test the det drained bearing resistance solver. This is a test.'''

    #Given Values
    qNet_d_guess = 100 #[kPa]
    qNet_dyn = 123.939 #[kPa]
    relative_density = 60 #[%]
    V = 5.6 #[m/s]
    V_50 = 1 #[m/s]
    Q = 10 #[crushing coefficient default value]
    phi_cv = 32 #[degrees]
    Nkt = 12 #[cone factor default value]

    # Hand Calc for p_f: 21662.40033777
    # Hand Calc for su: 13942.0421555
    # Hand Calc for qNet_ud: 167304.505866
    # Hand Calc for qNet_dyn_calc: 141670.4898257

    # Expected result
    expected_qNet_dry = 141846.5508257

    # Call the function
    result = find_qNet_dry(qNet_d_guess, qNet_dyn, relative_density, V, V_50, Q, phi_cv, Nkt)

    # Check if the result is correct
    print("test_calc_qNet_undrained")
    np.testing.assert_almost_equal(result,expected_qNet_dry, decimal = 6)

def test_find_qNet_dry2():
    '''Test the det drained bearing resistance solver. This is a test.'''

    #Given Values
    qNet_d_guess = 100 #[kPa]
    qNet_dyn = 123.939 #[kPa]
    depth = 1.5 #[m]
    V = 5.6 #[m/s]
    V_50 = 1 #[m/s]
    Q = 10 #[crushing coefficient default value]
    phi_cv = 32 #[degrees]
    Nkt = 12 #[cone factor default value]

    # Hand Calc for relative_density: -0.6943092560273
    # Hand Calc for p_f: 92993.081908145
    # Hand Calc for su: 59850.868228701
    # Hand Calc for qNet_ud: 71810.41874441
    # Hand Calc for qNet_dyn_calc: 609405.80984374
    # Expected result
    expected_qNet_dry2 = 609405.80984374

    # Call the function
    result = find_qNet_dry_2(qNet_d_guess, qNet_dyn, depth, V, V_50, Q, phi_cv, Nkt)
    
    # Check if the result is correct
    print("test_calc_qNet_undrained")
    np.testing.assert_almost_equal(result,expected_qNet_dry2, decimal = 4)
