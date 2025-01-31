import boto3
import json
from botocore.exceptions import ClientError


cognito_client = boto3.client("cognito-idp")


def signup_user(body):
    """
    Sign up a new user into Cognito.
    """
    try:
        # Extract required fields from the request body
        user_pool_client_id = body.get("client_id")
        email = body.get("email")
        password = body.get("password")
        additional_attributes = body.get("attributes", {})  # Optional custom attributes

        if not user_pool_client_id or not email or not password:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {"message": "Missing required fields: client_id, email, password"}
                ),
            }

        # Format custom attributes
        attributes = [{"Name": "email", "Value": email}]
        for key, value in additional_attributes.items():
            attributes.append({"Name": key, "Value": value})

        # Call Cognito sign up API
        cognito_client.sign_up(
            ClientId=user_pool_client_id,
            Username=email,
            Password=password,
            UserAttributes=attributes,
        )

        return {"statusCode": 200, "body": json.dumps({"message": "User signed up successfully"})}

    except ClientError as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


def signin_user(body):
    """
    Sign in an existing user into Cognito and return JWT tokens.
    """
    try:
        # Extract required fields from the request body
        user_pool_client_id = body.get("client_id")
        email = body.get("email")
        password = body.get("password")

        if not user_pool_client_id or not email or not password:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {"message": "Missing required fields: client_id, email, password"}
                ),
            }

        # Call Cognito sign in API
        response = cognito_client.initiate_auth(
            ClientId=user_pool_client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": email, "PASSWORD": password},
        )

        # Extract tokens from the response
        tokens = response.get("AuthenticationResult", {})

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "AccessToken": tokens.get("AccessToken"),
                    "IdToken": tokens.get("IdToken"),
                    "RefreshToken": tokens.get("RefreshToken"),
                }
            ),
        }

    except ClientError as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
