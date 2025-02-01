import boto3
import json
from http import HTTPStatus
from botocore.exceptions import ClientError
from ..models.user_authentication.user_request_response import SignupRequest, SigninRequest
from aws_lambda_powertools.event_handler import Response, content_types
from service.environment import USER_POOL_CLIENT_ID

cognito_client = boto3.client("cognito-idp")


def signup_user(signup_request: SignupRequest) -> dict:
    """
    Sign up a new user into Cognito.
    """
    try:
        # Format custom attributes
        attributes = [{"Name": "email", "Value": signup_request.email}]
        for key, value in signup_request.attributes.items():
            attributes.append({"Name": key, "Value": value})
        print(attributes)

        # Call Cognito sign up API
        cognito_client.sign_up(
            ClientId=USER_POOL_CLIENT_ID,
            Username=signup_request.email,
            Password=signup_request.password,
            UserAttributes=attributes,
        )

        response_body = {"message": "User successfully created"}

        return Response(
            status_code=HTTPStatus.CREATED.value,
            content_type=content_types.APPLICATION_JSON,
            body=response_body,
        )

    except ClientError as e:
        return Response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            content_type=content_types.APPLICATION_JSON,
            body={"error": str(e)},
        )


def signin_user(signin_request: SigninRequest):
    """
    Sign in an existing user into Cognito and return JWT tokens.
    """
    try:
        # Call Cognito sign in API
        response = cognito_client.initiate_auth(
            ClientId=USER_POOL_CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": signin_request.email, "PASSWORD": signin_request.password},
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

    except ClientError as e:
        return Response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            content_type=content_types.APPLICATION_JSON,
            body={"error": str(e)},
        )
