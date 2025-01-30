
from backend.database.db_table import DBTable
from backend.models.db.job import DBJob
from backend.service.environment import JOB_TABLE_NAME, JOB_TABLE_WRITE_ROLE
from boto3.dynamodb.conditions import Key

from ..constants import TEST_JOB_DESCRIPTION, TEST_JOB_TYPE, TEST_USER_ID, TEST_WORK_ORDER

def test_put_item(empty_job_database, db_job_all_attributes):
    base_resource = empty_job_database

    table = DBTable(table_name=JOB_TABLE_NAME, role=JOB_TABLE_WRITE_ROLE, item_schema=DBJob)

    table.put(item=db_job_all_attributes)

    items: list[dict] = base_resource.scan()["Items"]
    assert len(items) == 1
    assert DBJob.model_validate(items[0]) == db_job_all_attributes

def test_get_item(job_database_with_item):
    base_resource, job = job_database_with_item

    table = DBTable(table_name=JOB_TABLE_NAME, role=JOB_TABLE_WRITE_ROLE, item_schema=DBJob)

    key = DBJob.create_key(work_order=TEST_WORK_ORDER)

    assert table.get(key=key) == job

def test_delete_item(job_database_with_item):
    base_resource, job = job_database_with_item

    table = DBTable(table_name=JOB_TABLE_NAME, role=JOB_TABLE_WRITE_ROLE, item_schema=DBJob)

    key = DBJob.create_key(work_order=TEST_WORK_ORDER)

    assert table.delete(key=key) == None

    items: list[dict] = base_resource.scan()["Items"]
    assert len(items) == 0

def test_query_items(job_database_with_item):
    base_resource, job = job_database_with_item

    table = DBTable(table_name=JOB_TABLE_NAME, role=JOB_TABLE_WRITE_ROLE, item_schema=DBJob)

    key = DBJob.create_key(work_order=TEST_WORK_ORDER)

    items = table.query(key_condition_expression=Key("work_order").eq(TEST_WORK_ORDER))
    assert len(items) == 1
    assert items[0] == job
