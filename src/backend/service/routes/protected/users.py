"""
Routes to associated with user management and authentication
"""

from aws_lambda_powertools.event_handler.api_gateway import Router
from aws_lambda_powertools.event_handler.openapi.params import Body, Query
from typing_extensions import Annotated

from ...environment import USER_POOL_CLIENT_ID, USER_POOL_ID
from ...models.user_authentication.user_request_response import (
    AdminSignupRequest,
    GetUsersByAttributeRequest,
    SignupRequest,
    UpdateUserAttributeRequest,
)
from ...user_authentication.user_authentication import (
    AdminCognitoClient,
    CognitoClient,
    admin_create_user_handler,
    admin_get_users_handler,
    admin_update_user_attributes_handler,
    logout_user_handler,
    signup_user_handler,
)

router = Router()


@router.post("/signup")
def signup_handler(body: Annotated[SignupRequest, Body()]):
    """
    Route to signup a new user
    :param body: The body of the HTTP request
    :return: dictionary containing http response
    """
    cognito_client = CognitoClient(USER_POOL_CLIENT_ID)
    return signup_user_handler(body, cognito_client)


@router.post("/create_user")
def create_user_handler(body: Annotated[AdminSignupRequest, Body()]):
    """
    Route to signup a new user
    :param body: The body of the HTTP request
    :return: dictionary containing http response
    """
    cognito_client = AdminCognitoClient(USER_POOL_CLIENT_ID, USER_POOL_ID)

    return admin_create_user_handler(body, cognito_client)


@router.get("/signout")
def signout_handler(user_token: Annotated[str, Query()]):
    """
    Route to signout a new user
    :param user_token: Access token of the user to signout
    :return: dictionary containing http response
    """
    cognito_client = CognitoClient(USER_POOL_CLIENT_ID)
    return logout_user_handler(user_token, cognito_client)


@router.post("/update_user")
def update_user_handler(body: Annotated[UpdateUserAttributeRequest, Body()]):
    """
    Route to signup a new user
    :param body: The body of the HTTP request
    :return: dictionary containing http response
    """
    cognito_client = AdminCognitoClient(USER_POOL_CLIENT_ID, USER_POOL_ID)

    return admin_update_user_attributes_handler(body, cognito_client)


@router.post("/get_users")
def get_users_handler(body: Annotated[GetUsersByAttributeRequest, Body()]):
    """
    Route to get a list of users based on provided attributes
    :param body: The body of the HTTP request
    :return: dictionary containing http response
    """
    cognito_client = AdminCognitoClient(USER_POOL_CLIENT_ID, USER_POOL_ID)

    return admin_get_users_handler(body, cognito_client)
