"""
Temporary route for initial setup
"""

from aws_lambda_powertools.event_handler.api_gateway import Router

router = Router()


@router.get("/test")
def thingy() -> dict:
    """
    Dummy route for use in initial project structure setup. Can be removed later.

    :return: dummy dict.
    """
    return {"Hello": "World"}
