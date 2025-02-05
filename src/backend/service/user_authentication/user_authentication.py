"""
Module implementing operations relating to user authentication
"""

from http import HTTPStatus
from typing import List, Optional

import boto3
from aws_lambda_powertools.event_handler import Response, content_types
from botocore.exceptions import ClientError

from ..models.user_authentication.user_request_response import (
    AdminSignupRequest,
    SigninRequest,
    SignupRequest,
)
from ..util import create_client_with_role
from ..environment import COGNITO_ACCESS_ROLE

from ..exceptions import (
    ForceChangePasswordException,
    ResourceNotFound,
    UnauthorizedException,
    ExternalServiceException,
    BadRequestException,
    ConflictException,
)


class CognitoClient:
    """
    Wrapper class for AWS cognito providing an interface for our desired
    operations
    """

    def __init__(self, clientid: str):
        """
        Initialize a connection to Cognito
        :param clientid: The Cognito user pool client id
        :return: The CognitoClient object
        :raises ExternalServiceException: Unable to connect to AWS Cognito
        """
        self._client = boto3.client("cognito-idp")
        self._clientid = clientid

    def authenticate_user(self, username: str, password: str, new_password: Optional[str]):
        """
        Authenticate a user with their credentials
        :param username: The Cognito username (aliased to email)
        :param password: The users password
        :param new_password: Optional field for users in a force change password
        state
        :return: The respose from Cognito
        :raises ClientError Unable to process request for the given parameters
        """
        response = self._client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": username, "PASSWORD": password},
            ClientId=self._clientid,
        )

        # Check if the user is in "NEW_PASSWORD_REQUIRED" state, admin auth flow
        # requires users to change their assigned one time password
        if response.get("ChallengeName") == "NEW_PASSWORD_REQUIRED":
            if not new_password:
                raise ForceChangePasswordException()

            response = self._client.respond_to_auth_challenge(
                ClientId=self._clientid,
                ChallengeName="NEW_PASSWORD_REQUIRED",
                Session=response["Session"],  # Use the same session from previous response
                ChallengeResponses={
                    "USERNAME": username,
                    "NEW_PASSWORD": new_password,
                },
            )

        return response

    def signup_user(self, username: str, password: str, attributes: List[dict[str, str]]):
        """
        Sign up a user to Cognito
        :param username: The Cognito username (aliased to email)
        :param password: The users password
        :param attributes: The additional attributes for the user
        :return: The respose from Cognito
        :raises ClientError Unable to process request for the given parameters
        """
        response = self._client.sign_up(
            ClientId=self._clientid,
            Username=username,
            Password=password,
            UserAttributes=attributes,
        )
        return response


class AdminCognitoClient:
    """
    Wrapper class for AWS Cognito providing an interface for admin cognito
    operations
    """

    def __init__(self, clientid: str, user_pool_id: str):
        self._client = create_client_with_role(service_name="cognito-idp", role=COGNITO_ACCESS_ROLE)
        self._clientid = clientid
        self._user_pool_id = user_pool_id

    def admin_create_user(self, username: str, attributes: List[dict[str, str]]):
        response = self._client.admin_create_user(
            UserPoolId=self._user_pool_id,
            Username=username,
            UserAttributes=attributes,
        )
        return response

    def add_user_to_group(self, username: str, group_name: str):
        self._client.admin_add_user_to_group(
            UserPoolId=self._user_pool_id, Username=username, GroupName=group_name
        )

    def update_user_attributes(self, username: str, attributes: List[dict[str, str]]):
        self._client.admin_update_user_attributes(
            UserPoolId=self._user_pool_id, Username=username, UserAttributes=attributes
        )


def signup_user_handler(signup_request: SignupRequest, cognito_client: CognitoClient) -> Response:
    """
    Lambda handler to sign up a new user into Cognito
    :param signup_request: SignupRequest object of the HTTP request body
    :param cognito_client: The CognitoClient used to process the operation
    :return: HTTP Response of the request
    """
    try:
        attributes = [{"Name": "email", "Value": signup_request.email}]
        for key, value in signup_request.attributes.items():
            attributes.append({"Name": key, "Value": value})

        response_body = cognito_client.signup_user(
            signup_request.email, signup_request.password, attributes
        )

        return Response(
            status_code=HTTPStatus.CREATED.value,
            content_type=content_types.APPLICATION_JSON,
            body=response_body,
        )

    except ClientError as err:
        error_code = err.response["Error"]["Code"]
        match error_code:
            case "UsernameExistsException":
                raise ConflictException("User with this username already exists") from err
            case "InvalidPasswordException":
                raise BadRequestException(
                    "Password does not meet organization policy requirements"
                ) from err
            case _:
                raise ExternalServiceException from err


def signin_user_handler(signin_request: SigninRequest, cognito_client: CognitoClient) -> Response:
    """
    Sign in an existing user into Cognito and return JWT tokens.
    :param signin_request: The body of the HTTP request from API gateway
    :param cognito_client: The CognitoClient used to process the operation
    :return Response containg the result of the cognito operation, if successful
    return the AccessToken, IdToken, and RefreshToken
    """
    try:
        response = cognito_client.authenticate_user(
            signin_request.email, signin_request.password, signin_request.new_password
        )

        # Extract tokens from the response
        tokens = response.get("AuthenticationResult", {})

        response_body = {
            "AccessToken": tokens.get("AccessToken"),
            "IdToken": tokens.get("IdToken"),
            "RefreshToken": tokens.get("RefreshToken"),
        }
        return Response(
            status_code=HTTPStatus.OK.value,
            content_type=content_types.APPLICATION_JSON,
            body=response_body,
        )
    except ClientError as err:
        error_code = err.response["Error"]["Code"]
        match error_code:
            case "NotAuthorizedException":
                raise UnauthorizedException("Incorrect Credentials") from err
            case "UserNotFoundException":
                raise ResourceNotFound("user", "username") from err
            case _:
                raise ExternalServiceException from err


def admin_create_user_handler(
    create_user_request: AdminSignupRequest, cognito_client: AdminCognitoClient
) -> Response:
    """
    Function to create a user using admin create user flow
    :param create_user_request: The body of the HTTP request from API gateway
    :param cognito_client: The AdminCognitoClient used to process the operation
    :return Response containg the result of the cognito operation
    """
    try:
        attributes = [{"Name": "email", "Value": create_user_request.email}]
        for key, value in create_user_request.attributes.items():
            attributes.append({"Name": key, "Value": value})

        response_body = cognito_client.admin_create_user(create_user_request.email, attributes)

        return Response(
            status_code=HTTPStatus.CREATED.value,
            content_type=content_types.APPLICATION_JSON,
            body=response_body,
        )
    except ClientError as err:
        error_code = err.response["Error"]["Code"]
        match error_code:
            case "UsernameExistsException":
                raise ConflictException("User with this username already exists") from err
            case _:
                raise ExternalServiceException from err
