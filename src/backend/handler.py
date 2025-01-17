"""
Main lambda handler for all API Gateway events
"""

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

from .routes import temp

logger = Logger()
app = APIGatewayRestResolver()
app.include_router(router=temp.router)


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """
    Main lambda handler for all API Gateway events. Handles routing of requests.

    :param event: The API Gateway event coming from AWS.
    :param context: The lambda context coming from AWS.
    :return: The response determined be the application.
    """
    return app.resolve(event, context)
