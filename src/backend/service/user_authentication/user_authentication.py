"""
Module implementing operations relating to user authentication
"""

from http import HTTPStatus
from typing import List

import boto3
from aws_lambda_powertools.event_handler import Response, content_types
from botocore.exceptions import ClientError

from ..models.user_authentication.user_request_response import SigninRequest, SignupRequest


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

    def authenticate_user(self, username: str, password: str):
        """
        Authenticate a user with their credentials
        :param username: The Cognito username (aliased to email)
        :param password: The users password
        :return: The respose from Cognito
        :raises ClientError Unable to process request for the given parameters
        """
        response = self._client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": username, "PASSWORD": password},
            ClientId=self._clientid,
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
                status_code = HTTPStatus.CONFLICT.value
            case "InvalidPasswordException":
                status_code = HTTPStatus.BAD_REQUEST.value
            case _:
                status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return Response(
            status_code=status_code,
            content_type=content_types.APPLICATION_JSON,
            body={"error": f"An unexpected error occurred {str(err)}"},
        )


def signin_user_handler(signin_request: SigninRequest, cognito_client: CognitoClient) -> Response:
    """
    Sign in an existing user into Cognito and return JWT tokens.
    :param signin_request: The body of the HTTP request from API gateway
    :param cognito_client: The CognitoClient used to process the operation
    :return Response containg the result of the cognito operation, if successful
    return the AccessToken, IdToken, and RefreshToken
    """
    try:
        response = cognito_client.authenticate_user(signin_request.email, signin_request.password)

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
                status_code = HTTPStatus.UNAUTHORIZED.value
            case "UserNotFoundException":
                status_code = HTTPStatus.NOT_FOUND.value
            case _:
                status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return Response(
            status_code=status_code,
            content_type=content_types.APPLICATION_JSON,
            body={"error": f"An unexpected error occurred {str(err)}"},
        )
