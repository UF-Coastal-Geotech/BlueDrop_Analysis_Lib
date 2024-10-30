from numpy import sqrt as np_sqrt

from lib.general_functions.global_constants import PI_CONST

def calcCylinderSurfaceArea(radius, height):
    """
    Purpose: Calculates the Surface area of a cylinder
    where:
        radius: Radius of the cylinder
        height of the cylinder

    Parameters
    ----------

    radius : float
        The radius of the cylinder's base, typically in units of length (e.g., meters).
    height : float
        The height of the cylinder, typically in units of length (e.g., meters).

    Returns
    -------

    float
        The total surface area of the cylinder, typically in square units (e.g., square meters).

    Notes
    -----

    The total surface area is calculated as the sum of the area of the two circular bases and the area of the lateral surface. The formula used is:

    .. math::

        A_{\text{total}} = 2 \pi r^2 + 2 \pi r h

    where:
    - :math:`r` is the radius of the cylinder's base.
    - :math:`h` is the height of the cylinder.
    - :math:`\pi` is a mathematical constant approximately equal to 3.14159.

    Example
    -------

    Calculate the surface area of a cylinder with a radius of 3 units and a height of 5 units:

    >>> radius = 3
    >>> height = 5
    >>> surface_area = calcCylinderSurfaceArea(radius, height)
    >>> print(surface_area)
    150.79644737231007  # example output

    """
    baseArea = PI_CONST * radius**2 # Surface area of the base of the cylinder
    sideArea = 2 * PI_CONST * radius * height # Surface area on the side of the cylinder
    totalSurfaceArea = baseArea + sideArea
    return totalSurfaceArea

def calcConeLateralSurfaceArea(radius, height):
    """
    Calculates the lateral surface area of a cone.

    Parameters
    ----------

    radius : float
        The radius of the base of the cone.
    height : float
        The height of the cone, measured perpendicular to the base.

    Returns
    -------

    float
        The lateral surface area of the cone.

    Notes
    -----

    The lateral surface area of a cone is calculated using the formula:
        A = π * radius * sideSlope
    where the sideSlope (slant height) of the cone is calculated as:
        sideSlope = sqrt(height^2 + radius^2)
    """
    return PI_CONST * radius * np_sqrt(height**2 + radius**2)

def calcCircleArea(radius):
    """
    Calculates the area of a circle.

    Parameters
    ----------

    radius : float
        The radius of the circle.

    Returns
    -------

    float
        The area of the circle.

    Notes
    -----
    
    The area of a circle is calculated using the formula:
        A = π * radius^2
    """

    return PI_CONST * radius**2

def calcParabolaSurfaceArea(depth, radius_coeff):
    """
    Calculate the surface area of a rotated parabola.

    This function computes the surface area of a parabola rotated around its axis 
    using the surface area formula derived from Pappus's centroid theorem.

    The surface area \( A_{mantle} \) is given by:

        A_{mantle} = \frac{4}{3} \frac{\pi}{r_c} \left[ \left( r_c d + \frac{r_c^2}{4} \right)^{3/2} - \left( \frac{r_c^2}{4} \right)^{3/2} \right]

    where:
        r_c : radius coefficient (constant related to the curvature of the parabola)
        d   : depth of penetration (height on the parabola)

    Parameters
    ----------
    
    depth : float
        The depth of penetration or height on the parabola.
    radius_coeff : float
        The radius coefficient, related to the curvature of the parabola.

    Returns
    -------

    float
        The surface area of the rotated parabola.

    Notes
    -----

    The integral used in the surface area calculation has an analytic solution. 
    Ensure that the depth and radius_coeff are positive numbers to avoid mathematical errors.

    Examples
    --------
    >>> calcParabolaSurfaceArea(10, 5)
    334.23874119161055
    """
      # Ensure the depth and radius_coeff are positive
    if depth <= 0 or radius_coeff <= 0:
        raise ValueError("Both depth and radius_coeff must be positive values.")
    
    #TODO: Check the work on this equation one more time
    # Integral has an analytic solution (goes from depth == 0 to depth == current depth)
    area = 4/3 * PI_CONST/radius_coeff * ( (radius_coeff * depth + radius_coeff**2/4)**(3/2) - (radius_coeff**2/4)**(3/2) )

    return area

if __name__ == "__main__":
    # Add some testing here
    pass