import boto3
import pytest
from backend.service.environment import TABLE_NAME
from moto import mock_aws

TABLE_SPEC = dict(
    TableName=TABLE_NAME,
    AttributeDefinitions=[
        {"AttributeName": "pk", "AttributeType": "S"},
        {"AttributeName": "sk", "AttributeType": "S"},
        {"AttributeName": "gsi_1_pk", "AttributeType": "S"},
        {"AttributeName": "gsi_1_sk", "AttributeType": "S"},
    ],
    KeySchema=[
        {"AttributeName": "pk", "KeyType": "HASH"},
        {"AttributeName": "sk", "KeyType": "RANGE"},
    ],
    GlobalSecondaryIndexes=[
        {
            "IndexName": "GSI1",
            "KeySchema": [
                {"AttributeName": "gsi_1_pk", "KeyType": "HASH"},
                {"AttributeName": "gsi_1_sk", "KeyType": "RANGE"},
            ],
            "Projection": {"ProjectionType": "ALL"},
        }
    ],
    BillingMode="PAY_PER_REQUEST",
)


@pytest.fixture()
def empty_database():
    with mock_aws():
        # setup
        resource = boto3.resource("dynamodb")
        resource.create_table(**TABLE_SPEC)
        resource.meta.client.get_waiter("table_exists").wait(TableName=TABLE_NAME)
        yield resource.Table(TABLE_NAME)
        # implicit teardown from closing mock_aws


@pytest.fixture()
def database_with_item(empty_database, db_document):
    empty_database.put_item(Item=db_document.model_dump())
    return empty_database, db_document
