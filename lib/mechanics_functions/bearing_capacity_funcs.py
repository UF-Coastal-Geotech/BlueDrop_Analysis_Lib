# Standard imports
import numpy as np

# Lib imports
from lib.general_functions.global_constants import GRAVITY_CONST, DEBUG
from lib.mechanics_functions.fluid_funcs import calc_drag_force

def calc_air_drop_dyn_bearing(pffp_accel, pffp_velocity, pffp_mass, pffp_frontal_area, soil_contact_area, 
                              drag_coeff, gravity, rho_air):
    """
    Calculate the soil dynamic bearing capacity for air drops.

    This function computes the dynamic bearing capacity of the soil when subjected to air drops,
    following the equations provided below. Units are assumed to be standard SI (m/s^2, Newtons, kg).
    The reference frame convention assumes the direction towards the sky is positive.

    Note: DO NOT pass raw accelerometer data to this function. The acceleration passed should be the sensor 
    offset by 1g down (i.e., `pffp_accel = raw_sensor_accel - 1g`).

    Parameters
    ----------

    pffp_accel : float
        Acceleration of the portable free fall penetrometer (pffp) during impact.
    pffp_velocity : float
        Velocity of the pffp.
    pffp_mass : float
        Mass of the pffp.
    pffp_frontal_area : float
        Frontal area of the pffp.
    soil_contact_area : float
        Contact area between the soil and the pffp.
    drag_coeff : float
        Drag coefficient.
    gravity : float
        Gravity constant.
    rho_air : float
        Density of the air.

    Returns
    -------

    float
        Net dynamic bearing capacity.

    Notes
    -----

    Equations:

    1. .. math::
        F_{Br} = m_{p} a_{p} + m_{p} g - \\frac{1}{2} \\rho_{fluid} v_{p}^{2} C_{D} A

    2. .. math::
        q_{Dyn} = \\frac{F_{Br}}{A}

    where:
        - :math:`F_{Br}`        : Force of soil bearing resistance.
        - :math:`m_{p}`         : Mass of the portable free fall penetrometer (pffp).
        - :math:`a_{p}`         : Acceleration of the pffp during impact.
        - :math:`g`             : Gravity constant.
        - :math:`\\rho_{fluid}` : Density of the fluid.
        - :math:`v_{p}`         : Velocity of the pffp.
        - :math:`C_{D}`         : Drag coefficient.
        - :math:`A`             : Frontal area (single value).

    """

    # Calc the force of gravity
    force_gravity = pffp_mass * gravity
    
    # Calc the drag force
    force_drag = calc_drag_force(rho_fluid = rho_air, drag_coeff = drag_coeff, velocity = pffp_velocity, frontal_area = pffp_frontal_area )

    # Calc the bearing force
    force_bearing = pffp_mass * pffp_accel + force_gravity - force_drag

    # Calc the dyn
    qDyn = force_bearing/soil_contact_area

    return  qDyn

def calc_water_drop_dyn_bearing(pffp_accel, pffp_velocity, pffp_mass, pffp_frontal_area, soil_contact_area, pffp_volume, drag_coeff, gravity, rho_water):
    """
    Calculate the soil dynamic bearing capacity for water drops.

    This function computes the dynamic bearing capacity of the soil when subjected to water drops,
    following the equations provided below. Units are assumed to be standard SI (m/s^2, Newtons, kg).
    The reference frame convention assumes the direction towards the sky is positive.

    Note: DO NOT pass raw accelerometer data to this function. The acceleration passed should be the sensor 
    offset by 1g down (i.e., `pffp_accel = raw_sensor_accel - 1g`).

    Parameters
    ----------

    pffp_accel : float
        Acceleration of the portable free fall penetrometer (pffp) during impact.
    pffp_velocity : float
        Velocity of the pffp.
    pffp_mass : float
        Mass of the pffp.
    pffp_frontal_area : float
        Frontal area of the pffp.
    soil_contact_area : float
        Contact area between the soil and the pffp.
    pffp_volume : float
        Volume of the pffp.
    drag_coeff : float
        Drag coefficient.
    gravity : float
        Gravity constant.
    rho_water : float
        Density of the water.

    Returns
    -------

    float
        Net dynamic bearing capacity.

    Notes
    -----

    Equations:
    
    1. .. math::
        F_{Br} = m_{p} a_{p} + m_{p} g - \\rho_{f} V_{p} g - \\frac{1}{2} \\rho_{f} v_{p}^{2} C_{D} A

    2. .. math::
        q_{Dyn} = \\frac{F_{Br}}{A}

    where:
        - :math:`F_{Br}`        : Force of soil bearing resistance.
        - :math:`m_{p}`         : Mass of the portable free fall penetrometer (pffp).
        - :math:`a_{p}`         : Acceleration of the pffp during impact.
        - :math:`g`             : Gravity constant.
        - :math:`\\rho_{fluid}` : Density of the fluid.
        - :math:`V_{p}`         : Volume of the pffp.
        - :math:`v_{p}`         : Velocity of the pffp.
        - :math:`C_{D}`         : Drag coefficient.
        - :math:`A`             : Frontal area (single value).

    """
     
    # Calc the force of gravity
    force_gravity = pffp_mass * gravity 

    # Calc the buyant force assuming water pressure in soil doesn't change # NOTE: This is a pretty big assumption
    force_buoyant = rho_water * gravity * pffp_volume
    
    # Calc the drag force
    force_drag = calc_drag_force(rho_fluid=rho_water,drag_coeff= drag_coeff, velocity=pffp_velocity, frontal_area= pffp_frontal_area)

    # Calc the bearing capacity force 
    force_bearing = pffp_mass * pffp_accel + force_gravity - force_buoyant - force_drag

    # Need to convert force_bearing to array to over the stored indices in it's series
    # Calc the dynamic bearing capacity
    qDyn = np.array(force_bearing)/soil_contact_area

    return qDyn

def calc_dyn_bearing_capacity(pffp_accel, pffp_velocity, pffp_mass, pffp_frontal_area, soil_contact_area, pffp_volume, water_drop, drag_coeff = 0.0, 
                              gravity = GRAVITY_CONST, rho_water = 1020, rho_air = 1.293):
    """
    Calculate the dynamic bearing capacity of the soil for both water and air drops.

    This function acts as a wrapper for calculating the dynamic bearing capacity for both water and air drops.
    It uses the acceleration of the portable free fall penetrometer (pffp) and other parameters to compute the 
    dynamic bearing capacity. Note that the acceleration should not be the raw sensor acceleration but should 
    be adjusted to the pffp acceleration.

    Parameters
    ----------

    pffp_accel : float
        Deceleration of the pffp.
    pffp_velocity : float
        Velocity of the pffp, used to calculate the drag force.
    pffp_mass : float
        Mass of the Free Fall Penetrometer (FFP).
    pffp_frontal_area : float
        Frontal area of the pffp. This is a single number.
    soil_contact_area : float
        Contact area between the FFP and the soil.
    pffp_volume : float
        Volume of the FFP.
    water_drop : bool
        True for water drops, False for air drops.
    drag_coeff : float, optional
        Drag coefficient of the pffp. Default is 1.0.
    gravity : float, optional
        Gravity constant. Default is GRAVITY_CONST.
    rho_water : float, optional
        Density of water. Default is 1020 kg/m^3, a good estimate for ocean water.
    rho_air : float, optional
        Density of the air. Default is 1.293 kg/m^3.

    Returns
    -------

    float
        Dynamic bearing capacity of the soil.

    Notes
    -----

    This function selects the appropriate calculation method based on the `water_drop` flag.
    If `water_drop` is True, it uses the water drop calculation. If False, it uses the air drop calculation.

    """
    
    # Make sure water_drop is set to True or False
    if not isinstance(water_drop, bool):
        raise TypeError(f"water_drop type is {type(water_drop)}. The type should be a boolean. Therefore it has to have a value of True or False")
    
    if water_drop:
        # Calc the dynamic bearing capacity
        qDyn = calc_water_drop_dyn_bearing(pffp_accel, pffp_velocity, pffp_mass= pffp_mass, pffp_frontal_area=pffp_frontal_area, 
                                           soil_contact_area=soil_contact_area, pffp_volume = pffp_volume, drag_coeff = drag_coeff, 
                                           gravity=gravity, rho_water=rho_water)

    elif not water_drop:
        # Otherwise do the calc using the air drop formula
        qDyn = calc_air_drop_dyn_bearing(pffp_accel=pffp_accel, pffp_velocity=pffp_velocity, pffp_mass=pffp_mass, pffp_frontal_area=pffp_frontal_area,
                                         soil_contact_area=soil_contact_area, drag_coeff = drag_coeff, gravity=gravity, rho_air = rho_air)

    return qDyn

def calc_qs_bearing_capacity(velocity, strainrateCorrectionType, qDyn, k_factor = 0.1, ref_velocity = 0.02):
    """
    Calculate the quasi-static bearing capacity value.

    This function computes the quasi-static bearing capacity value based on the given velocity,
    strain rate correction type, dynamic bearing capacity, and other parameters.

    Parameters
    ----------

    velocity : array-like
        Array of FFP velocity values [m/s].
    strainrateCorrectionType : str
        Type of strain rate correction to use. Must be one of "log", "Brilli", or "invHyperSin".
    qDyn : float
        Dynamic bearing capacity value.
    k_factor : float, optional
        K factor to be used. Default is 0.1.
    ref_velocity : float, optional
        Reference velocity for strain rate correction. Default is 0.02 m/s.

    Returns
    -------

    float
        Quasi-static bearing capacity value.

    Raises
    ------

    ValueError
        If `strainrateCorrectionType` is not one of the following: "log", "Brilli", "invHyperSin".

    Notes
    -----

    This function calculates the strain rate correction factor (`f_SR`) based on the specified 
    `strainrateCorrectionType` and then uses it to compute the quasi-static bearing capacity value (`qsbc`).

    The strain rate correction types are as follows:

    - "log": Logarithmic strain rate correction.

    - "Brilli": Strain rate correction following Brilli et al. (20??). Commonly used for air drops.

    - "invHyperSin": Inverse hyperbolic sine correction factor following Stephan (2015) and Randolph (2004).

    Warnings
    --------

    A warning is printed if a non-standard `k_factor` is used for the Brilli type strain rate correction.

    """

    maxVelocity = np.max(velocity)
    
    # make sure that velocity isn't a series
    velocity = np.array(velocity)

    # Selct with strain rate factor should be used
    match strainrateCorrectionType:
        case "log":

            # Force the log val to not become undefined
            log_val = np.log10(velocity / ref_velocity)
            log_val = np.nan_to_num(log_val, nan=0.0)
            
            f_SR = 1 + k_factor * log_val

        case "Brilli":
            # Strain rate correction factor following Brilli et al. (20??) Commonly used for air drops
            
            # The value used by Brilli was 0.31
            if k_factor != 0.31:
                # Print a warning if a non-standard value is used for the brilli type calculation
                print("Warning: Value used for Brilli type strain rate correction is not 0.31")
            
            log_val = np.log10(velocity/ref_velocity)
            f_SR = 1 + k_factor * maxVelocity * log_val

        case "invHyperSin":
            # Inv hyperbolic sin correction factor following Stephan (2015) and Randolph (2004)
            f_SR = 1 + k_factor/np.log(10) * np.arcsinh(velocity / ref_velocity)

        case _:
            ValueError("strainrateCorrectionType must be one of the folliwng: log, Brilli, invHyperSin.")

    # calc Quasi Static Bearing capacity value
    qsbc = qDyn / f_SR
    
    return qsbc

if __name__ == "__main__":
    # Add some testing here
    pass