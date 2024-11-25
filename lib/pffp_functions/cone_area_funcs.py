#Standard imports 
import numpy as np
import pandas as pd

# From local library
from lib.pffp_functions.basic_geometry_funcs import calcCircleArea, calcConeLateralSurfaceArea, calcCylinderSurfaceArea, calcParabolaSurfaceArea
from lib.general_functions.global_constants import ALLOWED_TIP_TYPES_LIST


def calc_pffp_contact_area(penetrationDepth, areaCalcType, tipType, tipProps, tip_val_col):
    """
    Wrapper for the contact area functions for all cones.

    Assumes a consistent set of units.

    Parameters
    ----------

    penetrationDepth : array-like
        Array of depths the FFP has penetrated.
    areaCalcType : str
        Calculation type for the area, either "mantle" or "projected".
    tipType : str
        Type of the tip, either "blunt", "cone", or "parabola".
    tipProps : pandas.DataFrame
        DataFrame containing the tip properties required for the area calculation.
    tip_val_col : str
        The column name in `tipProps` that contains the tip property values.

    Returns
    -------
    
    area : array-like
        Calculated contact area.

    Raises
    ------

    TypeError
        If `tipProps` is not a pandas DataFrame.
    ValueError
        If `tipType` is not a valid type. Valid options are "blunt", "cone", or "parabola".

    Notes
    -----

    This function assumes a consistent set of units for all input parameters.

    Examples
    --------

    >>> import pandas as pd
    >>> tip_props = pd.DataFrame({
    ...     'Properties': ['tip_height', 'base_radius', 'tip_radius', 'radius_coeff'],
    ...     'Values': [10, 5, 1, 0.5]
    ... })
    >>> penetration_depth = [1, 2, 3]
    >>> calc_pffp_contact_area(penetration_depth, 'projected', 'cone', tip_props, 'Values')
    [calculated area array]
    """

    if not isinstance(tipProps, pd.DataFrame):
        raise TypeError("Tip props should be a dataframe of the tip properties") 
    
    # Unpack the general tip properties
    tipHeight = tipProps.loc[tipProps["Properties"] == "tip_height"][tip_val_col].iloc[0]
    baseRadius = tipProps.loc[tipProps["Properties"] == "base_radius"][tip_val_col].iloc[0] 

    # Calc area for cone tip
    match tipType:
        case "cone":
            # Unpack the cone properties
            coneTipRadius = tipProps.loc[tipProps["Properties"] == "tip_radius"][tip_val_col].iloc[0] 

            area = calcFFPConeContactArea(penetrationDepth, tipHeight, baseRadius, coneTipRadius,  areaCalcType)

        # Calc area for blunt tip
        case "blunt":
            area = calcFFPBluntContactArea(penetrationDepth, tipHeight, baseRadius, areaCalcType)
        
        case "parabola":
            # Unpack the radius coefficient
            radius_coeff = tipProps.loc[tipProps["Properties"] == "radius_coeff"][tip_val_col].iloc[0]

            area = calcParabolicContactArea(penetrationDepth, tipHeight, areaCalcType, radius_coeff)
        case _: 
            raise ValueError("{} is not a valid contact area calculation type\n \
                             Valid options are {}".format(tipType, ALLOWED_TIP_TYPES_LIST))
    return area 

#TODO: Could use a mask to calc the values for the whole array that is below the tipHeight and init array for the part that is above

def calcFFPConeContactArea(penetrationDepth, tipHeight, baseRadius, coneTipRadius, areaCalcType):
    """ 
    Purpose: calculates the contact area for the cone top of the FFP

    where:
        penetrationDepth: Array of penetration depth values
        baseRadius: Radius of the Cone at the base (Circular side)
        coneTipRadius: Radius of the cone tip (is not zero)
        tipHeight: Height of the cone when measured normal to the circular base
        areaCalcType: Selection of mantle or projected

    return: Array of calculated contact area values for each penetration depth.
    rtype: np.ndarray
    raises ValueError: If `areaCalcType` is not "mantle" or "projected"
    """

    # Init array to store area
    area = np.ones(len(penetrationDepth))

    # Calc cone side slope
    coneSideSlope = (baseRadius-coneTipRadius)/tipHeight

    for i, depth in enumerate(penetrationDepth):
        
        # if the depth is greater than the tipHeight of the cone
        if depth > tipHeight:
            # decrease the depth used in the calculation to the tipHeight
            depth = tipHeight
        
        # Calc the radius
        radius = coneTipRadius + depth * coneSideSlope

        # Check area selection
        if areaCalcType == "mantle":
            # if selected calc mantle area (Same as surface area without the base of cone)
            area[i] = calcConeLateralSurfaceArea(radius, depth)

        elif areaCalcType == "projected":
            # if selected calc projected area
            area[i] = calcCircleArea(radius)

        else: 
            return ValueError("areaCalcType must be mantle or projected. Currently is: {}".format(areaCalcType))

    return area

def calcFFPBluntContactArea(penetrationDepth, tipHeight, baseRadius, areaCalcType):
    """
    Purpose: Calc contact area for the blunt pffp tip
    
    where:
        penetrationDepth: Array of penetration depth values
        tipHeight: Height of the tip measured normal to the circular base
        baseRadius: Radius of the Cone at the base (Circular side)
        areaCalcType: Selection of mantle or projected
    """
    # init array to store area calcs
    area = np.zeros(len(penetrationDepth))

    for i, depth in enumerate(penetrationDepth):
        # if the depth is greater than the tipHeight of the blunt cylinder
        if depth > tipHeight:
            # decrease the depth used in the calculation to the tipHeight
            depth = tipHeight
        
        # Check the tipHeight in one line than calc the area in one line instead of looping
        # radius is constant for cylinder
        radius = baseRadius

        # Check area selection
        if areaCalcType == "mantle":
            # if selected calc mantle area (Surface Area of a cylinder)
            area[i] = calcCylinderSurfaceArea(radius, depth)

        elif areaCalcType == "projected":
            # if selected calc projected area
            area[i] = calcCircleArea(radius)

        else: 
            return ValueError("areaCalcType must be mantle or projected. Currently is: {}".format(areaCalcType))
        
    return area

def calcParabolicContactArea(penetrationDepth, tipHeight, areaCalcType, radius_coeff = 2.4184):
    """
    Purpose: Calc the contact area for the parabolic type of  the bluedrop

    where:
    penetrationDepth: Array of penetration depth values
    tipHeight: Height of the tip measured normal to the circular base
    areaCalcType: Selection of mantle or projected
    radius_coeff: The coefficient required to calc the radius of the parabola from the depth of penetration
                  radius = \sqrt{depth/a} where a is from the parabola eqn. depth = a * radius^{2}
    """
    # init array to store the area calcs
    area = np.zeros(len(penetrationDepth))

    for i, depth in enumerate(penetrationDepth):
        #if the depth  is greater than the max length of the parabolic  cylinder
        if depth  > tipHeight:
            # decrease the depth used in the calculatiion to the tipHeight
            depth = tipHeight

        # calc the radius
        radius = np.sqrt(radius_coeff * depth) 

        # Check area selection
        if areaCalcType == "mantle":
            # if selected  calc mantle area (Surface area of a parabola with the form y = f(x) = a*x^{2})
            area[i] = calcParabolaSurfaceArea(depth, radius_coeff)
        
        elif areaCalcType == "projected":
            #if selected calc projected area
            area[i] = calcCircleArea(radius)
    
    return area