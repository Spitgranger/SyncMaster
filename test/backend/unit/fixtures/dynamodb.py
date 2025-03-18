import boto3
import pytest
from backend.service.environment import TABLE_NAME
from moto import mock_aws

TABLE_SPEC = dict(
    TableName=TABLE_NAME,
    AttributeDefinitions=[
        {"AttributeName": "pk", "AttributeType": "S"},
        {"AttributeName": "sk", "AttributeType": "S"},
        {"AttributeName": "type", "AttributeType": "S"},
        {"AttributeName": "last_modified_time", "AttributeType": "S"},
    ],
    KeySchema=[
        {"AttributeName": "pk", "KeyType": "HASH"},
        {"AttributeName": "sk", "KeyType": "RANGE"},
    ],
    GlobalSecondaryIndexes=[
        {
            "IndexName": "GSI1",
            "KeySchema": [
                {"AttributeName": "type", "KeyType": "HASH"},
                {"AttributeName": "last_modified_time", "KeyType": "RANGE"},
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
def database_with_document(empty_database, db_document):
    empty_database.put_item(Item=db_document.model_dump())
    return empty_database, db_document


@pytest.fixture()
def database_with_documents_and_folders(
    empty_database,
    db_document,
    db_document_folder,
    db_document_folder_in_folder,
    db_document_file_in_folder,
):
    empty_database.put_item(Item=db_document.model_dump())
    empty_database.put_item(Item=db_document_folder.model_dump())
    empty_database.put_item(Item=db_document_folder_in_folder.model_dump())
    empty_database.put_item(Item=db_document_file_in_folder.model_dump())
    return (
        empty_database,
        db_document,
        db_document_folder,
        db_document_folder_in_folder,
        db_document_file_in_folder,
    )


@pytest.fixture()
def database_with_complete_site_visit(empty_database, db_site_visit_complete):
    empty_database.put_item(Item=db_site_visit_complete.model_dump())
    return empty_database, db_site_visit_complete


@pytest.fixture()
def database_with_two_site_visits(database_with_complete_site_visit, db_site_visit_only_entry):
    database, complete_entry = database_with_complete_site_visit
    database.put_item(Item=db_site_visit_only_entry.model_dump())
    return database, [complete_entry, db_site_visit_only_entry]


@pytest.fixture()
def database_with_site(empty_database, db_site):
    empty_database.put_item(Item=db_site.model_dump())
    return empty_database, db_site


@pytest.fixture()
def database_with_two_sites(database_with_site, db_site_new):
    database, complete_entry = database_with_site
    database.put_item(Item=db_site_new.model_dump())
    return empty_database, {complete_entry, db_site_new}
