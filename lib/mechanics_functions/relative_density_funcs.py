# Standard imports 
import numpy as np

# Libary imports
from lib.mechanics_functions.general_geotech_funcs import calc_cambridge_mean_eff_stress
from lib.general_functions.global_constants import DEBUG

def  calc_Albatal_rel_density(max_deceleration):
    """
    Calculate the relative density following the correlation presented by Albatal (2019).

    Parameters
    ----------

    max_deceleration : float
        The maximum deceleration from the BlueDrop recording in g's.

    Returns
    -------

    float
        Relative density [-].

    Notes
    -----

    The relative density is calculated using the correlation provided by Albatal (2019):
    
    .. math::
        D_r = -2.18 \\times 10^{-4} \\cdot a^3 + 1.29 \\times 10^{-2} \\cdot a^2 + 1.61 \\cdot a - 13.09

    where:
        - :math:`D_r`: Relative density [-].
        - :math:`a`  : Maximum deceleration [g].

    For more information, refer to the paper:
    [Albatal (2019)](https://cdnsciencepub.com/doi/pdf/10.1139/cgj-2018-0267) (Equation at the bottom right of page 26).

    """
    return -2.18 * 1e-4 * max_deceleration**3  + 1.29 * 1e-2 * max_deceleration**2 + 1.61 * max_deceleration - 13.09

# def calc_Jamiolkowski_relative_density(qNet_dry, depth, soil_unit_wt = 17.81, water_unit_wt = 9.81, C0 = 300, C1 = 0.46, C2 = 2.96, k0 = 0.5):
def calc_Jamiolkowski_relative_density(qNet_dry, depth, soil_unit_wt = 17.81, water_unit_wt = 9.81, C0 = 300, C1 = 0.46, C2 = 2.96, k0 = 0.5):
    """
    Calculate the relative density (I_d) using the equation from Jamiolkowski et al. (2003).

    Parameters
    ----------

    qNet_dry : float
        Net drained bearing resistance [kPa].
    depth : float
        Depth below the seabed [m].
    soil_unit_wt : float, optional
        Total soil unit weight [kN/m^3], default is 17.81.
    water_unit_wt : float, optional
        Water unit weight (rho * g) [kN/m^3], default is 9.81.
    C0 : float, optional
        Dimensionless coefficient, default is 300.
    C1 : float, optional
        Coefficient, default is 0.46.
    C2 : float, optional
        Coefficient, default is 2.96.
    k0 : float, optional
        Coefficient of lateral earth pressure at rest, default is 0.5.

    Returns
    -------
    
    float
        Relative density (I_d).

    Notes
    -----
    The relative density is calculated using the following equation:
    
    .. math::
        I_{d} = \\frac{1}{C_{2}} \\ln \\left( \\frac{q_{net, d}}{ C_{0} p_{0}^{' \\ C_{1} } } \\right)

    where:
        - :math:`I_{d}`      : Relative density.
        - :math:`q_{net, d}` : Net drained bearing resistance.
        - :math:`C_{0}`      : Dimensionless coefficient.
        - :math:`C_{1}`      : Coefficient.
        - :math:`C_{2}`      : Coefficient.
        - :math:`p'_{0}`     : Mean effective stress.
    
    The vertical effective stress is calculated as:
    
    .. math::
        \\sigma_{1} = (\\gamma_{soil} - \\gamma_{water}) \\cdot \\text{depth}
    
    The horizontal effective stress is calculated as:
    
    .. math::
        \\sigma_{3} = k_{0} \\cdot \\sigma_{1}
    
    The mean effective stress is calculated using the Cambridge mean effective stress equation.
    
    For more information, refer to the paper: Jamiolkowski et al. (2003).
    
    """

    # Calc the vertical effective stress
    sigma_1 = (soil_unit_wt - water_unit_wt) * depth

    # Calc the horizontal effective stress
    sigma_3  = k0 * sigma_1 

    # Calc the mean effective stress
    mean_eff_stress = calc_cambridge_mean_eff_stress(sigma_1, sigma_3, sigma_3)

    # Calc the insid of the parenthesis
    inside = qNet_dry/(C0 * mean_eff_stress**C1)

    # if DEBUG:
    #     print("Inside the parenthesis: {}".format(inside))
    #     print("sigma_1: {:.2f}".format(sigma_1))
    #     print("Mean effective stress: {:.2f}".format(mean_eff_stress))

    # Calc the relative density
    return 1/C2 * np.log(inside)


if __name__ == "__main__":
    # Add some testing here
    pass