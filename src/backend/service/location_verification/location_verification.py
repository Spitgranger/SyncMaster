from http import HTTPStatus
from math import asin, cos, radians, sin, sqrt

from aws_lambda_powertools.event_handler import Response, content_types

from ..environment import ACCEPTABLE_RADIUS_METERS, TARGET_LATITUDE, TARGET_LONGITUDE
from ..models.location_verification.location_request_response import LocationVerificationRequest


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


def verify_location(location_request: LocationVerificationRequest) -> Response:
    """
    Verify if provided coordinates are within a certain radius of the target point.
    """
    distance = haversine(
        location_request.latitude, location_request.longitude, TARGET_LATITUDE, TARGET_LONGITUDE
    )
    is_within_range = distance <= (ACCEPTABLE_RADIUS_METERS + location_request.accuracy)

    response_body = {"is_within_range": is_within_range}

    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=response_body,
    )

