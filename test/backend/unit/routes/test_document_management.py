import json
from datetime import datetime
from http import HTTPStatus

from backend.service.database.db_table import DBTable, KeySchema
from backend.service.handler import lambda_handler
from backend.service.models.api.document import APIDocumentResponse, APIExpiringDocumentResponse

from ..constants import TEST_DOCUMENT_ID, TEST_PARENT_FOLDER_ID


def test_get_presigned_url_handler(s3_bucket_with_item, get_presigned_url_request):
    response = lambda_handler(
        event=get_presigned_url_request[0], context=get_presigned_url_request[1]
    )

    assert response["statusCode"] == HTTPStatus.CREATED
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_upload_handler(empty_database, s3_bucket_with_item, upload_document_request):
    response = lambda_handler(event=upload_document_request[0], context=upload_document_request[1])

    assert response["statusCode"] == HTTPStatus.CREATED
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_upload_with_conflict_handler(
    database_with_document, s3_bucket_with_item, upload_document_request
):
    response = lambda_handler(event=upload_document_request[0], context=upload_document_request[1])

    assert response["statusCode"] == HTTPStatus.CONFLICT
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_get_files_handler(database_with_document, s3_bucket_with_item, get_files_request):
    response = lambda_handler(event=get_files_request[0], context=get_files_request[1])
    assert response["statusCode"] == HTTPStatus.OK
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]
    response_body = json.loads(response["body"])
    first_document = APIDocumentResponse.model_validate(response_body[0])
    assert first_document.document_id == TEST_DOCUMENT_ID
    assert first_document.parent_folder_id == TEST_PARENT_FOLDER_ID


def test_delete_files_handler(database_with_document, s3_bucket_with_item, delete_files_request):
    response = lambda_handler(event=delete_files_request[0], context=delete_files_request[1])
    assert response["statusCode"] == HTTPStatus.NO_CONTENT


def test_delete_files_with_bad_role_handler(
    database_with_document, s3_bucket_with_item, delete_files_bad_role_request
):
    response = lambda_handler(
        event=delete_files_bad_role_request[0], context=delete_files_bad_role_request[1]
    )
    assert response["statusCode"] == HTTPStatus.FORBIDDEN


def test_list_expiring_documents_handler_from_now(
    database_with_document, list_expiring_documents_request
):
    response = lambda_handler(
        event=list_expiring_documents_request[0], context=list_expiring_documents_request[1]
    )
    assert response["statusCode"] == HTTPStatus.OK
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_list_expiring_documents_handler_bad_role(
    database_with_document, list_expiring_documents_bad_role_request
):
    response = lambda_handler(
        event=list_expiring_documents_bad_role_request[0],
        context=list_expiring_documents_bad_role_request[1],
    )
    assert response["statusCode"] == HTTPStatus.FORBIDDEN
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_list_expiring_documents_handler_no_days(
    database_with_documents_and_folders, list_expiring_documents_request_none
):
    response = lambda_handler(
        event=list_expiring_documents_request_none[0],
        context=list_expiring_documents_request_none[1],
    )
    assert response["statusCode"] == HTTPStatus.OK
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_list_expiring_documents_handler_paginated(
    api_gateway_event,
    database_with_documents_and_folders,
    list_expiring_documents_paginated_request,
):
    response = lambda_handler(
        event=list_expiring_documents_paginated_request[0],
        context=list_expiring_documents_paginated_request[1],
    )
    assert response["statusCode"] == HTTPStatus.OK
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]
    response_body = APIExpiringDocumentResponse.model_validate_json(response["body"])
    assert response_body.last_key is not None
    assert len(response_body.documents) == 1

    new_event = api_gateway_event(
        path=f"/protected/documents/expiring_documents",
        method="GET",
        query_params={"limit": "1", "start_key": response_body.last_key},
        user_role="admin",
        user_groups=["admin"],
        time=datetime.now(),
    )

    response = lambda_handler(event=new_event[0], context=new_event[1])

    assert response["statusCode"] == HTTPStatus.OK
    response_body = APIExpiringDocumentResponse.model_validate_json(response["body"])
    assert len(response_body.documents) == 1
    assert response_body.documents[0] in [
        document.to_api_model() for document in database_with_documents_and_folders[1]
    ]
    assert response_body.last_key is None
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]
