"""
Unprotected routes associated with authentication
"""

from http import HTTPStatus

from aws_lambda_powertools.event_handler import content_types
from aws_lambda_powertools.event_handler.api_gateway import Router
from aws_lambda_powertools.event_handler.openapi.params import Body
from typing_extensions import Annotated

from ...database.db_table import DBTable
from ...environment import USER_POOL_CLIENT_ID
from ...models.api.user_requests import APIUserRequest
from ...models.db.user_request import DBUserRequest
from ...models.user_authentication.user_request_response import SigninRequest
from ...user_authentication.user_authentication import CognitoClient, signin_user_handler
from ...user_requests.user_requests import create_user_request
from ...util import AWSAccessLevel, create_http_response, time_epoch_to_datetime

router = Router()


@router.post("/signin")
def signin_handler(body: Annotated[SigninRequest, Body()]):
    """
    Route to signup a new user
    :param body: The body of the HTTP request
    :return: dictionary containing http response
    """
    cognito_client = CognitoClient(USER_POOL_CLIENT_ID)
    return signin_user_handler(body, cognito_client)


@router.post("/create-request")
def create_user_request_handler(body: Annotated[APIUserRequest, Body()]):
    """
    Route to create a signup request for a new user
    :param body: The body of the HTTP request
    :return: dictionary containing http response
    """
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBUserRequest)
    request_time = time_epoch_to_datetime(
        router.current_event["requestContext"]["requestTimeEpoch"]
    )
    response_body = create_user_request(
        table=table,
        email=body.email,
        requested_role=body.role_requested,
        company=body.company,
        name=body.name,
        time=request_time,
    )
    return create_http_response(
        status_code=HTTPStatus.CREATED.value,
        content_type=content_types.APPLICATION_JSON,
        body=response_body.to_api_model(),
    )
