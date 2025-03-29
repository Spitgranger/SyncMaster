"""
Routes to associated with document management
"""

import base64
import json
from http import HTTPStatus
from typing import Optional

from aws_lambda_powertools.event_handler import Response, content_types
from aws_lambda_powertools.event_handler.api_gateway import Router
from aws_lambda_powertools.event_handler.openapi.params import Body, Path, Query
from typing_extensions import Annotated

from ...database.db_table import DBTable
from ...document_management.document_management import (
    delete,
    get_all_files,
    get_presigned_url,
    list_expiring_documents,
    upload_file,
)
from ...environment import DOCUMENT_STORAGE_BUCKET_NAME
from ...file_storage.s3_bucket import S3Bucket
from ...models.api.document import APIDocumentUploadRequest, APIExpiringDocumentResponse
from ...models.db.document import DBDocument
from ...util import (
    CORS_HEADERS,
    AWSAccessLevel,
    UserType,
    create_http_response,
    time_epoch_to_datetime,
    verify_user_role,
)

router = Router()


@router.post("/upload")
def upload_handler(body: Annotated[APIDocumentUploadRequest, Body()]):
    """
    "Uploads" a file to the virtual file system
    :param body: The body of the HTTP request
    :return: dictionary containing http response
    """
    verify_user_role(
        user_groups=router.current_event["requestContext"]["authorizer"]["claims"][
            "cognito:groups"
        ],
        acceptable_roles=[UserType.ADMIN],
        action="upload documents",
    )

    request_time = time_epoch_to_datetime(
        router.current_event["requestContext"]["requestTimeEpoch"]
    )

    document_table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBDocument)
    item = upload_file(
        document_table,
        body.document_name,
        body.document_type,
        body.parent_folder_id,
        body.site_id,
        body.document_path,
        body.s3_key,
        body.e_tag,
        body.user_id,
        body.requires_ack,
        request_time,
        body.document_expiry,
    )
    return create_http_response(
        status_code=HTTPStatus.CREATED.value,
        content_type=content_types.APPLICATION_JSON,
        body=item.to_api_model().model_dump_json(),
    )


@router.get("/<site_id>/<folder>/get_files")
def get_files_handler(site_id: Annotated[str, Path()], folder: Annotated[str, Path()]):
    """
    Route to get files for a specific site
    :param site_id: The site id to get documents for
    :param folder: The parent folder id to get files for
    :return: dictionary containing http response
    """
    s3_bucket = S3Bucket(DOCUMENT_STORAGE_BUCKET_NAME, AWSAccessLevel.READ)
    document_table = DBTable(access=AWSAccessLevel.READ, item_schema=DBDocument)

    files = get_all_files(document_table, s3_bucket, site_id, folder)

    response_body = json.dumps([file.model_dump() for file in files])

    return create_http_response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=response_body,
        headers=CORS_HEADERS,
    )


@router.get("/get_presigned_url/<s3_key>")
def get_presigned_url_handler(s3_key: Annotated[str, Path()]):
    """
    Route to get presigned url to upload file
    :param s3_key: The name of the file
    :return: dictionary containing http response
    """
    s3_bucket = S3Bucket(DOCUMENT_STORAGE_BUCKET_NAME, AWSAccessLevel.WRITE)
    url = get_presigned_url(s3_key, s3_bucket)

    return create_http_response(
        status_code=HTTPStatus.CREATED.value,
        content_type=content_types.APPLICATION_JSON,
        body=json.dumps({"s3_presigned_url": url}),
    )


@router.delete("/delete")
def delete_file_handler(
    site_id: Annotated[str, Query()],
    parent_folder_id: Annotated[str, Query()],
    document_id: Annotated[str, Query()],
):
    """
    Route to get files for a specific site
    :param site_id: The site containg the file to be deleted
    :param parent_folder_id: The parent folder which contains this document
    :param document_id: The unique identifier of the document to be deleted
    :return: dictionary containing http response
    """
    verify_user_role(
        user_groups=router.current_event["requestContext"]["authorizer"]["claims"][
            "cognito:groups"
        ],
        acceptable_roles=[UserType.ADMIN],
        action="delete documents",
    )

    s3_bucket = S3Bucket(DOCUMENT_STORAGE_BUCKET_NAME, AWSAccessLevel.WRITE)
    document_table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBDocument)
    delete(document_table, s3_bucket, site_id, parent_folder_id, document_id)
    return create_http_response(
        status_code=HTTPStatus.NO_CONTENT.value,
    )


@router.get("/expiring_documents")
def list_expiring_documents_handler(
    days: Annotated[Optional[int], Query()] = None,
    limit: Annotated[Optional[int], Query()] = None,
    start_key: Annotated[Optional[str], Query()] = None,
) -> Response[APIExpiringDocumentResponse]:
    """
    Lists all the documents expiring withing the provided timedelta.

    :param days: Only documents expiring between now and this many days in the future are returned
    :param limit: The maximum amount of site visits to retrieve
    :param start_key: The key to start listing visits from, should be
        obtained from the last_key of a previous request
    :return: The documents that are expiring
    """
    request_time = time_epoch_to_datetime(
        router.current_event["requestContext"]["requestTimeEpoch"]
    )
    verify_user_role(
        user_groups=router.current_event["requestContext"]["authorizer"]["claims"][
            "cognito:groups"
        ],
        acceptable_roles=[UserType.EMPLOYEE, UserType.ADMIN],
        action="list expiring documents",
    )

    decoded_key: Optional[dict] = None
    if start_key:
        key_bytes = base64.urlsafe_b64decode(start_key.encode("utf-8"))
        decoded_key = json.loads(key_bytes)

    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBDocument)
    documents, last_eval_key = list_expiring_documents(
        table=table,
        from_time=request_time,
        days=days,
        limit=limit,
        start_key=decoded_key,
    )

    encoded_key = None
    if last_eval_key:
        key_bytes = json.dumps(last_eval_key).encode("utf-8")
        encoded_key = base64.urlsafe_b64encode(key_bytes).decode("utf-8")

    response_body = APIExpiringDocumentResponse(
        documents=[document.to_api_model() for document in documents], last_key=encoded_key
    )

    return create_http_response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=response_body,
    )
