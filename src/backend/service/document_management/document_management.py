"""
Module for document management operations
"""

from datetime import datetime
from typing import List

from aws_lambda_powertools.logging import Logger
from boto3.dynamodb.conditions import Attr, Key

from ..database.db_table import DBTable, KeySchema
from ..environment import DOCUMENT_STORAGE_BUCKET_NAME
from ..exceptions import (
    ConditionCheckFailed,
    ResourceConflict,
)
from ..file_storage.s3_bucket import S3Bucket
from ..models.api.document import APIDocumentResponse
from ..models.db.document import DBDocument

logger = Logger()


def get_presigned_url(s3_key: str, bucket: S3Bucket) -> str:
    """
    Function to get create a presigned upload url for a given s3 key
    :param bucket: The S3Bucket containing the files
    :param s3_key: the s3 key to use when identifying this file
    """
    # To keep it simple for the demo use the name of the file for the key
    # name in s3, won't work in future since you could have multiple folders
    # with the same file name and would have to change this impl.
    upload_url = bucket.create_upload_url(s3_key)

    return upload_url


def get_all_files(
    table: DBTable[DBDocument], bucket: S3Bucket, site_id: str
) -> List[APIDocumentResponse]:
    """
    Function to get all documents for a given site
    :param table: The DB table object to use for this operation
    :param bucket: The S3Bucket containing the files
    :param site_id: The site id to get files for
    """
    key_expression_specific = Key("pk").eq(f"DOCUMENT#{site_id}")
    key_expression_all = Key("pk").eq("DOCUMENT#ALL")

    site_specific_documents = table.query(key_condition_expression=key_expression_specific)
    site_wide_documents = table.query(key_condition_expression=key_expression_all)

    # split for now, not necessary but the response may change in the future for
    # flexibility
    returned_specific_documents = []
    returned_site_wide_documents = []
    for document in site_specific_documents:
        presigned_get_url = bucket.create_get_url(document.s3_key, document.s3_e_tag)
        api_document = document.to_api_model()
        api_document.s3_presigned_get = presigned_get_url
        returned_specific_documents.append(api_document)

    for document in site_wide_documents:
        presigned_get_url = bucket.create_get_url(document.s3_key, document.s3_e_tag)
        api_document = document.to_api_model()
        api_document.s3_presigned_get = presigned_get_url
        returned_site_wide_documents.append(api_document)

    return returned_specific_documents + returned_site_wide_documents


def upload_file(
    table: DBTable[DBDocument],
    site_id: str,
    document_path: str,
    s3_key: str,
    e_tag: str,
    user_id: str,
    requires_ack: bool,
) -> DBDocument:
    """
    Function upload a file to the virtual filesystem, given that is doesn't
    already exist with the same name
    :param table: The DB table object to use for this operation
    :param site_id: The site id to upload to
    :param document_path: The absolute path to the file, for this site
    :param s3_key: The key of the file in s3
    :param e_tag: The e_tag of the file in s3
    :param user_id: The user who performed this operation
    :param requires_ack: Does this file require ack
    """
    # Save metadata in DynamoDB
    document = DBDocument(
        document_path=document_path,
        s3_bucket=DOCUMENT_STORAGE_BUCKET_NAME,
        s3_key=s3_key,
        s3_e_tag=e_tag,
        last_modified_by=user_id,
        last_modified_time=datetime.now(),
        requires_ack=requires_ack,
        site_id=site_id,
    )
    condition = Attr("pk").not_exists() & Attr("sk").not_exists()
    try:
        return table.put(item=document, condition_expression=condition)
    except ConditionCheckFailed as err:
        logger.exception(err)
        raise ResourceConflict(
            resource_type=document.type.value,
            resource_id=str(KeySchema(pk=document.pk, sk=document.sk)),
        ) from err


def delete_file(
    table: DBTable[DBDocument], s3_bucket: S3Bucket, site_id: str, file_path: str
) -> None:
    """
    Function to delete a file from the virtual file system
    :param table: The DB table object to use for this operation
    :param s3_bucket: The S3Bucket containing this file
    :param file_path: The file path of the file to delete
    :param site_id: The site id to delete from
    """
    document = table.get({"pk": f"DOCUMENT#{site_id}", "sk": file_path})
    s3_bucket.delete(key=document.s3_key, e_tag=document.s3_e_tag)
    table.delete({"pk": document.pk, "sk": document.sk})
