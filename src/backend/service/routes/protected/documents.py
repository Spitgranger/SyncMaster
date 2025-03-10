"""
Routes to associated with document management
"""

import json
from datetime import datetime, timezone
from http import HTTPStatus

from aws_lambda_powertools.event_handler import Response, content_types
from aws_lambda_powertools.event_handler.api_gateway import Router
from aws_lambda_powertools.event_handler.openapi.params import Body, Path, Query
from typing_extensions import Annotated

from ...database.db_table import DBTable
from ...document_management.document_management import (
    delete,
    get_all_files,
    get_presigned_url,
    upload_file,
)
from ...environment import DOCUMENT_STORAGE_BUCKET_NAME
from ...exceptions import InsufficientUserPermissionException
from ...file_storage.s3_bucket import S3Bucket
from ...models.api.document import APIDocumentUploadRequest
from ...models.db.document import DBDocument
from ...util import AWSAccessLevel

router = Router()

cors_headers = {
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, PUT, PATCH, DELETE",
}


@router.post("/upload")
def upload_handler(body: Annotated[APIDocumentUploadRequest, Body()]):
    """
    "Uploads" a file to the virtual file system
    :param body: The body of the HTTP request
    :return: dictionary containing http response
    """
    request_time = datetime.fromtimestamp(
        router.current_event["requestContext"]["requestTimeEpoch"] / 1000, tz=timezone.utc
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
    return Response(
        status_code=HTTPStatus.CREATED.value,
        content_type=content_types.APPLICATION_JSON,
        body=item.to_api_model,
        headers=cors_headers,
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

    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=response_body,
        headers=cors_headers,
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

    return Response(
        status_code=HTTPStatus.CREATED.value,
        content_type=content_types.APPLICATION_JSON,
        body={"s3_presigned_url": url},
        headers=cors_headers,
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
    # Getting role from user claims
    role = router.current_event["requestContext"]["authorizer"]["claims"]["custom:role"]

    # Role check to ensure admin for document deletion
    if role != "admin":
        raise InsufficientUserPermissionException(role=role, action="delete documents")

    s3_bucket = S3Bucket(DOCUMENT_STORAGE_BUCKET_NAME, AWSAccessLevel.WRITE)
    document_table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBDocument)
    delete(document_table, s3_bucket, site_id, parent_folder_id, document_id)
    return Response(
        status_code=HTTPStatus.NO_CONTENT.value,
        headers=cors_headers,
    )
