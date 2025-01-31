"""
Module allowing interaction with a DynamoDB table, for getting, updating, and deleting items
"""

from typing import Optional, Type, TypedDict
from boto3.dynamodb.conditions import ConditionBase

from ..models.db.db_base import DBItemModel
from ..util import create_table_with_role

class KeySchema(TypedDict):
    pk: str
    sk: str


class DBTable[T: DBItemModel]:
    """
    Abstraction around an DynamoDB Table providing a limited selection of operations on a given table.
    """

    def __init__(self, table_name: str, role: str, item_schema: Type[T]):
        """
        Initialize a connection to a DynamoDB Table

        :param table_name: The name of the underlying DynamoDB Table in AWS
        :param access: The level of permission desired for this connection
        :return: The DynamoDB Table object
        :raises ExternalServiceException: Unable to connect to the DynamoDB Service
        :raises IAMPermissionError: Unable to assume IAM role for required access level
        """
        self.name = table_name
        self.item_schema = item_schema

        self._table = create_table_with_role(table_name=table_name, role=role)

    def get(
        self,
        key: KeySchema,
    ) -> T:
        """
        get an item from the database with the given key

        :param key: The key of the item in the database
        :return: The item with the given key stored in the database
        :raises ExternalServiceException: Unexpected error occurs in AWS
        :raises ItemNotFound: The item with the given key could not be found in the database
        """
        response: dict = self._table.get_item(TableName=self.name, Key=key)
        return self.item_schema.model_validate(response["Item"])

    def put(self, item: T, condition_expression: Optional[ConditionBase] = None) -> T:
        """
        Puts the given item into the DynamoDB Table

        :param item: The item to put into the DynamoDB Table
        :param condition_expression: The condition that must be met before the item can be put into the table
        :return: The newly added item
        :raises ConditionCheckFailed: The provided condition was not met
        :raises ExternalServiceException: Unexpected error occurs in AWS
        :raises PermissionException: Assumed role does not have permission to make an put and item into the DB,
            likely due to table being initialized with only read permissions
        """
        kwargs = {"Item": item.model_dump()}
        if condition_expression:
            kwargs["ConditionExpression"] = condition_expression

        self._table.put_item(**kwargs)
        return item

    def delete(self, key: KeySchema, condition_expression: Optional[ConditionBase] = None) -> None:
        """
        Completes an existing multipart upload

        :param key: The key of the item to delete in the database
        :param condition_expression: The condition that must be met before the item can be deleted from the table
        :raises ConditionCheckFailed: The provided condition was not met
        :raises ExternalServiceException: Unexpected error occurs in AWS
        :raises PermissionException: Assumed role does not have permission delete an item,
            likely due to the table being initialized with only read permissions
        """
        kwargs = {"Key": key}
        if condition_expression:
            kwargs["ConditionExpression"] = condition_expression
        self._table.delete_item(**kwargs)

    def query(
        self,
        gsi: Optional[str] = None,
        key_condition_expression: Optional[ConditionBase] = None,
        filter_expression: Optional[ConditionBase] = None,
    ) -> list[T]:
        """
        Queries the database based on the given list of criterion

        :param gsi: The index being used to query the database, the key attributes of the items change depending on GSI
        :param key_condition_expression: A condition placed on the key attributes, only items meeting this condition are returned
        :param filter_expression: A condition placed on any attributes, only items meeting this condition are returned
        :raises ExternalServiceException: Unexpected error occurs in S3
        """
        kwargs = dict()
        if gsi:
            kwargs["IndexName"] = gsi
        if key_condition_expression:
            kwargs["KeyConditionExpression"] = key_condition_expression
        if filter_expression:
            kwargs["FilterExpression"] = filter_expression
        response: dict = self._table.query(**kwargs)
        items: list[dict] = response["Items"] if response["Items"] else list()
        return [self.item_schema.model_validate(item) for item in items]
