import pytest
from backend.service.database.db_table import GSI, DBTable, KeySchema
from backend.service.exceptions import (
    ConditionCheckFailed,
    ConditionValidationError,
    ExternalServiceException,
    PermissionException,
    ResourceNotFound,
)
from backend.service.models.db.document import DBDocument
from backend.service.models.db.site_visit import DBSiteVisit
from backend.service.util import AWSAccessLevel
from boto3.dynamodb.conditions import Attr, Key
from botocore.stub import Stubber

from ..constants import FUTURE_DATE_TIME, PREV_DATE_TIME, TEST_DOCUMENT_PATH_ALT, TEST_USER_ID


def test_put_item(empty_database, db_document):
    base_resource = empty_database

    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBDocument)

    table.put(item=db_document)

    items: list[dict] = base_resource.scan()["Items"]
    assert len(items) == 1
    assert DBDocument.model_validate(items[0]) == db_document


def test_put_item_condition_check_fail(database_with_document, db_document_old):
    base_resource, _ = database_with_document

    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBDocument)

    condition_expression = (
        Key("pk").eq(db_document_old.pk)
        & Key("sk").eq(db_document_old.sk)
        & Attr("last_modified_time").lt(db_document_old.last_modified_time.isoformat())
    )

    with pytest.raises(ConditionCheckFailed):
        table.put(item=db_document_old, condition_expression=condition_expression)

    items: list[dict] = base_resource.scan()["Items"]
    assert len(items) == 1


@pytest.mark.parametrize(
    "aws_error_code, expected_error_class",
    [
        pytest.param("InternalError", ExternalServiceException, id="AWS Error"),
        pytest.param("AccessDeniedException", PermissionException, id="Incorrect Permissions"),
    ],
)
def test_put_item_external_errors(
    empty_database, db_document, aws_error_code, expected_error_class
):
    base_resource = empty_database

    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBDocument)

    stubber = Stubber(table._resource.meta.client)
    stubber.add_client_error(method="put_item", service_error_code=aws_error_code)

    with stubber, pytest.raises(expected_error_class):
        table.put(item=db_document)

    items: list[dict] = base_resource.scan()["Items"]
    assert len(items) == 0


def test_get_item(database_with_document):
    base_resource, document = database_with_document

    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBDocument)

    key = KeySchema(pk=document.pk, sk=document.sk)

    assert table.get(key=key) == document


def test_get_item_resource_not_found(empty_database):
    base_resource = empty_database

    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBDocument)

    key = KeySchema(pk="does-not-exist", sk="does-not-exist")

    with pytest.raises(ResourceNotFound):
        table.get(key=key)


def test_get_item_external_error(database_with_document):
    base_resource, document = database_with_document

    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBDocument)

    stubber = Stubber(table._resource.meta.client)
    stubber.add_client_error(method="get_item", service_error_code="InternalError")

    key = KeySchema(pk=document.pk, sk=document.sk)

    with stubber, pytest.raises(ExternalServiceException):
        table.get(key=key) == document


def test_delete_item(database_with_document):
    base_resource, document = database_with_document

    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBDocument)

    key = KeySchema(pk=document.pk, sk=document.sk)

    assert table.delete(key=key) == None

    items: list[dict] = base_resource.scan()["Items"]
    assert len(items) == 0


def test_delete_item_condition_check_fail(database_with_document):
    base_resource, document = database_with_document

    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBDocument)

    key = KeySchema(pk=document.pk, sk=document.sk)

    condition_expression = (
        Key("pk").eq(document.pk)
        & Key("sk").eq(document.sk)
        & Attr("last_modified_time").lt(PREV_DATE_TIME.isoformat())
    )

    with pytest.raises(ConditionCheckFailed):
        table.delete(key=key, condition_expression=condition_expression)

    items: list[dict] = base_resource.scan()["Items"]
    assert len(items) == 1


@pytest.mark.parametrize(
    "aws_error_code, expected_error_class",
    [
        pytest.param("InternalError", ExternalServiceException, id="AWS Error"),
        pytest.param("AccessDeniedException", PermissionException, id="Incorrect Permissions"),
    ],
)
def test_delete_item_external_errors(database_with_document, aws_error_code, expected_error_class):
    base_resource, document = database_with_document

    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBDocument)

    stubber = Stubber(table._resource.meta.client)
    stubber.add_client_error(method="delete_item", service_error_code=aws_error_code)

    key = KeySchema(pk=document.pk, sk=document.sk)

    with stubber, pytest.raises(expected_error_class):
        table.delete(key=key)

    items: list[dict] = base_resource.scan()["Items"]
    assert len(items) == 1


def test_update_item(database_with_document):
    base_resource, document = database_with_document

    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBDocument)

    item = table.update(
        key=KeySchema(pk=document.pk, sk=document.sk),
        update_attributes={
            "document_path": TEST_DOCUMENT_PATH_ALT,
        },
        last_modified_by=TEST_USER_ID,
        last_modified_time=FUTURE_DATE_TIME,
        condition_expression=Attr("last_modified_time").lt(FUTURE_DATE_TIME.isoformat()),
    )
    assert item.document_path == TEST_DOCUMENT_PATH_ALT
    assert item.last_modified_time == FUTURE_DATE_TIME

    items: list[dict] = base_resource.scan()["Items"]
    assert len(items) == 1
    assert DBDocument.model_validate(items[0]) == item


def test_update_item_with_removal(database_with_complete_site_visit):
    base_resource, site_visit = database_with_complete_site_visit

    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)

    item = table.update(
        key=KeySchema(pk=site_visit.pk, sk=site_visit.sk),
        update_attributes={
            "exit_time": None,
        },
        last_modified_by=TEST_USER_ID,
        last_modified_time=FUTURE_DATE_TIME,
        condition_expression=Attr("last_modified_time").lt(FUTURE_DATE_TIME.isoformat()),
    )
    assert item.exit_time == None
    assert item.last_modified_time == FUTURE_DATE_TIME

    items: list[dict] = base_resource.scan()["Items"]
    assert len(items) == 1
    assert DBSiteVisit.model_validate(items[0]) == item


def test_update_item_condition_check_fail(database_with_document):
    base_resource, document = database_with_document

    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBDocument)

    with pytest.raises(ConditionCheckFailed):
        table.update(
            key=KeySchema(pk=document.pk, sk=document.sk),
            update_attributes={
                "document_path": TEST_DOCUMENT_PATH_ALT,
            },
            last_modified_by=TEST_USER_ID,
            last_modified_time=FUTURE_DATE_TIME,
            condition_expression=Attr("last_modified_time").lt(PREV_DATE_TIME.isoformat()),
        )


@pytest.mark.parametrize(
    "aws_error_code, expected_error_class",
    [
        pytest.param("InternalError", ExternalServiceException, id="AWS Error"),
        pytest.param("AccessDeniedException", PermissionException, id="Incorrect Permissions"),
    ],
)
def test_update_item_external_errors(database_with_document, aws_error_code, expected_error_class):
    base_resource, document = database_with_document

    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBDocument)

    stubber = Stubber(table._resource.meta.client)
    stubber.add_client_error(method="update_item", service_error_code=aws_error_code)

    key = KeySchema(pk=document.pk, sk=document.sk)

    with stubber, pytest.raises(expected_error_class):
        table.update(
            key=KeySchema(pk=document.pk, sk=document.sk),
            update_attributes={
                "document_path": TEST_DOCUMENT_PATH_ALT,
            },
            last_modified_by=TEST_USER_ID,
            last_modified_time=FUTURE_DATE_TIME,
            condition_expression=Attr("last_modified_time").lt(PREV_DATE_TIME.isoformat()),
        )


def test_query_items(database_with_document):
    base_resource, document = database_with_document

    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBDocument)

    items = table.query(key_condition_expression=Key("pk").eq(document.pk), limit=1)
    assert len(items) == 1
    assert items[0] == document


def test_query_items_with_gsi(database_with_document):
    base_resource, document = database_with_document

    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBDocument)

    items = table.query(gsi=GSI.GSI1, key_condition_expression=Key("type").eq(document.type.value))
    assert len(items) == 1
    assert items[0] == document


def test_query_items_with_filter(database_with_document):
    base_resource, document = database_with_document

    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBDocument)

    items = table.query(
        key_condition_expression=Key("pk").eq(document.pk),
        filter_expression=Attr("last_modified_by").eq("does-not-exist"),
    )
    assert len(items) == 0


def test_query_items_invalid_key_condition(database_with_document):
    base_resource, document = database_with_document

    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBDocument)

    with pytest.raises(ConditionValidationError):
        table.query(key_condition_expression=Key("pk").begins_with(DBDocument.item_type().value))
        # can only do .eq with a hash key on a query


def test_query_items_external_error(database_with_document):
    base_resource, document = database_with_document

    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBDocument)

    stubber = Stubber(table._resource.meta.client)
    stubber.add_client_error(method="query", service_error_code="InternalError")

    with stubber, pytest.raises(ExternalServiceException):
        table.query(gsi=GSI.GSI1, key_condition_expression=Key("type").eq(document.type.value))
