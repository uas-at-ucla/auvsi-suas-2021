"""
Helper function module
"""

from typing import Tuple, Union
import math

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


def get_bearing(lat0, lon0, lat1, lon1):
    dlon = lon1 - lon0
    x = math.sin(dlon) * math.cos(lat1)
    y = math.cos(lat0) * math.sin(lat1) - \
        math.sin(lat0) * math.sin(lat1) * math.cos(dlon)
    bearing = math.atan2(x, y)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360
    return bearing

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


def draw_circle(cx: int, cy: int, r: int, resolution: float = 1, min_x = 0, min_y = 0, 
              max_x = 1000, max_y = 1000):
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
            if (min_x <= cx + x <= max_x and min_y <= cy + y <= max_y):
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

def draw_line(x0, y0, x1, y1, thickness = 5, 
              min_x = 0, min_y = 0, 
              max_x = 1000, max_y = 1000):
    x_list = []
    y_list = []
    
    dx = x1 - x0
    dy = y1 - y0
    
    distance = math.ceil(math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2))
    
    for i in range(distance):
        t = i/distance
        x = round(x0 + dx * t)
        y = round(y0 + dy * t)
        
        # if (i > 0 and abs(x - x_list[-1]) == 1 and abs(y - y_list[-1]) == 1):
        #     tx = x - x_list[-1]
        #     ty = y - y_list[-1]
            
        #     x_list.append(x - tx)
        #     y_list.append(y)
            
        #     x_list.append(x)
        #     y_list.append(y - ty)
        
        r2 = thickness * thickness
        for i in range(max(min_x, x-thickness), min(max_x, x+thickness)+1):
            for j in range(max(min_y, y-thickness), min(max_y, y+thickness)+1):
                d_x = (i - x)
                d_y = (j - y)
                d = d_x * d_x + d_y * d_y
                if (d < r2):
                    x_list.append(i)
                    y_list.append(j)
            
        # x_list.append(x)
        # y_list.append(y)
    
    return x_list, y_list
        
# Utility function for scaling one coordinate system to another coordinate system
def scale_coords(x, y, prev_width, prev_height, new_width, new_height):
    return (x / prev_width * new_width, y / prev_height * new_height)