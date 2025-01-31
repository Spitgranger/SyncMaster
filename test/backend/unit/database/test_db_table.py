
from backend.service.database.db_table import DBTable, KeySchema
from backend.service.models.db.document import DBDocument
from backend.service.environment import TABLE_NAME, TABLE_WRITE_ROLE
from boto3.dynamodb.conditions import Key

from ..constants import TEST_USER_ID, TEST_SITE_ID, TEST_DOCUMENT_PATH

def test_put_item(empty_database, db_document):
    base_resource = empty_database

    table = DBTable(table_name=TABLE_NAME, role=TABLE_WRITE_ROLE, item_schema=DBDocument)

    table.put(item=db_document)

    items: list[dict] = base_resource.scan()["Items"]
    assert len(items) == 1
    assert DBDocument.model_validate(items[0]) == db_document

def test_get_item(database_with_item):
    base_resource, document = database_with_item

    table = DBTable(table_name=TABLE_NAME, role=TABLE_WRITE_ROLE, item_schema=DBDocument)

    key = KeySchema(pk=document.pk, sk=document.sk)

    assert table.get(key=key) == document

def test_delete_item(database_with_item):
    base_resource, document = database_with_item

    table = DBTable(table_name=TABLE_NAME, role=TABLE_WRITE_ROLE, item_schema=DBDocument)

    key = KeySchema(pk=document.pk, sk=document.sk)

    assert table.delete(key=key) == None

    items: list[dict] = base_resource.scan()["Items"]
    assert len(items) == 0

def test_query_items(database_with_item):
    base_resource, document = database_with_item

    table = DBTable(table_name=TABLE_NAME, role=TABLE_WRITE_ROLE, item_schema=DBDocument)

    items = table.query(key_condition_expression=Key("pk").eq(document.pk))
    assert len(items) == 1
    assert items[0] == document
