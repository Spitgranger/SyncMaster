"""
Temporary route for initial setup
"""

from aws_lambda_powertools.event_handler.api_gateway import Router
from aws_lambda_powertools.event_handler.openapi.params import Body
from typing_extensions import Annotated
from ..location_verification.location_verification import verify_location
from ..models.location_verification.location_request_response import LocationVerificationRequest

router = Router()


@router.get("/test")
def thingy() -> dict:
    """
    Dummy route for use in initial project structure setup. Can be removed later.

    :return: dummy dict.
    """
    return {"Hello": "World"}

@router.post("/verify-location")
def verify_location_handler(body: Annotated[LocationVerificationRequest, Body()]) -> dict:
    """
    Route to verify user location
    """
    return verify_location(body)
