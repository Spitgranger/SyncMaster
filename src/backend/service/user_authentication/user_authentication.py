"""
Module implementing operations relating to user authentication
"""

from http import HTTPStatus
from typing import Dict, List, Optional

import boto3
from aws_lambda_powertools.event_handler import Response, content_types
from aws_lambda_powertools.logging import Logger
from botocore.exceptions import ClientError

from ..environment import COGNITO_ACCESS_ROLE
from ..exceptions import (
    BadRequestException,
    ConflictException,
    ExternalServiceException,
    ForceChangePasswordException,
    ResourceNotFound,
    UnauthorizedException,
)
from ..location_verification.location_verification import verify_location
from ..models.user_authentication.user_request_response import (
    AdminSignupRequest,
    GetUsersByAttributeRequest,
    SigninRequest,
    SignupRequest,
    UpdateUserAttributeRequest,
)
from ..util import cors_headers, create_client_with_role

logger = Logger()


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

    def authenticate_user(self, username: str, password: str, new_password: Optional[str]) -> dict:
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
        logger.info(response)

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

    def get_user(self, access_token: str) -> dict:
        """
        Authenticate a user with their credentials
        :param access_token: The unexpired access token for the user
        :return: The respose from Cognito
        :raises ClientError Unable to process request for the given parameters
        """
        response = self._client.get_user(AccessToken=access_token)
        return response

    def sign_out(self, access_token: str) -> dict:
        """
        Invalidate all tokens issued by cognito to a user
        :param access_token: The unexpired access token for the user
        :return: The respose from Cognito
        :raises ClientError Unable to process request for the given parameters
        """
        response = self._client.global_sign_out(AccessToken=access_token)
        return response

    def signup_user(self, username: str, password: str, attributes: List[dict[str, str]]) -> dict:
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
        """
        Initialize a connection to Cognito with admin access
        :param clientid: The Cognito user pool client id
        :param user_pool_id: The Cognito user pool id for this connection
        :return: The AdminCognitoClient object
        :raises ExternalServiceException: Unable to connect to AWS Cognito
        """
        self._client = create_client_with_role(service_name="cognito-idp", role=COGNITO_ACCESS_ROLE)
        self._clientid = clientid
        self._user_pool_id = user_pool_id

    def admin_create_user(
        self, username: str, attributes: List[dict[str, str]], temp_password: Optional[str] = None
    ):
        """
        Create an user using the admin creation flow
        :param username:  The username of the user
        :param attributes: List of dictionaries containing the attributes of the
        :param temp_password: Used for testing, sets the users temporary
        password
        user
        :return: A list of matching user records
        """
        if temp_password:
            response = self._client.admin_create_user(
                UserPoolId=self._user_pool_id,
                Username=username,
                UserAttributes=attributes,
                TemporaryPassword=temp_password,
            )
        else:
            response = self._client.admin_create_user(
                UserPoolId=self._user_pool_id,
                Username=username,
                UserAttributes=attributes,
            )
        return response

    # This maybe useful in the future, keeping it commented out for Rev0
    #  def add_user_to_group(self, username: str, group_name: str):
    #      self._client.admin_add_user_to_group(
    #          UserPoolId=self._user_pool_id, Username=username, GroupName=group_name
    #      )

    def update_user_attributes(self, username: str, attributes: List[Dict[str, str]]) -> Dict:
        """
        Updates the user attributes for the given username
        :param attributes:  List of attributes stored as key value pairs in a
        dictionary
        :param username: The user to update the attributes for
        :return: A list of matching user records
        """
        response = self._client.admin_update_user_attributes(
            UserPoolId=self._user_pool_id, Username=username, UserAttributes=attributes
        )
        return response

    def get_users_by_attribute(self, attributes: Dict[str, str]) -> List[Dict]:
        """
        Retrieve all users from the user pool who have a specific attribute value.
        Will select users matching any of the given attributes
        :param attributes: a dictionary containing attributes to search for
        :return: A list of matching user records
        """
        users = []
        pagination_token: Optional[str] = None

        while True:
            params = {"UserPoolId": self._user_pool_id}
            if pagination_token:
                params["PaginationToken"] = pagination_token

            response = self._client.list_users(**params)
            # Right now the pagination is implemented within this method itself.
            # Might be worthwhile in the future to move to client side instead
            # when there are a large number of users to be returned
            for user in response.get("Users", []):
                user_attributes = {
                    attr["Name"]: attr["Value"] for attr in user.get("Attributes", [])
                }
                if (
                    any(user_attributes.get(k) == v for k, v in attributes.items())
                    or not attributes
                ):
                    users.append(user)

            pagination_token = response.get("PaginationToken")
            if not pagination_token:
                break

        return users


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
            headers=cors_headers,
            body=response_body,
        )

    except ClientError as err:
        logger.error(err)
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
        access_token = tokens.get("AccessToken")
        user = cognito_client.get_user(access_token)
        for attr in user.get("UserAttributes", {}):
            if attr["Name"] == "custom:role" and attr["Value"] == "contractor":
                if signin_request.location is None:
                    raise UnauthorizedException("Location not provided for contractor")
                if not verify_location(signin_request.location[0], signin_request.location[1], 10):
                    cognito_client.sign_out(access_token)
                    raise UnauthorizedException("User is not on site")

        response_body = {
            "AccessToken": tokens.get("AccessToken"),
            "IdToken": tokens.get("IdToken"),
            "RefreshToken": tokens.get("RefreshToken"),
        }
        return Response(
            status_code=HTTPStatus.OK.value,
            content_type=content_types.APPLICATION_JSON,
            headers=cors_headers,
            body=response_body,
        )
    except ClientError as err:
        logger.error(err)
        error_code = err.response["Error"]["Code"]
        match error_code:
            case "NotAuthorizedException":
                raise UnauthorizedException("Incorrect Credentials") from err
            case "UserNotFoundException":
                raise ResourceNotFound("user", "username") from err
            case _:
                raise ExternalServiceException from err


def logout_user_handler(user_access_token: str, cognito_client: CognitoClient) -> Response:
    """
    Invalidates Cognito tokens for the given user
    :param user_access_token: The body of the HTTP request
    :param cognito_client: The CognitoClient used to process the operation
    :return Response containg the result of the cognito operation
    """
    try:
        cognito_client.sign_out(user_access_token)

        return Response(
            status_code=HTTPStatus.NO_CONTENT.value,
            headers=cors_headers,
        )
    except ClientError as err:
        logger.error(err)
        error_code = err.response["Error"]["Code"]
        match error_code:
            case "NotAuthorizedException":
                raise BadRequestException("Invalid token") from err
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
            headers=cors_headers,
            body=response_body,
        )
    except ClientError as err:
        logger.error(err)
        error_code = err.response["Error"]["Code"]
        match error_code:
            case "UsernameExistsException":
                raise ConflictException("User with this username already exists") from err
            case _:
                raise ExternalServiceException from err


def admin_update_user_attributes_handler(
    update_user_request: UpdateUserAttributeRequest, cognito_client: AdminCognitoClient
):
    """
    Function to create a update a users attributes given the username
    :param update_user_request: The body of the HTTP request from API gateway
    :param cognito_client: The AdminCognitoClient used to process the operation
    :return Response containg the result of the cognito operation
    """
    try:
        cognito_client.update_user_attributes(
            update_user_request.email, update_user_request.attributes
        )

        return Response(
            status_code=HTTPStatus.NO_CONTENT.value,
            headers=cors_headers,
        )

    except ClientError as err:
        logger.error(err)
        error_code = err.response["Error"]["Code"]
        match error_code:
            case "UserNotFoundException":
                raise ResourceNotFound("user", "username") from err


def admin_get_users_handler(
    get_users_request: GetUsersByAttributeRequest, cognito_client: AdminCognitoClient
):
    """
    Function to get a list of users based on a given attribute
    :param get_users_request: The body of the HTTP request from API gateway
    :param cognito_client: The AdminCognitoClient used to process the operation
    :return Response containg the result of the cognito operation
    """
    user_array = cognito_client.get_users_by_attribute(get_users_request.attributes)

    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        headers=cors_headers,
        body=user_array,
    )
