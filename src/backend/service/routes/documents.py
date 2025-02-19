"""
Routes to associated with user management and authentication
"""

import json
from http import HTTPStatus

from aws_lambda_powertools.event_handler import Response, content_types
from aws_lambda_powertools.event_handler.api_gateway import Router
from aws_lambda_powertools.event_handler.openapi.params import Body, Path, Query
from typing_extensions import Annotated

from ..database.db_table import DBTable
from ..document_management.document_management import (
    delete_file,
    get_all_files,
    get_presigned_url,
    upload_file,
)
from ..environment import DOCUMENT_STORAGE_BUCKET_NAME
from ..file_storage.s3_bucket import S3Bucket
from ..models.api.document import APIDocumentUploadRequest
from ..models.db.document import DBDocument
from ..util import AWSAccessLevel

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
    document_table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBDocument)
    item = upload_file(
        document_table,
        body.site_id,
        body.document_path,
        body.s3_key,
        body.e_tag,
        body.user_id,
        body.requires_ack,
    )
    return Response(
        status_code=HTTPStatus.CREATED.value,
        content_type=content_types.APPLICATION_JSON,
        body=item.to_api_model,
        headers=cors_headers,
    )


@router.get("/<site_id>/get_files")
def get_files_handler(site_id: Annotated[str, Path()]):
    """
    Route to get files for a specific site
    :param site_id: The site id to get documents for
    :return: dictionary containing http response
    """
    s3_bucket = S3Bucket(DOCUMENT_STORAGE_BUCKET_NAME, AWSAccessLevel.READ)
    document_table = DBTable(access=AWSAccessLevel.READ, item_schema=DBDocument)

    files = get_all_files(document_table, s3_bucket, site_id)

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
def delete_file_handler(site_id: Annotated[str, Query()], file_path: Annotated[str, Query()]):
    """
    Route to get files for a specific site
    :param site_id: The site containg the file to be deleted
    :param file_path: The path to the file to be deleted
    :return: dictionary containing http response
    """
    s3_bucket = S3Bucket(DOCUMENT_STORAGE_BUCKET_NAME, AWSAccessLevel.WRITE)
    document_table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBDocument)
    delete_file(document_table, s3_bucket, file_path, site_id)
    return Response(
        status_code=HTTPStatus.NO_CONTENT.value,
        headers=cors_headers,
    )
