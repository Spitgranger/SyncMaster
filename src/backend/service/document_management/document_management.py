"""
Module for document management operations
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import uuid4

from aws_lambda_powertools.logging import Logger
from boto3.dynamodb.conditions import Key

from ..database.db_table import GSI, DBTable, KeySchema
from ..environment import DOCUMENT_STORAGE_BUCKET_NAME
from ..exceptions import (
    ResourceConflict,
)
from ..file_storage.s3_bucket import S3Bucket
from ..models.api.document import APIDocumentResponse
from ..models.db.document import DBDocument
from ..util import FileType, ItemType

logger = Logger()


def get_presigned_url(s3_key: str, bucket: S3Bucket) -> dict:
    """
    Function to get create a presigned upload url for a given s3 key
    :param bucket: The S3Bucket containing the files
    :param s3_key: the s3 key to use when identifying this file
    :return: The presigned upload url, encoded as a dictionary
    """
    # To keep it simple for the demo use the name of the file for the key
    # name in s3, won't work in future since you could have multiple folders
    # with the same file name and would have to change this impl.
    upload_url = bucket.create_upload_url(s3_key)

    return upload_url


def get_all_files(
    table: DBTable[DBDocument], bucket: S3Bucket, site_id: str, parent_folder_id: str
) -> List[APIDocumentResponse]:
    """
    Function to get all documents for a given site, contains both files and
    folders under the given parent folder
    :param table: The DB table object to use for this operation
    :param bucket: The S3Bucket containing the files
    :param site_id: The site id to get files for
    :param parent_folder_id: folder to get documents for
    :return: A list of documents in the given folder
    """
    logger.info(site_id)
    key_expression_specific = Key("pk").eq(
        f"{ItemType.DOCUMENT.value}#{site_id}#{parent_folder_id}"
    )

    site_specific_documents, _ = table.query(key_condition_expression=key_expression_specific)
    logger.info(site_specific_documents)

    # split for now, not necessary but the response may change in the future for
    # flexibility
    returned_documents = []
    # returned_site_wide_documents = []
    for document in site_specific_documents:
        presigned_get_url = None
        if document.document_type == FileType.FILE.value:
            presigned_get_url = bucket.create_get_url(document.s3_key)
        api_document = document.to_api_model(presigned_get_url)
        returned_documents.append(api_document)

    return returned_documents


def upload_file(
    table: DBTable[DBDocument],
    document_name: str,
    document_type: FileType,
    parent_folder_id: str,
    site_id: str,
    document_path: str,
    s3_key: str,
    e_tag: str,
    user_id: str,
    requires_ack: bool,
    timestamp: datetime,
    document_expiry: Optional[datetime] = None,
) -> DBDocument:
    """
    Function upload a file to the virtual filesystem, given that is doesn't
    already exist with the same name, note that there are no distinctions
    between folder and file. The distinction will be a property in the document
    itself
    :param table: The DB table object to use for this operation
    :param document_name: The canonical name of the file.
    :param document_type: The type of the file
    :param parent_folder_id: The DB table object to use for this operation
    :param site_id: The site id to upload to
    :param document_path: The absolute path to the file, for this site
    :param s3_key: The key of the file in s3
    :param e_tag: The e_tag of the file in s3
    :param user_id: The user who performed this operation
    :param requires_ack: Does this file require ack
    :param timestamp: The time that this operation was performed
    :param document_expiry: An optional parameter indicating that this document has an expiry
    :return: The document object that was uploaded, including the document id
    :raises ResourceConflict: If a document in the same folder already exists with the same filename
    """
    # Save metadata in DynamoDB
    document = DBDocument(
        document_id=uuid4().hex,
        document_name=document_name,
        document_type=document_type,
        expiry_date=document_expiry,
        parent_folder_id=parent_folder_id,
        document_path=document_path,
        s3_bucket=DOCUMENT_STORAGE_BUCKET_NAME,
        s3_key=s3_key,
        s3_e_tag=e_tag,
        last_modified_by=user_id,
        last_modified_time=timestamp,
        requires_ack=requires_ack,
        site_id=site_id,
    )
    # Query to check if a document with the same name already exists in the folder,
    # since SK is the unique document ID, we need to query to to see if a document
    # with the same name exists in the parent folder.
    key_expression = Key("pk").eq(f"{ItemType.DOCUMENT.value}#{site_id}#{parent_folder_id}")
    existing_docs, _ = table.query(key_condition_expression=key_expression)

    for doc in existing_docs:
        if doc.document_name == document_name:
            raise ResourceConflict(
                resource_type=document.type.value,
                resource_id=str(KeySchema(pk=document.pk, sk=document.document_name)),
            )

    return table.put(item=document)


def delete(
    table: DBTable[DBDocument],
    s3_bucket: S3Bucket,
    site_id: str,
    parent_folder_id: str,
    document_id: str,
) -> None:
    """
    Function to delete a document from the virtual file system. If the provided
    document is a file, it is deleted. If the provided document is a folder, the
    a recursive delete is run through all the files in the folder before
    deleting the folder itself
    :param table: The DB table object to use for this operation
    :param s3_bucket: The S3Bucket containing this file
    :param site_id: The site id to delete from
    :param parent_folder_id: The parent folder that contains the file to be deleted
    :param document_id: The document id to be deleted
    """
    document = table.get(
        {"pk": f"{ItemType.DOCUMENT.value}#{site_id}#{parent_folder_id}", "sk": f"{document_id}"}
    )
    # If the document is a file, delete it
    if document.document_type == FileType.FILE.value:
        s3_bucket.delete(key=document.s3_key, e_tag=document.s3_e_tag)
        table.delete({"pk": document.pk, "sk": document.sk})
    # If the document is a folder, recursively clear the folder, then delete it.
    elif document.document_type == FileType.FOLDER.value:
        key_expression = Key("pk").eq(f"{ItemType.DOCUMENT.value}#{site_id}#{document.document_id}")
        items, _ = table.query(key_condition_expression=key_expression)
        for item in items:
            if item.document_type == FileType.FOLDER.value:
                # recursively delete subfolders
                delete(table, s3_bucket, site_id, document.document_id, item.document_id)
            else:
                s3_bucket.delete(key=item.s3_key, e_tag=item.s3_e_tag)
                table.delete({"pk": item.pk, "sk": item.sk})
        table.delete({"pk": document.pk, "sk": document.sk})


def list_expiring_documents(
    table: DBTable[DBDocument],
    from_time: datetime,
    days: Optional[int] = None,
    limit: Optional[int] = None,
    start_key: Optional[dict] = None,
) -> tuple[list[DBDocument], Optional[dict]]:
    """
    Function to get all documents that are expiring within a given time range, if no days
    are provided, will return the documents that are expiring before the from_time

    :param table: The DBTable object to use to access the database. Requires write access
    :param from_time: The time from which to start looking for expiring documents
    :param days: The number of days from the from_time to look for expiring documents
    :param limit: Maximum number of documents to retrieve from the database
    :param start_key: The key to start getting new documents from
    :return: The list of documents expiring
    :raises ExternalServiceException: An unexpected error occurs in AWS
    """
    key_expression = Key("type").eq(ItemType.DOCUMENT.value)
    # Either query a range starting from today to the future or all before now
    if days:
        key_expression = key_expression & Key("expiry_date").between(
            from_time.isoformat(), (from_time + timedelta(days=days)).isoformat()
        )
    else:
        key_expression = key_expression & Key("expiry_date").lte(from_time.isoformat())
    return table.query(
        gsi=GSI.GSI2,
        key_condition_expression=key_expression,
        limit=limit,
        scan_reverse=True,
        start_key=start_key,
    )
