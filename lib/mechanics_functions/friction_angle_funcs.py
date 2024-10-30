# Standard imports
import numpy as np

# Functions that are related to calculating friction angle

def calc_Duncan_friction_angle(relative_density, unit_weight, max_depth, coeff = [34, 10, 3, 2], atmospheric_pressure = 101.325):
    """
    Calculate the friction angle (phi) using the Duncan correlation.

    This function computes the friction angle of soil based on the Duncan correlation,
    as noted in Albatal et al. (2020) DOI: 10.1139/cgj-2018-0267. The original source of the equation 
    should be verified as the Duncan et al. (2014) reference. I couldn't find this equation in there.

    Parameters
    ----------

    relative_density : float
        Relative density of the soil.
    unit_weight : float
        Unit weight of the soil (assumed to be 1120 kg/m^3 for the calculation).
    max_depth : float
        Max penetration depth of the FFP.
    coeff : list of float, optional
        Coefficients [A, B, C, D] from the Duncan correlation (default is [34, 10, 3, 2]).
    atmospheric_pressure : float, optional
        Atmospheric pressure in kPa (default is 101.325 kPa).

    Returns
    -------

    float
        Calculated friction angle (phi).

    Notes
    -----

    The friction angle is calculated using the following equation:
    
    .. math::
        \\phi' = A^{*} + B^{*}(D_{r}) - [C^{*} + D^{*}(D_{r})] \\log(\\sigma'_{n} / P_{a})

    where:
        - :math:`A^{*}` is a constant with a value of 34.
        - :math:`B^{*}` is a constant with a value of 10.
        - :math:`C^{*}` is a constant with a value of 3.
        - :math:`D^{*}` is a constant with a value of 2.
        - :math:`D_{r}` is the relative density.
        - :math:`\\sigma_{n}` is the normal stress (assumed to be the vertical normal stress).
        - :math:`P_{a}` is the atmospheric pressure (used to make the stress dimensionless).

    Note: If alternate values for the equation coefficients are available, they can be passed into this function.
    
    """
    
    # Coefficients A, B, C, and D from the Duncan correlation
    A = coeff[0]
    B = coeff[1]
    C = coeff[2]
    D = coeff[3]

    sigma = unit_weight  * max_depth

    phi = A * B  * relative_density/100 - (C + D * relative_density/100) *  np.log(sigma/atmospheric_pressure)

    return phi


def calc_Alabatal_friction_angle(relative_density, unit_weight, max_depth, atmospheric_pressure = 101.325):
    """
    Calculate the friction angle (phi) using the modified Duncan correlation coefficients from Albatal.

    This function acts as a wrapper for the Duncan friction angle equation, using the specific coefficients
    provided by Albatal. The coefficients and methodology are adapted from Albatal et al. (2020).

    Albatal et al. (2020) DOI: 10.1139/cgj-2018-0267

    Parameters
    ----------

    relative_density : float
        Relative density of the soil.
    unit_weight : float
        Unit weight of the soil (assumed to be 1120 kg/m^3 for the calculation).
    max_depth : float
        Max penetration depth of the FFP.
    atmospheric_pressure : float, optional
        Atmospheric pressure in kPa (default is 101.325 kPa).

    Returns
    -------

    float
        Calculated friction angle (phi).

    Notes
    -----

    This function utilizes the Duncan friction angle equation with coefficients from Albatal et al. (2020):
    
    1. .. math::
        \\phi' = A^{*} + B^{*}(D_{r}) - [C^{*} + D^{*}(D_{r})] \\log(\\sigma'_{n} / P_{a})

    where:
        - :math:`A^{*}` is a constant with a value of 34.
        - :math:`B^{*}` is a constant with a value of 10.
        - :math:`C^{*}` is a constant with a value of 2.
        - :math:`D^{*}` is a constant with a value of 5.
        - :math:`D_{r}` is the relative density.
        - :math:`\\sigma_{n}` is the normal stress (assumed to be the vertical normal stress).
        - :math:`P_{a}` is the atmospheric pressure (used to make the stress dimensionless).

    Note: The coefficients are specific to Albatal's fit and may differ from other versions of the Duncan correlation.
    
    """

    # List of coefficients that Albatal used for his fit
    Alabatal_coeff = [34, 10, 2, 5]

    # Calc phi (friction angle)
    phi = calc_Duncan_friction_angle(relative_density, unit_weight, max_depth, Alabatal_coeff, atmospheric_pressure)

    return phi

if __name__ == "__main__":
    # Add some testing here
    pass