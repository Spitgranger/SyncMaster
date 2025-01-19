import boto3
import pytest
from backend.environment import JOB_TABLE_NAME
from moto import mock_aws

table_spec = dict(
    TableName=JOB_TABLE_NAME,
    AttributeDefinitions=[
        {"AttributeName": "WorkOrder", "AttributeType": "S"},
        {"AttributeName": "UserId", "AttributeType": "S"},
        {"AttributeName": "JobType", "AttributeType": "S"},
    ],
    KeySchema=[{"AttributeName": "WorkOrder", "KeyType": "HASH"}],
    GlobalSecondaryIndexes=[
        {
            "IndexName": "ListGSI",
            "KeySchema": [
                {"AttributeName": "UserId", "KeyType": "HASH"},
                {"AttributeName": "JobType", "KeyType": "RANGE"},
            ],
            "Projection": {
                "ProjectionType": "ALL"
            }
        }
    ],
    BillingMode="PAY_PER_REQUEST",
)


@pytest.fixture()
def empty_job_database():
    with mock_aws():
        # setup
        client = boto3.client("dynamodb")
        client.create_table(**table_spec)
        client.get_waiter("table_exists").wait(TableName=JOB_TABLE_NAME)
        yield client
        # implicit teardown from closing mock_aws
