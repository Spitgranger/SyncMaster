"""
Generic utility functions common across modules
"""

import base64
import json
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

import boto3
from aws_lambda_powertools.event_handler import Response
from aws_lambda_powertools.event_handler.openapi.types import (
    OpenAPIResponse,
    OpenAPIResponseContentModel,
    OpenAPIResponseContentSchema,
)
from aws_lambda_powertools.logging import Logger
from botocore.config import Config
from botocore.exceptions import ClientError
from cachetools.func import ttl_cache
from pydantic import BaseModel

from .exceptions import (
    ExternalServiceException,
    InsufficientUserPermissionException,
    PermissionException,
)
from .models.custom_base_model import CustomBaseModel

logger = Logger()

CORS_HEADERS = {
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, PUT, PATCH, DELETE",
}


class AWSAccessLevel(Enum):
    """
    Enum of access levels for AWS resources
    """

    WRITE = "write"
    # Access to read and write to the specified resource

    READ = "read"
    # Read-only access to the specified resource


class ItemType(Enum):
    """
    Enum of different types of items stored by the application
    """

    DOCUMENT = "document"
    SITE_VISIT = "site_visit"
    SITE = "site"
    USER_REQUEST = "user_request"


class UserRequestAction(Enum):
    """
    Enum of different actions that can be taken on a user request
    """

    APPROVE = "approve"
    REJECT = "reject"


class FileType(Enum):
    """
    Enum of the different types of documents stored in the system
    """

    FILE = "file"
    FOLDER = "folder"


class UserType(Enum):
    """
    Enum of the different types of user roles in the system
    """

    EMPLOYEE = "employee"
    CONTRACTOR = "contractor"
    ADMIN = "admin"


@ttl_cache(maxsize=16, ttl=15 * 60)
def create_client_with_role(service_name: str, role: str):
    """
    Creates a boto3 client for the provided service, with the given role

    :param service_name: The service that this client should interact with,
        takes the same values as a boto3 client
    :param role: The role for this client to assume
    :raises PermissionException: The lambda does not have permission to assume
        the provided role
    :raises ExternalServiceException: Unable to connect to AWS
    :return: The boto3 client for the given service, with the provided credentials
    """
    try:
        assumed_role_object: dict = boto3.client("sts").assume_role(
            RoleArn=role, RoleSessionName="SyncMasterRoleSession", DurationSeconds=30 * 60
        )

        creds: dict = assumed_role_object["Credentials"]

        return boto3.client(
            service_name,
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
            config=Config(signature_version="s3v4", region_name="us-east-2"),
        )
    except ClientError as err:
        logger.exception(err)
        if err.response["Error"]["Code"] == "AccessDenied":
            raise PermissionException("Insufficient permissions to assume role") from err
        raise ExternalServiceException("Unknown Error from AWS") from err


@ttl_cache(maxsize=16, ttl=15 * 60)
def create_resource_with_role(service_name: str, role: str):
    """
    Creates a boto3 resource, with the given role

    :param service_name: The service that this client should interact with,
        takes the same values as a boto3 resource
    :param role: The role for this resource to assume
    :raises PermissionException: The lambda does not have permission to assume
        the provided role
    :raises ExternalServiceException: Unable to connect to AWS
    :return: The boto3 resource for the given service, with the provided credentials
    """
    try:
        assumed_role_object: dict = boto3.client("sts").assume_role(
            RoleArn=role, RoleSessionName="SyncMasterRoleSession", DurationSeconds=30 * 60
        )

        creds: dict = assumed_role_object["Credentials"]

        return boto3.resource(
            service_name,
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
        )
    except ClientError as err:
        logger.exception(err)
        if err.response["Error"]["Code"] == "AccessDenied":
            raise PermissionException("Insufficient permissions to assume role") from err
        raise ExternalServiceException("Unknown Error from AWS") from err


def decode_db_key(key: str) -> dict:
    """
    Decodes an encoded dynamodb key

    :param key: The encoded dynamodb key
    :return: The decoded dynamodb key
    """
    key_str = base64.urlsafe_b64decode(key.encode("utf-8")).decode("utf-8")
    return json.loads(key_str)


def encode_db_key(key: dict) -> str:
    """
    Encodes a dynamodb key, to be returned in an API, and used in queries

    :param key: The dynamodb key
    :return: The encoded dynamodb key
    """
    key_bytes = json.dumps(key).encode("utf-8")
    return base64.urlsafe_b64encode(key_bytes).decode("utf-8")


def create_http_response(
    status_code: int,
    content_type: Optional[str] = None,
    headers: Optional[dict] = None,
    body: Optional[str | CustomBaseModel | dict] = None,
) -> Response:
    """
    Function to create a Response object for the API Gateway
    :param status_code: The status code of the response
    :param content_type: The content type of the response
    :param headers: The headers to include in the response
    :param body: The body of the response
    :return: The Response object to be returned to the API Gateway
    """
    if headers is None:
        headers = CORS_HEADERS
    return Response(
        status_code=status_code,
        content_type=content_type,
        body=body,
        headers=headers,
    )


def time_epoch_to_datetime(time_epoch: int) -> datetime:
    """
    From time epoch given in api gateway request, create a datetime object

    :param time_epoch: The time epoch to convert into a datetime
    :return: The datetime representing the time epoch
    """
    return datetime.fromtimestamp(time_epoch / 1000, tz=timezone.utc)


def verify_user_role(user_groups: list[str], acceptable_roles: list[UserType], action: str) -> None:
    """
    Verify the users groups fall under the list of acceptable groups for the action
    they want to perform

    :param user_groups: The user groups the user beolngs to
    :param acceptable_roles: The roles that are allowed to perform the given action
    :param action: The action being performed
    :raises InsufficientUserPermissionException: If user cannot perform the given action
    """
    allowed_access = False

    for role in acceptable_roles:
        if role.value in user_groups:
            allowed_access = True

    if not allowed_access:
        raise InsufficientUserPermissionException(roles=user_groups, action=action)


def create_open_api_response(
    description: str, response_body_schema: dict | type[BaseModel]
) -> OpenAPIResponse:
    """
    Gives the openapi response appropriate for the API docs

    :param description: description of response content
    :param response_body_schema: schema of response body
    :return: The open api response schema appropriate for the swagger docs
    """
    content_schema = (
        OpenAPIResponseContentModel(model=response_body_schema)
        if isinstance(response_body_schema, type)
        else OpenAPIResponseContentSchema(schema=response_body_schema)
    )
    return OpenAPIResponse(description=description, content={"application/json": content_schema})


class ErrorResponse(BaseModel):
    """Model representing API error response"""

    error: str


def create_open_api_error_response(description: str) -> OpenAPIResponse:
    """
    Gives the openapi error response appropriate for the API docs

    :param description: description of error response content
    :return: The open api response schema appropriate for the swagger docs
    """
    content_schema = OpenAPIResponseContentModel(model=ErrorResponse)
    return OpenAPIResponse(description=description, content={"application/json": content_schema})
