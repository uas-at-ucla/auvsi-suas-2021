"""
Helper function module
"""

from typing import Tuple, Union


COORD_EPSILON = 0.000005
ALTITUDE_EPSILON = 1


def mps_to_kn(num):
    return num * 1.944


def m_to_ft(num):
    return num * 3.281


def kn_to_mps(num):
    return num / 1.944


def ft_to_m(num):
    return num / 3.281


def kn_to_ftps(num):
    return num * 1.68781


def compare_coords(
        coords1: Tuple[Union[float, None], Union[float, None]],
        coords2: Tuple[Union[float, None], Union[float, None]],
        epsilon: float = COORD_EPSILON) -> bool:
    """
    Compares two coordinates using an epsilon.
    Coordinates should be a tuple in the form (lat, lon)

    Parameters
    ----------
    coords1
        First set of coordinates.
    coords2
        Second set of coordinates.
    epsilon
        Specificed epsilon. If None, epsilon uses a default value

    Returns
    ----------
    Whether the two sets of coordinates are within an epsilon of each other.
    """

    lat_check = coords1[0] is None or coords2[0] is None or abs(
        coords1[0] - coords2[0]) <= epsilon
    lon_check = coords1[1] is None or coords2[1] is None or abs(
        coords1[1] - coords2[1]) <= epsilon
    return lat_check and lon_check


def compare_altitude(
        altitude1: Union[float, None],
        altitude2: Union[float, None],
        epsilon: float = ALTITUDE_EPSILON) -> bool:

    return altitude1 is None or altitude2 is None or abs(altitude1 - altitude2) <= epsilon


def compare_position(
        pos1: Tuple[Union[float, None], Union[float, None], Union[float, None]],
        pos2: Tuple[Union[float, None], Union[float, None], Union[float, None]],
        coord_epsilon: float = COORD_EPSILON,
        altitude_epsilon: float = ALTITUDE_EPSILON) -> bool:
    """
    Compares two positions using an epsilon.
    Positions should be a tuple in the form (lat, lon, alt)

    Parameters
    ----------
    coords1
        First position.
    coords2
        Second position.
    epsilon
        Specificed epsilon. If None, epsilon uses a default value

    Returns
    ----------
    Whether the two position are within an epsilon of each other.
    """

    return compare_coords((pos1[0], pos1[1]), (pos2[0], pos2[1]), coord_epsilon) and \
        compare_altitude(pos1[2], pos2[2], altitude_epsilon)


def draw_circle(cx: int, cy: int, r: int, resolution: float = 1):
    """Convert circle coords into a list of x and y values in that circle

    Args:
        cx (int): center x value
        cy (int): center y value
        r (int): radius of the circle

    Returns:
        Tuple[List[int], List[int]]: tuple of x and y (respectively) values
        that are within the circle
    """
    x_list = [] # list of x's in the circle
    y_list = [] # list of y's in the circle
    
    r2 = r*r # radius_squared
    for x in range(-r, r + resolution, resolution):
        for y in range(-r, r + resolution, resolution):
            distance = x*x + y*y    # distance to the center
            if (distance >= r2):
                continue

            x_list.append(cx + x)
            y_list.append(cy + y)
    
    return x_list, y_list


def draw_border(min_x, min_y, max_x, max_y, resolution=1):
    if (min_x > max_x):
        return draw_border(max_x, min_y, min_x, max_y, resolution)
    if (min_y > max_y):
        return draw_border(min_x, max_y, max_x, min_y, resolution)
    
    x_list = []
    y_list = []
    
    for x in range(min_x, max_x + resolution, resolution):
        x_list.append(x)
        y_list.append(min_y)
        
        x_list.append(x)
        y_list.append(max_y)
        
    for y in range(min_y, max_y + resolution, resolution):
        x_list.append(min_x)
        y_list.append(y)
        
        x_list.append(max_x)
        y_list.append(y)
    
    return x_list, y_list

def draw_line(min_x, min_y, max_x, max_y, resolution=1):
    if (min_x > max_x):
        return draw_border(max_x, min_y, min_x, max_y, resolution)
    if (min_y > max_y):
        return draw_border(min_x, max_y, max_x, min_y, resolution)
    
    x_list = []
    y_list = []
    
    dx = max_x - min_x
    dy = max_y - min_y
    
    for x in range(min_x, max_x + resolution, resolution):
        y = min_y + dy * (x - min_x) / dx
        x_list.append(x)
        y_list.append(y)        
        
# Utility function for scaling one coordinate system to another coordinate system
def scale_coords(x, y, prev_width, prev_height, new_width, new_height):
    return (x / prev_width * new_width, y / prev_height * new_height)