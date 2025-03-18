"""
Main lambda handler for all API Gateway events
"""

from http import HTTPStatus

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response, content_types
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

from .exceptions import HTTPError
from .routes.protected import documents, site_visits, users
from .routes.unprotected import auth
from .util import CORS_HEADERS

logger = Logger()
app = APIGatewayRestResolver(enable_validation=True)
app.include_router(router=site_visits.router, prefix="/protected/site")
app.include_router(router=users.router, prefix="/protected/users")
app.include_router(router=documents.router, prefix="/protected/documents")
app.include_router(router=auth.router, prefix="/unprotected/auth")


@app.exception_handler(Exception)
def exception_handler(exception: Exception):
    """
    Exception handler for all exceptions generated on invocation of this router

    :param exception: The exception caught
    :return: Response containing the correct HTTP code and message of exception
    """
    logger.error(exception)
    error_message = str(exception) or repr(exception) or "Unknown error"
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
    content_type = content_types.APPLICATION_JSON
    body = {"error": str(exception)}
    if isinstance(exception, HTTPError):
        status_code = exception.http_code.value
        content_type = content_types.APPLICATION_JSON
        body = {"error": error_message}

    return Response(
        status_code=status_code, content_type=content_type, body=body, headers=CORS_HEADERS
    )


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """
    Main lambda handler for all API Gateway events. Handles routing of requests.

    :param event: The API Gateway event coming from AWS.
    :param context: The lambda context coming from AWS.
    :return: The response determined be the application.
    """
    return app.resolve(event, context)
