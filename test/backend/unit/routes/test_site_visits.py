import json
from http import HTTPStatus

from backend.service.database.db_table import DBTable, KeySchema
from backend.service.environment import DOCUMENT_STORAGE_BUCKET_NAME
from backend.service.file_storage.s3_bucket import S3Bucket
from backend.service.handler import lambda_handler
from backend.service.models.api.site_visit import APIListSiteVisitResponse, APISiteVisit
from backend.service.models.db.site_visit import DBSiteVisit
from backend.service.util import AWSAccessLevel, ItemType

from ..constants import (
    CURRENT_DATE_TIME,
    PREV_DATE_TIME,
    TEST_ATTACHMENT_NAME,
    TEST_SITE_ID,
    TEST_USER_ID,
)


def test_list_sites_handler(database_with_two_site_visits, list_site_visits_request):
    _, set_of_db_entries = database_with_two_site_visits

    response = lambda_handler(
        event=list_site_visits_request[0], context=list_site_visits_request[1]
    )

    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.READ)

    found_visits = APIListSiteVisitResponse.model_validate_json(response["body"]).visits

    assert response["statusCode"] == HTTPStatus.OK
    assert len(found_visits) == len(set_of_db_entries)
    for visit in found_visits:
        assert visit in [x.to_api_model(bucket=bucket) for x in set_of_db_entries]
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_list_sites_handler_paginated(
    database_with_two_site_visits, list_site_visits_request_paginated, api_gateway_event
):
    _, set_of_db_entries = database_with_two_site_visits

    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.READ)

    response = lambda_handler(
        event=list_site_visits_request_paginated[0], context=list_site_visits_request_paginated[1]
    )

    assert response["statusCode"] == HTTPStatus.OK
    response_body = APIListSiteVisitResponse.model_validate_json(response["body"])
    assert len(response_body.visits) == 1
    assert response_body.visits[0] in [
        visit.to_api_model(bucket=bucket) for visit in set_of_db_entries
    ]
    assert response_body.last_key is not None
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]

    new_event = api_gateway_event(
        path=f"/protected/site/visits",
        method="GET",
        query_params={"limit": "1", "start_key": response_body.last_key},
        user_role="admin",
        user_groups=["admin"],
    )

    response = lambda_handler(event=new_event[0], context=new_event[1])

    assert response["statusCode"] == HTTPStatus.OK
    response_body = APIListSiteVisitResponse.model_validate_json(response["body"])
    assert len(response_body.visits) == 1
    assert response_body.visits[0] in [
        visit.to_api_model(bucket=bucket) for visit in set_of_db_entries
    ]
    assert response_body.last_key is None
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_list_sites_handler_bad_role(
    database_with_two_site_visits, list_site_visits_request_bad_role
):
    _, set_of_db_entries = list_site_visits_request_bad_role

    response = lambda_handler(
        event=list_site_visits_request_bad_role[0], context=list_site_visits_request_bad_role[1]
    )

    assert response["statusCode"] == HTTPStatus.FORBIDDEN
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_exit_site_handler(
    database_with_two_site_visits, exit_site_request, db_site_visit_only_entry
):
    response = lambda_handler(event=exit_site_request[0], context=exit_site_request[1])

    table = DBTable(AWSAccessLevel.READ, item_schema=DBSiteVisit)
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.READ)

    assert response["statusCode"] == HTTPStatus.OK
    assert APISiteVisit.model_validate_json(response["body"]) == table.get(
        key=KeySchema(pk=db_site_visit_only_entry.pk, sk=db_site_visit_only_entry.sk)
    ).to_api_model(bucket=bucket)
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_enter_site_handler(empty_database, enter_site_request, db_site_visit_only_entry):
    response = lambda_handler(event=enter_site_request[0], context=enter_site_request[1])

    table = DBTable(AWSAccessLevel.READ, item_schema=DBSiteVisit)
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.READ)

    validated_response_body = APISiteVisit.model_validate_json(response["body"])
    assert validated_response_body.exit_time == None

    assert response["statusCode"] == HTTPStatus.CREATED
    assert validated_response_body == table.get(
        key=KeySchema(pk=db_site_visit_only_entry.pk, sk=db_site_visit_only_entry.sk)
    ).to_api_model(bucket=bucket)
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_enter_site_handler_invalid_body(
    empty_database, enter_site_request_invalid_body, db_site_visit_only_entry
):
    response = lambda_handler(
        event=enter_site_request_invalid_body[0], context=enter_site_request_invalid_body[1]
    )

    print(response)

    assert response["statusCode"] == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_edit_site_visit_handler(database_with_two_site_visits, edit_site_visit_details_request):
    response = lambda_handler(
        event=edit_site_visit_details_request[0], context=edit_site_visit_details_request[1]
    )

    table = DBTable(AWSAccessLevel.READ, item_schema=DBSiteVisit)
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.READ)

    validated_response_body = APISiteVisit.model_validate_json(response["body"])

    assert response["statusCode"] == HTTPStatus.OK
    key = KeySchema(
        pk=f"{ItemType.SITE_VISIT.value}#{TEST_SITE_ID}#{TEST_USER_ID}",
        sk=CURRENT_DATE_TIME.isoformat(),
    )
    assert validated_response_body == table.get(key=key).to_api_model(bucket=bucket)
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_add_file_attachment_handler(database_with_two_site_visits, add_file_attachment_request):
    response = lambda_handler(
        event=add_file_attachment_request[0], context=add_file_attachment_request[1]
    )

    table = DBTable(AWSAccessLevel.READ, item_schema=DBSiteVisit)
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.READ)

    validated_response_body = APISiteVisit.model_validate_json(response["body"])

    assert response["statusCode"] == HTTPStatus.OK
    key = KeySchema(
        pk=f"{ItemType.SITE_VISIT.value}#{TEST_SITE_ID}#{TEST_USER_ID}",
        sk=CURRENT_DATE_TIME.isoformat(),
    )
    assert validated_response_body == table.get(key=key).to_api_model(bucket=bucket)
    assert TEST_ATTACHMENT_NAME in [
        attachment.name for attachment in validated_response_body.attachments
    ]
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_remove_file_attachment_handler(
    database_with_two_site_visits, remove_file_attachment_request, s3_bucket_with_item
):
    response = lambda_handler(
        event=remove_file_attachment_request[0], context=remove_file_attachment_request[1]
    )

    table = DBTable(AWSAccessLevel.READ, item_schema=DBSiteVisit)
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.READ)

    validated_response_body = APISiteVisit.model_validate_json(response["body"])

    assert response["statusCode"] == HTTPStatus.OK
    key = KeySchema(
        pk=f"{ItemType.SITE_VISIT.value}#{TEST_SITE_ID}#{TEST_USER_ID}",
        sk=PREV_DATE_TIME.isoformat(),
    )
    assert validated_response_body == table.get(key=key).to_api_model(bucket=bucket)
    assert TEST_ATTACHMENT_NAME not in [
        attachment.name for attachment in validated_response_body.attachments
    ]
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]
