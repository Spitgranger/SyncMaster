from http import HTTPStatus
from math import asin, cos, radians, sin, sqrt

from aws_lambda_powertools.event_handler import Response, content_types

from ..models.location_verification.location_request_response import LocationVerificationRequest


TARGET_LATITUDE = 43.2588581564085
TARGET_LONGITUDE = -79.92097591189501
ACCEPTABLE_RADIUS_METERS = 100

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth (in meters).
    """
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    distance = 6371000 * c  # Earth's radius in meters
    return distance


def verify_location(location_request: LocationVerificationRequest) -> bool:
    """
    Verify if provided coordinates are within a certain radius of the target point.
    """
    distance = haversine(
        location_request.latitude, location_request.longitude, TARGET_LATITUDE, TARGET_LONGITUDE
    )
    is_within_range = distance <= (ACCEPTABLE_RADIUS_METERS + location_request.accuracy)

    return is_within_range

