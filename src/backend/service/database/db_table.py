"""
Module allowing interaction with a DynamoDB table, for getting, updating, and deleting items
"""

from enum import Enum, auto
from typing import Any, Literal, Optional, Type, TypedDict

from aws_lambda_powertools.logging import Logger
from boto3.dynamodb.conditions import ConditionBase
from botocore.exceptions import ClientError

from ..environment import TABLE_NAME, TABLE_READ_ROLE, TABLE_WRITE_ROLE
from ..exceptions import (
    ConditionCheckFailed,
    ConditionValidationError,
    ExternalServiceException,
    PermissionException,
    ResourceNotFound,
)
from ..models.db.db_base import DBItemModel
from ..util import AWSAccessLevel, create_resource_with_role

logger = Logger()


class GSI(Enum):
    """
    An enum of all availables GSI's on the table
    """

    GSI1 = auto()


class KeySchema(TypedDict):
    """
    Defines the key schema for the table
    """

    pk: str
    sk: str


class DBTable[T: DBItemModel]:
    """
    Abstraction around an DynamoDB Table providing a limited selection of operations on
    a given table.
    """

    def __init__(self, access: AWSAccessLevel, item_schema: Type[T]):
        """
        Initialize a connection to a DynamoDB Table

        :param table_name: The name of the underlying DynamoDB Table in AWS
        :param access: The level of permission desired for this connection
        :return: The DynamoDB Table object
        :raises ExternalServiceException: Unable to connect to the DynamoDB Service
        :raises PermissionException: Unable to assume IAM role for required access level
        """
        self.name = TABLE_NAME
        self.item_schema = item_schema

        role = TABLE_READ_ROLE
        if access == AWSAccessLevel.WRITE:
            role = TABLE_WRITE_ROLE

        self._resource = create_resource_with_role(service_name="dynamodb", role=role)
        self._table = self._resource.Table(self.name)

    def get(
        self,
        key: KeySchema,
    ) -> T:
        """
        get an item from the database with the given key

        :param key: The key of the item in the database
        :return: The item with the given key stored in the database
        :raises ExternalServiceException: Unexpected error occurs in AWS
        :raises ValidationError: The returned item did not match the provided schema for the table
        :raises ResourceNotFound: The item with the given key could not be found in the database
        """
        try:
            response: dict = self._table.get_item(Key=key)
            if not response.get("Item"):
                raise ResourceNotFound(
                    resource_type=self.item_schema.item_type().value, resource_id=str(key)
                )
        except ClientError as err:
            logger.exception(err)
            raise ExternalServiceException("Unknown Error from AWS") from err
        return self.item_schema.model_validate(response["Item"])

    def put(self, item: T, condition_expression: Optional[ConditionBase] = None) -> T:
        """
        Puts the given item into the DynamoDB Table

        :param item: The item to put into the DynamoDB Table
        :param condition_expression: The condition that must be met before the item can be put
        into the table
        :return: The newly added item
        :raises ConditionCheckFailed: The provided condition was not met
        :raises ExternalServiceException: Unexpected error occurs in AWS
        :raises PermissionException: Assumed role does not have permission to make an put and item
            into the DB, likely due to table being initialized with only read permissions
        """
        kwargs = {"Item": item.model_dump()}
        if condition_expression:
            kwargs["ConditionExpression"] = condition_expression

        try:
            self._table.put_item(**kwargs)
        except ClientError as err:
            logger.exception(err)
            if err.response["Error"]["Code"] == "AccessDeniedException":
                raise PermissionException(
                    "Insufficient permissions to perform put on the table"
                ) from err
            if err.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise ConditionCheckFailed() from err
            raise ExternalServiceException("Unknown Error from AWS") from err
        return item

    def update(
        self,
        key: KeySchema,
        update_attributes: dict[str, Any],
        condition_expression: Optional[ConditionBase] = None,
    ) -> T:
        expression_attribute_values: dict[str, Any] = {}
        set_attributes: list[str] = []
        delete_attributes: list[str] = []

        for k, v in update_attributes.items():
            if v is not None:
                expression_attribute_values[f":{k}"] = v
                set_attributes.append(f"{k} = :{k}")
            else:
                delete_attributes.append(k)

        update_expression = f"SET {", ".join(set_attributes)} REMOVE {", ".join(delete_attributes)}"

        kwargs = {}
        if condition_expression:
            kwargs["ConditionExpression"] = condition_expression
        response = self._table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW",
            **kwargs,
        )

        return self.item_schema.model_validate(response["Attributes"])

    def delete(self, key: KeySchema, condition_expression: Optional[ConditionBase] = None) -> None:
        """
        Completes an existing multipart upload

        :param key: The key of the item to delete in the database
        :param condition_expression: The condition that must be met before the item can be
            deleted from the table
        :raises ConditionCheckFailed: The provided condition was not met
        :raises ExternalServiceException: Unexpected error occurs in AWS
        :raises PermissionException: Assumed role does not have permission delete an item,
            likely due to the table being initialized with only read permissions
        """
        kwargs = {"Key": key}
        if condition_expression:
            kwargs["ConditionExpression"] = condition_expression

        try:
            self._table.delete_item(**kwargs)
        except ClientError as err:
            if err.response["Error"]["Code"] == "AccessDeniedException":
                raise PermissionException(
                    "Insufficient permissions to perform delete on the table"
                ) from err
            if err.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise ConditionCheckFailed() from err
            raise ExternalServiceException("Unknown Error from AWS") from err

    def query(
        self,
        gsi: Optional[GSI] = None,
        key_condition_expression: Optional[ConditionBase] = None,
        filter_expression: Optional[ConditionBase] = None,
        limit: Optional[int] = None,
    ) -> list[T]:
        """
        Queries the database based on the given list of criterion

        :param gsi: The index being used to query the database, the key attributes of the items
            change depending on GSI
        :param key_condition_expression: A condition placed on the key attributes, only items
            meeting this condition are returned
        :param filter_expression: A condition placed on any attributes, only items meeting this
            condition are returned
        :param limit: The maximum number of entries to be returned from the query
        :raises ConditionValidationError: The key condition is not valid, this usually happens
            when using a condition other than `.eq` on a hash key
        :raises ValidationError: The returned items did not match the provided schema for the table
        :raises ExternalServiceException: Unexpected error occurs in S3
        """
        kwargs = {}
        if gsi:
            kwargs["IndexName"] = gsi.name
        if key_condition_expression:
            kwargs["KeyConditionExpression"] = key_condition_expression
        if filter_expression:
            kwargs["FilterExpression"] = filter_expression

        last_eval_key = None
        items: list[dict] = []

        try:
            while True:
                if last_eval_key:
                    kwargs["ExclusiveStartKey"] = last_eval_key
                if limit:
                    kwargs["Limit"] = limit

                response: dict = self._table.query(**kwargs)

                items.extend(response.get("Items", []))

                if not (last_eval_key := response.get("LastEvaluatedKey")):
                    break

                if limit and not (limit := limit - response.get("Count", 0)):
                    break
        except ClientError as err:
            if err.response["Error"]["Code"] == "ValidationException":
                raise ConditionValidationError() from err
            raise ExternalServiceException("Unknown Error from AWS") from err
        return [self.item_schema.model_validate(item) for item in items]
