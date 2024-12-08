# Standard imports
import numpy as np

# Lib imports
from lib.general_functions.global_constants import GRAVITY_CONST

def calc_consolidation_coeff(diameter, t_50, T_50 = 0.6):
    """
    Calculate the consolidation coefficient (c_h).

    This function computes the consolidation coefficient based on the given diameter, time to 50% pore pressure
    dissipation, and a dimensionless time factor.

    Parameters
    ----------

    diameter : float
        Diameter of the penetrating object [m].
    t_50 : float
        Time to 50% of pore pressure dissipation [s].
    T_50 : float, optional
        Dimensionless time factor (default is 0.6).

    Returns
    -------

    float
        Consolidation coefficient [m^2/s].

    Notes
    -----

    The consolidation coefficient is calculated using the following equation:
    
    .. math::
        c_{h} = \\frac{D^{2} T_{50}}{t_{50}}

    where:
        - :math:`D` is the diameter of the penetrating object.
        - :math:`t_{50}` is the time to 50% of pore pressure dissipation.
        - :math:`T_{50}` is the dimensionless time factor.

    Reference
    ---------
    
    White, D. J., et al. "Free fall penetrometer tests in sand: Determining the equivalent static resistance."
    
    """

    return ((diameter**2) * T_50)/t_50

def calc_dimensionless_velocity(v, D, coeff_consolidation):
    """
    Calculate the dimensionless velocity (V).

    Parameters
    ----------

    v : float
        Probe velocity [m/s].
    D : float
        Diameter of the probe [m].
    coeff_consolidation : float
        Consolidation coefficient (c_{h}).

    Returns
    -------

    float
        Dimensionless velocity (V).

    Notes
    -----

    The dimensionless velocity is calculated using the equation:
    
    .. math::
        V = \\frac{v \\cdot D}{c_{h}}
    
    where:
    
        - :math:`V`     : Dimensionless velocity.
        - :math:`v`     : Probe velocity.
        - :math:`D`     : Diameter of the probe.
        - :math:`c_{h}` : Consolidation coefficient.

    """

    return v * D/coeff_consolidation

def calc_cambridge_mean_eff_stress(sigma_1, sigma_2, sigma_3):
    """
    Calculate the Cambridge mean effective stress (p').

    Parameters
    ----------

    sigma_1 : float
        Effective stress 1.
    sigma_2 : float
        Effective stress 2.
    sigma_3 : float
        Effective stress 3.

    Returns
    -------

    float
        Cambridge mean effective stress (p').

    Notes
    -----

    The Cambridge mean effective stress is calculated using the equation:
    
    .. math::
        p' = \\frac{{\sigma'_{1} + \sigma'_{2} + \sigma'_{3}}}{{3}}
    
    where:
        - :math:`p'`           : Cambridge mean effective stress.
        - :math:`\\sigma'_{1}` : Effective stress 1.
        - :math:`\\sigma'_{3}` : Effective stress 3.
        - :math:`\\sigma'_{2}` : Effective stress 2.

    """

    return (sigma_1 +sigma_2 + sigma_3)/3

def calc_white_failure_mean_eff_stress(relative_density, Q = 10):
    """
    Calculate the mean effective stress at failure (p'_{f}).

    Parameters
    ----------

    Q : float
        Crushing strength parameter. Commonly taken as 10.
    relative_density : float
        Relative density.

    Returns
    -------

    float
        Mean effective stress at failure (p'_{f}) [kPa].

    Notes
    -----

    The mean effective stress at failure is calculated using the equation:
    
    .. math::
        p'_{f} = e^{Q - \\frac{1}{I_{D}}}
    
    where:
        - :math:`p'_{f}` : Mean effective stress at failure.
        - :math:`Q`      : Crushing strength parameter.
        - :math:`I_{D}`  : Relative density.

    Note that the equation derivation assumes zero relative dilatancy (I_{R} = 0) at undrained failure.

    """

    return np.exp( Q - 1/relative_density )

def calc_mohr_coulomb_su(failure_mean_eff_stress, phi_cv = 32):
    """
    Calculate the undrained strength (s_{u}) assuming a Mohr-Coulomb failure envelope.

    Parameters
    ----------

    failure_mean_eff_stress : float
        Mean effective stress at failure [kPa].
    phi_cv : float
        Friction angle at constant volume [degrees].

    Returns
    -------

    float
        Undrained strength (s_{u}) [kPa].

    Notes
    -----

    The undrained strength is calculated using the equation:
    
    .. math::
        s_{u} = \\frac{1}{2} p'_{f} \\frac{6 \\sin(\\phi_{cv})}{3 - \\sin(\\phi_{cv})}

    where:
        - :math:`s_{u}`     : Undrained strength.
        - :math:`p'_{f}`    : Mean effective stress at failure.
        - :math:\\phi_{cv}` : Friction angle at constant volume (in degrees).

    """

    # Convert phi to radians
    phi_cv = phi_cv * np.pi/180

    # Calc the inside of the parenthesis
    inside = 6 * np.sin(phi_cv)/( 3 - np.sin(phi_cv))

    return 0.5 * failure_mean_eff_stress * inside

def calc_Jaky_at_rest(phi_prime):
    """
    Calculate at rest earth pressure coefficient (k_{0}) using Jaky relationship.

    Parameters
    ----------

    phi_prime : float
        Effective friction angle [degrees].

    Returns
    -------

    float
        Coefficient of At Rest Lateral Earth Pressure

    Notes
    -----

    The coefficient of at rest lateral earth pressure is calculated using the equation:
    
    .. math::
        

    where:
        - :math:`k_{0}`     : Coefficient of At Rest Lateral Earth Pressure
        - :math:\\phi_prime`      : Effective friction angle

    """

    return 1 - (np.sin(phi_prime*(np.pi/180)))

"""
TODO: These are the functions that I want to add:
    - Jaky 1- sin(phi')
    - k0 as a function of effective stress (Never total stress)
    - """

if __name__ == "__main__":
    # Add some testing here
    pass