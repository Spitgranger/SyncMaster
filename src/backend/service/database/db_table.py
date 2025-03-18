"""
Module allowing interaction with a DynamoDB table, for getting, updating, and deleting items
"""

from datetime import datetime
from enum import Enum, auto
from typing import Any, Optional, Type, TypedDict

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
            print(response)
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
        kwargs: dict = {"Item": item.model_dump()}
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
        last_modified_time: datetime,
        last_modified_by: str,
        condition_expression: Optional[ConditionBase] = None,
        expression_attribute_names: Optional[dict[str, str]] = None,
    ) -> T:
        """
        Updates the given item in the db table. Be careful about modifying attributes that
        other attributes are derived from.

        :param key: The key of the item in the database to modify
        :param update_attributes: A dictionary where the keys represent the name of the attribute to
            update, and the values represent the value to update the attribute to. If the value is
            None, then the attribute is removed.
        :param last_modified_time: The time to update the last_modified_time to
        :param last_modified_by: The user to update the last_modified_by to
        :param condition_expression: A condition that must be met for the update to succeed
        :param expression_attribute_names: Aliases which can be used in the update attr's to address
            names containing special characters (i.e., containing ".")
        :return: The full updated item
        :raises ConditionCheckFailed: The provided condition was not met
        :raises ExternalServiceException: Unexpected error occurs in AWS
        :raises ValidationError: The newly updated item did not match the table schema
        :raises PermissionException: Assumed role does not have permission update an item
            in the DB, likely due to table being initialized with only read permissions
        """
        expression_attribute_values: dict[str, Any] = {
            ":last_modified_by": last_modified_by,
            ":last_modified_time": last_modified_time.isoformat(),
        }
        set_attributes: list[str] = [
            "last_modified_by = :last_modified_by",
            "last_modified_time = :last_modified_time",
        ]
        delete_attributes: list[str] = []

        if not expression_attribute_names:
            expression_attribute_names = {}

        for k, v in update_attributes.items():
            if v is not None:
                expression_attribute = k.replace(".", "_").replace("#", "_")
                expression_attribute_values[f":{expression_attribute}"] = v
                set_attributes.append(f"{k} = :{expression_attribute}")
            else:
                delete_attributes.append(k)

        update_expression = f"SET {', '.join(set_attributes)}"
        if delete_attributes:
            update_expression += f" REMOVE {', '.join(delete_attributes)}"

        kwargs = {}
        if condition_expression:
            kwargs["ConditionExpression"] = condition_expression

        try:
            response = self._table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ExpressionAttributeNames=expression_attribute_names,
                ReturnValues="ALL_NEW",
                **kwargs,
            )
        except ClientError as err:
            logger.exception(err)
            if err.response["Error"]["Code"] == "AccessDeniedException":
                raise PermissionException(
                    "Insufficient permissions to perform put on the table"
                ) from err
            if err.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise ConditionCheckFailed() from err
            raise ExternalServiceException("Unknown Error from AWS") from err
        return self.item_schema.model_validate(response["Attributes"])

    def delete(self, key: KeySchema, condition_expression: Optional[ConditionBase] = None) -> None:
        """
        Deletes a specified item from the database

        :param key: The key of the item to delete in the database
        :param condition_expression: The condition that must be met before the item can be
            deleted from the table
        :raises ConditionCheckFailed: The provided condition was not met
        :raises ExternalServiceException: Unexpected error occurs in AWS
        :raises PermissionException: Assumed role does not have permission delete an item,
            likely due to the table being initialized with only read permissions
        """
        kwargs: dict = {"Key": key}
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
        scan_reverse: bool = False,
        start_key: Optional[dict] = None,
    ) -> tuple[list[T], Optional[dict]]:
        """
        Queries the database based on the given list of criterion

        :param gsi: The index being used to query the database, the key attributes of the items
            change depending on GSI
        :param key_condition_expression: A condition placed on the key attributes, only items
            meeting this condition are returned
        :param filter_expression: A condition placed on any attributes, only items meeting this
            condition are returned
        :param limit: The maximum number of entries to be returned from the query
        :param scan_reverse: if true reverse the order that table items are scanned in, this
            reverses the order of the items received from the query. By default items come
            in ascending order, so making this true puts them in descending order.
        :param start_key: The key to start after, received from a previous query
        :return: The list of items matching the requested query and the last evaluated key
        :raises ConditionValidationError: The key condition is not valid, this usually happens
            when using a condition other than `.eq` on a hash key
        :raises ValidationError: The returned items did not match the provided schema for the table
        :raises ExternalServiceException: Unexpected error occurs in S3
        """
        kwargs: dict = {}
        if gsi:
            kwargs["IndexName"] = gsi.name
        if key_condition_expression:
            kwargs["KeyConditionExpression"] = key_condition_expression
        if filter_expression:
            kwargs["FilterExpression"] = filter_expression
        if scan_reverse is not None:
            kwargs["ScanIndexForward"] = not scan_reverse
        if start_key:
            kwargs["ExclusiveStartKey"] = start_key

        last_eval_key = None
        items: list[dict] = []

        try:
            while True:
                if last_eval_key:
                    kwargs["ExclusiveStartKey"] = last_eval_key
                if limit:
                    kwargs["Limit"] = limit

                response: dict = self._table.query(**kwargs)
                logger.info(response)

                items.extend(response.get("Items", []))

                if not (last_eval_key := response.get("LastEvaluatedKey")):
                    break

                if limit and not (limit := limit - response.get("Count", 0)):
                    break
        except ClientError as err:
            if err.response["Error"]["Code"] == "ValidationException":
                raise ConditionValidationError() from err
            raise ExternalServiceException("Unknown Error from AWS") from err
        return [self.item_schema.model_validate(item) for item in items], last_eval_key
