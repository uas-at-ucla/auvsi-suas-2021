"""
Helper function module
"""

from typing import Tuple, Union


COORD_EPSILON = 0.000001
ALTITUDE_EPSILON = 0.1


def compare_coords(
    coords1: Tuple[Union[float, None], Union[float, None]],
    coords2: Tuple[Union[float, None], Union[float, None]],
    epsilon: float=COORD_EPSILON) -> bool:

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

    lat_check = coords1[0] is None or coords2[0] is None or abs(coords1[0] - coords2[0]) <= epsilon
    lon_check = coords1[1] is None or coords2[1] is None or abs(coords1[1] - coords2[1]) <= epsilon
    return lat_check and lon_check


def compare_altitude(
    altitude1: Union[float, None],
    altitude2: Union[float, None],
    epsilon: float=ALTITUDE_EPSILON) -> bool:

    return altitude1 is None or altitude2 is None or abs(altitude1 - altitude2) <= epsilon


def compare_position(
    pos1: Tuple[Union[float, None], Union[float, None], Union[float, None]],
    pos2: Tuple[Union[float, None], Union[float, None], Union[float, None]],
    coord_epsilon: float=COORD_EPSILON,
    altitude_epsilon: float=ALTITUDE_EPSILON) -> bool:

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
