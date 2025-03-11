"""
Module for verifying a user's location
"""

from math import asin, cos, radians, sin, sqrt

from ..database.db_table import DBTable
from ..models.db.site import DBSite
from ..site_management.site_management import get_site
from ..util import AWSAccessLevel


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth in meters.

    :param lat1: latitude for location 1
    :param lon1: longitude for location 1
    :param lat2: latititude for location 2
    :param lon2: longitude for location 2
    :return: the distance between two locations in meters
    """
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    distance = 6371000 * c  # Earth's radius in meters
    return distance


def verify_location(latitude: float, longitude: float, accuracy: float, site_id: str) -> bool:
    """
    Verify if provided coordinates are within a certain radius of the target point.

    :param latitude: latitude of user location
    :param longitude: longitude of user location
    :param accuracy: accuracy of user location in meters
    :return: boolean for if a location is within range of the desired site
    """
    site = get_site(table=DBTable(access=AWSAccessLevel.READ, item_schema=DBSite), site_id=site_id)
    distance = haversine(latitude, longitude, float(site.latitude), float(site.longitude))
    is_within_range = distance <= (float(site.acceptable_range) + accuracy)

    return is_within_range
