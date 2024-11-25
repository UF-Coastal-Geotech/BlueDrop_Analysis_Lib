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
                V_50, Q, wanted_velocity, probe_diameter, phi_cv, Nkt, 
                calc_relative_density):
    '''def calc_qNet_dyn_at_vel(qNet_d_guess,  qNet_dyn, depth, relative_density, measured_velocity, coeff_consolidation,
                V_50 = 1, Q = 10, wanted_velocity = 0.02, probe_diameter = 1, phi_cv = 32, Nkt = 12, 
                calc_relative_density = False):'''
    
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

    This function computes the dynamic net bearing resistance (`qNet_dyn`) at a specified velocity (`wanted_velocity`) 
    and depth, given various soil and probe parameters. It first determines the dry net bearing resistance (`qNet_dry`) 
    using either a specified relative density or a guessed value and then computes the dynamic bearing resistance for the desired velocity.

    Parameters
    ----------

    qNet_d_guess : float
        An initial guess for the dry net bearing resistance. A reasonable range is between 1000 and 10000 kPa.
    qNet_dyn : float
        The measured dynamic net bearing resistance.
    depth : float
        Depth of the current measurement below the sediment interface, typically in meters.
    relative_density : float
        Relative density of the soil, typically expressed as a percentage. Used when `calc_relative_density` is True.
    measured_velocity : float
        Velocity of the portable free fall penetrometer (PFFP) at the measurement location, typically in m/s.
    coeff_consolidation : float
        Coefficient of consolidation of the soil, typically in m²/s.
    V_50 : float, optional
        Dimensionless velocity corresponding to a 50% reduction in the undrained shear strength. Default is 1.
    Q : float, optional
        Crushing coefficient or a parameter related to the soil’s response to penetration. Default is 10.
    wanted_velocity : float, optional
        Desired velocity at which the dynamic net bearing resistance is calculated. Default is 0.02 m/s.
    probe_diameter : float, optional
        Diameter of the probe used in the measurement, typically in meters. Default is 1 m.
    phi_cv : float, optional
        Critical state friction angle, typically in degrees. Default is 32°.
    Nkt : float, optional
        Cone factor, used to calculate the undrained shear strength from the net bearing resistance. Default is 12.
    calc_relative_density : bool, optional
        If True, the function will calculate the dry net bearing resistance based on the relative density. 
        If False, a dry net bearing resistance is calculated using a guessed value. Default is False.

    Returns
    -------
    
    float
        Dynamic net bearing resistance (`wanted_qNet_dyn`) at the specified velocity (`wanted_velocity`).

    Notes

    -----
    The function proceeds through the following steps:
    1. Calculate the dimensionless velocity (`current_V`) at the measured velocity.
    2. Determine the dry net bearing resistance (`qNet_dry`) based on either a guessed value or calculated relative density.
    3. Calculate the dynamic net bearing resistance (`wanted_qNet_dyn`) at the desired velocity.

    This function relies on several helper functions, including:
    - `calc_dimensionless_velocity`: Calculates the dimensionless velocity.
    - `find_qNet_dry`: Finds the dry net bearing resistance.
    - `calc_white_failure_mean_eff_stress`: Calculates the mean effective stress at failure.
    - `calc_mohr_coulomb_su`: Calculates the undrained shear strength using the Mohr-Coulomb criterion.
    - `calc_qNet_undrained`: Calculates the net bearing resistance under undrained conditions.
    - `calc_white_qNet_dyn`: Calculates the dynamic net bearing resistance using the White method.

    If debugging (`DEBUG`) is enabled, the function prints intermediate results, such as the calculated dimensionless velocities, relative density, and dry bearing resistance.

    Example
    -------
    
    Example usage:

    >>> qNet_dyn = calc_qNet_dyn_at_vel(qNet_d_guess=5000, qNet_dyn=1200, depth=5, relative_density=0.6,
                                        measured_velocity=0.05, coeff_consolidation=1e-6,
                                        V_50=1.5, Q=15, wanted_velocity=0.02, probe_diameter=0.05, 
                                        phi_cv=30, Nkt=10, calc_relative_density=True)
    >>> print(qNet_dyn)
    1100.34  # example output

    """

    # Calc the current dimensionless velocity
    current_V = calc_dimensionless_velocity(measured_velocity, probe_diameter, coeff_consolidation)
    print('current V =', current_V)
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
    Calc the Net undrained bearing resistance from Undrained strength (Su) and a cone factor (Nkt)

    Eqn:
        q_{net, u} = N_{kt} s_{u}

    Parameters
    ----------

    undrained_strength : float
        Undrained shear strength (Su) of the soil, typically in kPa.
    Nkt : float, optional
        Cone factor used to relate the undrained shear strength to the net bearing resistance. Default is 12.

    Returns
    -------

    float
        Net undrained bearing resistance (`q_net,u`), typically in kPa.

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

    Solve for the net drained bearing resistance (`qNet_dry`) considering depth and calculated relative density.

    Parameters
    ----------

    qNet_d_guess : float
        Initial guess for the net drained bearing resistance (`qNet_dry`), typically in kPa.
    qNet_dyn : float
        Measured dynamic bearing resistance, typically in kPa.
    depth : float
        Depth of the current measurement below the sediment interface, typically in meters.
    V : float
        Current dimensionless velocity.
    V_50 : float, optional
        Dimensionless velocity corresponding to a 50% failure probability. Default is 1.
    Q : float, optional
        Crushing coefficient. Default is 10.
    phi_cv : float, optional
        Critical state friction angle of the soil, in degrees. Default is 32°.
    Nkt : float, optional
        Cone factor used to relate the undrained shear strength to the net bearing resistance. Default is 12.

    Returns
    -------

    float
        Difference between the calculated dynamic bearing capacity and the measured dynamic bearing resistance (`qNet_dyn`).

    Notes
    -----

    This function first calculates the relative density using the `calc_Jamiolkowski_relative_density` function based on the guessed net drained bearing resistance (`qNet_dry`) and depth. It then uses this relative density to compute other parameters and ultimately the difference between the calculated and measured dynamic bearing capacities.

    """
    
    # Calc the relative density
    relative_density = calc_Jamiolkowski_relative_density(qNet_d_guess, depth)

    # Calc the failure mean eff stress
    p_f = calc_white_failure_mean_eff_stress(relative_density, Q)
    print(p_f)
    # Calc Su
    su = calc_mohr_coulomb_su(p_f, phi_cv)
    print(su)
    # Calc the qNet_undrained
    qNet_ud = calc_qNet_undrained(su, Nkt)
    print(qNet_ud)
    # Calc the dynamic bearing capacity
    qNet_dyn_calc = calc_white_qNet_dyn(qNet_ud, qNet_d_guess, V, V_50)
    
    return qNet_dyn_calc - qNet_dyn