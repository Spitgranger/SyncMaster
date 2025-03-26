"""Module contating functions to interact with user requests in the database"""

from datetime import datetime
from typing import Optional

from aws_lambda_powertools.logging import Logger
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError

from ..database.db_table import DBTable, KeySchema
from ..exceptions import (
    ConditionCheckFailed,
    ConflictException,
    ExternalServiceException,
    ResourceConflict,
)
from ..models.db.user_request import DBUserRequest
from ..user_authentication.user_authentication import AdminCognitoClient
from ..util import ItemType, UserRequestAction

logger = Logger()


def create_user_request(
    table: DBTable[DBUserRequest],
    email: str,
    requested_role: str,
    company: str,
    name: str,
    time: datetime,
) -> DBUserRequest:
    """
    Create a new user request with the given parameters

    :param table: The DBTable object to use to access the database. Requires write access
    :param email: The email of the user who is requesting a new role
    :param requested_role: The role the user is requesting
    :param company: The company the user is associated with
    :param name: The name of the user
    :param time: The time the request was made
    :raises ExternalServiceException: An unexpected error occurs in AWS
    :raises ResourceConflict: A user request with the same email and request id already exists
    """
    user_request = DBUserRequest(
        email=email,
        company=company,
        role_requested=requested_role,
        name=name,
        last_modified_time=time,
        last_modified_by="system",
    )

    condition = Attr("pk").not_exists() & Attr("sk").not_exists()

    try:
        return table.put(item=user_request, condition_expression=condition)
    except ConditionCheckFailed as err:
        logger.exception(err)
        raise ResourceConflict(
            resource_type=user_request.type.value,
            resource_id=str(KeySchema(pk=user_request.pk, sk=user_request.sk)),
        ) from err


def get_user_requests(
    table: DBTable[DBUserRequest],
    limit: Optional[int] = None,
    start_key: Optional[dict] = None,
) -> tuple[list[DBUserRequest], Optional[dict]]:
    """
    Get all user requests with the given parameters

    :param table: The DBTable object to use to access the database. Requires write access
    :param limit: The upper limit on how many entries to return
    :param start_key: The key to start the query from
    :return: A list of all user requests, and pagination key if there is one
    :raises ExternalServiceException: An unexpected error occurs in AWS
    """
    key_expression = Key("pk").eq(ItemType.USER_REQUEST.value)
    return table.query(
        key_condition_expression=key_expression,
        limit=limit,
        scan_reverse=True,
        start_key=start_key,
    )


def action_user_request(
    cognito_client: AdminCognitoClient,
    table: DBTable[DBUserRequest],
    email: str,
    action: str,
) -> dict:
    """
    Action (confirm) a user request with the given parameters
    :param cognito_client: The client to interact with the Cognito service
    :param table: The DBTable object to use to access the database. Requires write access
    :param email: The email of the user who is requesting a new role
    :param action: The action to take on the user request
    :raises ExternalServiceException: An unexpected error occurs in AWS
    :raises ResourceNotFound: The user request does not exist
    :raises ConflictException: A user with the same email already exists
    :raises ValueError: The action is not valid
    """
    try:
        pk = f"{ItemType.USER_REQUEST.value}"
        sk = email
        key = KeySchema(pk=pk, sk=sk)
        existing_item = table.get(key=key)
        if action == UserRequestAction.REJECT.value:
            table.delete(key=key)
            return {}
        if action == UserRequestAction.APPROVE.value:
            attributes = [
                {"Name": "email", "Value": email},
                {"Name": "custom:role", "Value": existing_item.role_requested},
                {"Name": "custom:company", "Value": existing_item.company},
                {"Name": "name", "Value": existing_item.name},
            ]
            response_body = cognito_client.admin_create_user(email, attributes)
            cognito_client.add_user_to_group(email, existing_item.role_requested)
            table.delete(key=key)
            return response_body
        raise ValueError("Invalid action")
    except ClientError as err:
        logger.error(err)
        error_code = err.response["Error"]["Code"]
        match error_code:
            case "UsernameExistsException":
                raise ConflictException("User with this username already exists") from err
            case _:
                raise ExternalServiceException from err
