import boto3
import pytest
from backend.environment import JOB_TABLE_NAME
from moto import mock_aws

JOB_TABLE_SPEC = dict(
    TableName=JOB_TABLE_NAME,
    AttributeDefinitions=[
        {"AttributeName": "work_order", "AttributeType": "S"},
        {"AttributeName": "user_id", "AttributeType": "S"},
        {"AttributeName": "job_type", "AttributeType": "S"},
    ],
    KeySchema=[{"AttributeName": "work_order", "KeyType": "HASH"}],
    GlobalSecondaryIndexes=[
        {
            "IndexName": "ListGSI",
            "KeySchema": [
                {"AttributeName": "user_id", "KeyType": "HASH"},
                {"AttributeName": "job_type", "KeyType": "RANGE"},
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
        resource = boto3.resource("dynamodb")
        resource.create_table(**JOB_TABLE_SPEC)
        resource.meta.client.get_waiter("table_exists").wait(TableName=JOB_TABLE_NAME)
        yield resource.Table(JOB_TABLE_NAME)
        # implicit teardown from closing mock_aws

@pytest.fixture()
def job_database_with_item(empty_job_database, db_job_all_attributes):
    empty_job_database.put_item(Item=db_job_all_attributes.model_dump())
    return empty_job_database, db_job_all_attributes
