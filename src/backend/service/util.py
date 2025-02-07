"""
Generic utility functions common across modules
"""

from enum import Enum

import boto3
from aws_lambda_powertools.logging import Logger
from botocore.exceptions import ClientError
from cachetools.func import ttl_cache
from botocore.config import Config

from .exceptions import ExternalServiceException, PermissionException

logger = Logger()


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
