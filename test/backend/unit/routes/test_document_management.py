import json
from http import HTTPStatus

from backend.service.database.db_table import DBTable, KeySchema
from backend.service.handler import lambda_handler
from backend.service.models.api.document import APIDocumentResponse

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
