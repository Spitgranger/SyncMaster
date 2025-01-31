"""
Temporary route for initial setup
"""

from aws_lambda_powertools.event_handler.api_gateway import Router
import json
from ..user_authentication.user_authentication import signup_user, signin_user

router = Router()


@router.get("/test")
def thingy() -> dict:
    """
    Dummy route for use in initial project structure setup. Can be removed later.

    :return: dummy dict.
    """
    return {"Hello": "World"}


@router.post("/signup")
def signup_handler():
    event = router.current_event
    # Extract HTTP method and path from the event
    body = json.loads(event.get("body", "{}"))

    return signup_user(body)


@router.post("/signin")
def signin_handler():
    event = router.current_event
    # Extract HTTP method and path from the event
    body = json.loads(event.get("body", "{}"))

    return signin_user(body)
