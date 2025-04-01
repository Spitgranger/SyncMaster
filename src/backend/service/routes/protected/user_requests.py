"""
Protected routes associated with user requests
"""

from http import HTTPStatus
from typing import Optional

from aws_lambda_powertools.event_handler import content_types
from aws_lambda_powertools.event_handler.api_gateway import Router
from aws_lambda_powertools.event_handler.openapi.params import Body, Query
from typing_extensions import Annotated

from ...database.db_table import DBTable
from ...environment import USER_POOL_CLIENT_ID, USER_POOL_ID
from ...models.api.user_requests import (
    APIActionUserRequest,
    APIGetUserRequestsResponse,
)
from ...models.db.user_request import DBUserRequest
from ...user_authentication.user_authentication import AdminCognitoClient
from ...user_requests.user_requests import action_user_request, get_user_requests
from ...util import (
    AWSAccessLevel,
    UserType,
    create_http_response,
    create_open_api_error_response,
    create_open_api_response,
    decode_db_key,
    encode_db_key,
    verify_user_role,
)

router = Router()


@router.get(
    "/get-requests",
    security=[{"bearer": [UserType.ADMIN.value, UserType.EMPLOYEE.value]}],
    responses={
        200: create_open_api_response(
            description="List of all user requests", response_body_schema=APIGetUserRequestsResponse
        )
    },
)
def get_user_requests_handler(
    limit: Annotated[Optional[int], Query(le=100)] = None,
    start_key: Annotated[Optional[str], Query()] = None,
):
    """
    Route to get all user requests that need to be approved
    :param limit: The maximum number of requests to return as query string
    :param start_key: The key to start the query from as query string
    :return: dictionary containing http response
    """

    verify_user_role(
        user_groups=router.current_event["requestContext"]["authorizer"]["claims"][
            "cognito:groups"
        ],
        acceptable_roles=[UserType.ADMIN, UserType.EMPLOYEE],
        action="get user requests",
    )

    decoded_key = decode_db_key(key=start_key) if start_key else None

    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBUserRequest)
    user_requests, last_eval_key = get_user_requests(
        table=table, limit=limit, start_key=decoded_key
    )
    encoded_key = encode_db_key(key=last_eval_key) if last_eval_key else None

    response_body = APIGetUserRequestsResponse(
        requests=[request.to_api_model() for request in user_requests], last_key=encoded_key
    )

    return create_http_response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=response_body,
    )


@router.post(
    "/action-request",
    security=[{"bearer": [UserType.ADMIN.value]}],
    responses={
        201: create_open_api_response(description="Created User", response_body_schema={}),
        204: create_open_api_response(
            description="User Successfully Rejected, No content", response_body_schema={}
        ),
        404: create_open_api_error_response(
            description="User request does not exist",
        ),
        409: create_open_api_error_response(
            description="User with the same email as request already exists",
        ),
    },
)
def action_user_request_handler(body: Annotated[APIActionUserRequest, Body()]):
    """
    Route to action a user request
    :param body: The body of the HTTP request
    :return: dictionary containing http response
    """
    verify_user_role(
        user_groups=router.current_event["requestContext"]["authorizer"]["claims"][
            "cognito:groups"
        ],
        acceptable_roles=[UserType.ADMIN],
        action="action user requests",
    )

    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBUserRequest)

    response_body = action_user_request(
        cognito_client=AdminCognitoClient(user_pool_id=USER_POOL_ID, clientid=USER_POOL_CLIENT_ID),
        table=table,
        email=body.email,
        action=body.action,
    )
    if not response_body:
        return create_http_response(
            status_code=HTTPStatus.NO_CONTENT.value,
        )
    return create_http_response(
        status_code=HTTPStatus.CREATED.value,
        content_type=content_types.APPLICATION_JSON,
        body=response_body,
    )
