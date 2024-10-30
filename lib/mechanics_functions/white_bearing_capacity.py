# Standard imports
import numpy as np
from scipy.optimize import fsolve

# Libary imports
from lib.general_functions.global_constants import GRAVITY_CONST, DEBUG
from lib.mechanics_functions.general_geotech_funcs import calc_dimensionless_velocity, calc_white_failure_mean_eff_stress, calc_mohr_coulomb_su
from lib.mechanics_functions.relative_density_funcs import calc_Jamiolkowski_relative_density

# TODO: Look other these functions and make sure all of the possible inputs into each of the nested functions 
# are incldued in the external function
def calc_qNet_dyn_at_vel(qNet_d_guess,  qNet_dyn, depth, relative_density, measured_velocity, coeff_consolidation,
                V_50 = 1, Q = 10, wanted_velocity = 0.02, probe_diameter = 1, phi_cv = 32, Nkt = 12, 
                calc_relative_density = False):
    
    """
    Calc the equivalent CPT bearing capacity at a given depth

    inputs:
        qNet_d_guess         : A guess of what the dry net bearing resistance is a good range is 1000 to 10000
        qNet_dyn             : The measured dynamic bearing resistance
        depth                : Depth of the current measurement below the sediment interface
        measured_velocity    : Velocity of the pffp at the measurement location
        coeff_consolidation  : Coefficient of consolidation of the soil
        V_50                 : Time to ???
        Q                    : Crushing coeff ???
        wated_velocity       : Velocity that q is wanted at

    """

    # Calc the current dimensionless velocity
    current_V = calc_dimensionless_velocity(measured_velocity, probe_diameter, coeff_consolidation)

    if calc_relative_density:
        qNet_dry = fsolve(find_qNet_dry_2, qNet_d_guess, args = (qNet_dyn, depth, current_V, V_50, Q, phi_cv, Nkt))

    else:
        # Calc the net dry bearing resistance
        qNet_dry = fsolve(find_qNet_dry, qNet_d_guess, args = (qNet_dyn, relative_density, current_V, V_50, Q, phi_cv, Nkt))
    
    #-------- Calc the terms for the wanted velocity ---------

    # Calc the dimensionless velocity
    wanted_V = calc_dimensionless_velocity(wanted_velocity, probe_diameter, coeff_consolidation)

    # Calc the failure mean eff stress
    p_f = calc_white_failure_mean_eff_stress(relative_density, Q)

    # Calc Su
    su = calc_mohr_coulomb_su(p_f, phi_cv)

    # Calc the qNet_undrained
    qNet_ud = calc_qNet_undrained(su, Nkt=Nkt)

    # Calc the dynamic bearing resistance at the wanted velocity
    wanted_qNet_dyn = calc_white_qNet_dyn(qNet_ud, qNet_dry, wanted_V, V_50)

    if DEBUG:
        print("Current V", current_V)
        print("Relative Density", relative_density)
        print("Current dimension less velocity", current_V)
        print("Dry bearing resistance (qNet_dry)", qNet_dry)
        print("wanted dimensionless V", wanted_V)

    return wanted_qNet_dyn

def calc_white_qNet_dyn(qNet_ud, qNet_d, V, V_50=1.0):
    """
    Calculate the net dynamic bearing resistance q_{net, dyn}, also referred to as the "backbone curve".

    This function is based on the work of White et al. (2018) and follows the equation:

    .. math::
        q_{net, dyn} = q_{net, ud} + (q_{net, d} - q_{net, ud}) \\frac{1}{1 + V/V_{50}}

    Parameters
    ----------
    qNet_ud : float
        Net undrained bearing resistance.
    qNet_d : float
        Net drained bearing resistance.
    V : float
        Dimensionless velocity as defined in White et al. (2018).
    V_50 : float, optional
        Parameter related to velocity, default is 1.0. For more details, refer to Randolph and Hope (2004).

    Returns
    -------
    float
        Net dynamic bearing resistance.

    Notes
    -----
    For detailed information, refer to the following paper:
    White, D. J., et al. "Free fall penetrometer tests in sand: Determining the equivalent static resistance."

    """
    return qNet_ud + (qNet_d - qNet_ud) * (1 / (1 + V / V_50))


def calc_qNet_undrained(undrained_strength, Nkt = 12):
    """
    Calc the Net undrained bearing resistange from Undrained strength (Su) and a cone factor (Nkt)

    Eqn:
        q_{net, u} = N_{kt} s_{u}
    """

    return Nkt * undrained_strength

def find_qNet_dry(qNet_d_guess, qNet_dyn, relative_density, V, V_50 = 1, Q = 10, phi_cv = 32, Nkt = 12):
    """
    Calculate the net drained bearing resistance.

    This function serves as the basis for a solver to find the net drained bearing resistance.

    Parameters
    ----------
    qNet_d_guess : float
        Initial guess for the net drained bearing resistance.
    qNet_dyn : float
        Dynamic bearing capacity.
    relative_density : float
        Relative density of the soil.
    V : float
        Applied load or force.
    V_50 : float, optional
        Reference velocity, default is 1.
    Q : float, optional
        Empirical parameter, default is 10.
    phi_cv : float, optional
        Critical state friction angle in degrees, default is 32.
    Nkt : float, optional
        Bearing capacity factor, default is 12.

    Returns
    -------

    float
        Difference between the calculated dynamic bearing capacity and the given dynamic bearing capacity.

    Notes
    -----

    - The function calculates the failure mean effective stress, the undrained shear strength, and the undrained bearing capacity.
    - It then calculates the dynamic bearing capacity based on these values and the initial guess.

    See Also
    --------

    calc_white_failure_mean_eff_stress : Function to calculate failure mean effective stress.
    calc_mohr_coulomb_su : Function to calculate undrained shear strength.
    calc_qNet_undrained : Function to calculate undrained bearing capacity.
    calc_white_qNet_dyn : Function to calculate dynamic bearing capacity.

    Examples
    --------

     qNet_d_guess = 100
     qNet_dyn = 150
     relative_density = 0.65
     V = 200
     find_qNet_dry(qNet_d_guess, qNet_dyn, relative_density, V)
    """
    
    # Calc the failure mean eff stress
    p_f = calc_white_failure_mean_eff_stress(relative_density, Q)

    # Calc Su
    su = calc_mohr_coulomb_su(p_f, phi_cv)

    # Calc the qNet_undrained
    qNet_ud = calc_qNet_undrained(su, Nkt)

    # Calc the dynamic bearing capacity
    qNet_dyn_calc = calc_white_qNet_dyn(qNet_ud, qNet_d_guess, V, V_50)
    
    return qNet_dyn_calc - qNet_dyn

def find_qNet_dry_2(qNet_d_guess, qNet_dyn, depth, V, V_50 = 1, Q = 10, phi_cv = 32, Nkt = 12):
    """
    Function to serve as the basis for the solver to find the net drained bearing resistance

    """
    
    # Calc the relative density
    relative_density = calc_Jamiolkowski_relative_density(qNet_d_guess, depth)

    # Calc the failure mean eff stress
    p_f = calc_white_failure_mean_eff_stress(relative_density, Q)

    # Calc Su
    su = calc_mohr_coulomb_su(p_f, phi_cv)

    # Calc the qNet_undrained
    qNet_ud = calc_qNet_undrained(su, Nkt)

    # Calc the dynamic bearing capacity
    qNet_dyn_calc = calc_white_qNet_dyn(qNet_ud, qNet_d_guess, V, V_50)
    
    return qNet_dyn_calc - qNet_dyn