# import numpy as np

def calc_drag_force(rho_fluid, drag_coeff, velocity, frontal_area):
    """
    Calculate the drag force for a body.

    This function computes the drag force experienced by a body moving through a fluid
    based on the drag equation.

    Parameters
    ----------
    
    rho_fluid : float
        Density of the fluid [kg/m^3].
    drag_coeff : float
        Drag coefficient of the body.
    velocity : float
        Velocity of the body [m/s].
    frontal_area : float
        Frontal area of the body [m^2].

    Returns
    -------

    float
        Drag force [N].

    Notes
    -----

    The drag force is calculated using the following equation:
    
    .. math::
        F_{Drag} = \\frac{1}{2} \\rho_{fluid} v^{2} C_{D} A

    where:
        - :math:`F_{Drag}` is the drag force.
        - :math:`\\rho_{fluid}` is the density of the fluid.
        - :math:`v` is the velocity of the body.
        - :math:`C_{D}` is the drag coefficient.
        - :math:`A` is the frontal area.
    
    For more information on the drag equation, refer to the `drag info <https://en.wikipedia.org/wiki/Drag_(physics)#The_drag_equation>`_.

    """
    return 0.5 * rho_fluid * velocity**2 * drag_coeff * frontal_area


def calc_buoyant_force(rho_fluid, displaced_volume, gravity):
    """
    Calculate the buoyant force on an object in a fluid.

    This function computes the buoyant force experienced by an object submerged in a fluid 
    based on the principle of buoyancy.

    Parameters
    ----------

    rho_fluid : float
        Density of the fluid [kg/m^3].
    displaced_volume : float
        Volume of fluid displaced by the object [m^3].
    gravity : float
        Acceleration due to gravity [m/s^2].

    Returns
    -------

    float
        Buoyant force [N].

    Notes
    -----
    The buoyant force is calculated using the following equation:
    
    .. math::
        F_{B} = \\rho V_{disp} g
    
    where:
        - :math:`F_{B}` is the buoyant force.
        - :math:`\\rho` is the fluid density.
        - :math:`V_{disp}` is the volume of fluid displaced.
        - :math:`g` is the acceleration due to gravity.
    
    For more information on buoyant force, refer to the `buoyant force info <https://en.wikipedia.org/wiki/Buoyancy#Forces_and_equilibrium>`_.

    """
    return rho_fluid * displaced_volume * gravity


def calc_corrected_water_depth(uncorrected_depth, velocity, gravity):
    """
    Calculate the corrected water depth using a Bernoulli's type correction.

    This function computes the corrected water depth based on the given uncorrected depth, 
    velocity, and gravitational acceleration.

    Parameters
    ----------

    uncorrected_depth : float
        The uncorrected water depth [m].
    velocity : float
        The velocity of the water [m/s].
    gravity : float
        The acceleration due to gravity [m/s^2].

    Returns
    -------

    float
        The corrected water depth [m].

    Notes
    -----
    The corrected water depth is calculated using the following equation:
    
    .. math::
        h_{c} = h_{u} + \\frac{v^{2}}{2g}
    
    where:
        - :math:`h_{c}` is the corrected water depth.
        - :math:`h_{u}` is the uncorrected water depth.
        - :math:`v` is the velocity of the water.
        - :math:`g` is the acceleration due to gravity.
    
    The equation is based on Bernoulli's principle, as referenced in Jaber's thesis.
    
    """

    pass

if __name__ == "__main__":
    # Calc a test run of the equation

    # Answer should be 24
    drag = calc_drag_force(rho_fluid=1, velocity=2, drag_coeff=3, cross_section_area=4)
    
    # Store the correc answer for the above input vals
    correct_ans = 23

    print(f"Drag force: {drag}")
    if drag == correct_ans:
        print("Answer is correct")
    else:
        raise ValueError(f"Calculated value is {drag} correct answer is {correct_ans}")

