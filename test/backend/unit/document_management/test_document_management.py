import pytest
from backend.service.database.db_table import DBTable, KeySchema
from backend.service.document_management.document_management import (
    delete,
    get_all_files,
    get_presigned_url,
    upload_file,
)
from backend.service.environment import DOCUMENT_STORAGE_BUCKET_NAME
from backend.service.exceptions import (
    ResourceConflict,
    ResourceNotFound,
    TimeConsistencyException,
)
from backend.service.file_storage.s3_bucket import S3Bucket
from backend.service.models.db.document import DBDocument
from backend.service.models.db.site_visit import DBSiteVisit
from backend.service.site_visits.site_visits import (
    add_exit_time,
    create_site_entry,
    list_site_visits,
)
from backend.service.util import AWSAccessLevel, FileType
from requests import get

from ..constants import (
    CURRENT_DATE_TIME,
    FUTURE_DATE_TIME,
    PREV_DATE_TIME,
    TEST_DOCUMENT_ETAG,
    TEST_DOCUMENT_FOLDER_ID,
    TEST_DOCUMENT_ID,
    TEST_DOCUMENT_NAME,
    TEST_DOCUMENT_PATH,
    TEST_PARENT_FOLDER_ID,
    TEST_S3_FILE_KEY,
    TEST_SITE_ID,
    TEST_USER_ID,
)


def test_create_document(empty_database):
    """
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
    document_expiry: Optional[datetime] = None,"
    """
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBDocument)
    document = upload_file(
        table=table,
        document_name=TEST_DOCUMENT_NAME,
        document_type=FileType.FILE,
        parent_folder_id=TEST_PARENT_FOLDER_ID,
        site_id=TEST_SITE_ID,
        document_path=TEST_DOCUMENT_PATH,
        s3_key=TEST_S3_FILE_KEY,
        e_tag=TEST_DOCUMENT_ETAG,
        user_id=TEST_USER_ID,
        requires_ack=False,
        timestamp=CURRENT_DATE_TIME,
        document_expiry=None,
    )

    table.put(document)

    assert table.get(key=KeySchema(pk=document.pk, sk=document.sk)) == document


def test_create_document_with_resource_conflict(database_with_document):
    base_resource, document = database_with_document
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBDocument)
    with pytest.raises(ResourceConflict):
        upload_file(
            table=table,
            document_name=document.document_name,
            document_type=document.document_type,
            parent_folder_id=document.parent_folder_id,
            site_id=document.site_id,
            document_path=document.document_path,
            s3_key=document.s3_key,
            e_tag=document.s3_e_tag,
            user_id=document.last_modified_by,
            requires_ack=document.requires_ack,
            timestamp=document.last_modified_time,
            document_expiry=document.document_expiry,
        )


def test_get_all_files(database_with_document, s3_bucket_with_item):
    client, metadata = s3_bucket_with_item

    # Initialize bucket wrapper
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.WRITE)
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBDocument)
    files = get_all_files(
        table=table, bucket=bucket, site_id=TEST_SITE_ID, parent_folder_id=TEST_PARENT_FOLDER_ID
    )
    assert len(files) == 1
    assert files[0].document_name == TEST_DOCUMENT_NAME
    assert files[0].document_path == TEST_DOCUMENT_PATH


def test_get_all_multiple_files(database_with_documents_and_folders, s3_bucket_with_item):
    client, metadata = s3_bucket_with_item

    # Initialize bucket wrapper
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.WRITE)
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBDocument)
    files = get_all_files(
        table=table, bucket=bucket, site_id=TEST_SITE_ID, parent_folder_id=TEST_PARENT_FOLDER_ID
    )
    assert len(files) == 2
    assert files[0].document_name == TEST_DOCUMENT_NAME
    assert files[0].document_path == TEST_DOCUMENT_PATH


def test_get_all_files_empty(empty_database, empty_s3_bucket):
    client = empty_s3_bucket

    # Initialize bucket wrapper
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.READ)
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBDocument)
    files = get_all_files(
        table=table, bucket=bucket, site_id=TEST_SITE_ID, parent_folder_id=TEST_PARENT_FOLDER_ID
    )
    assert len(files) == 0


def test_get_presigned_upload_url(empty_s3_bucket):
    client = empty_s3_bucket

    # Initialize bucket wrapper
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.WRITE)
    url = get_presigned_url(bucket=bucket, s3_key=TEST_S3_FILE_KEY)
    assert url


def test_delete_file(database_with_document, s3_bucket_with_item):
    client, metadata = s3_bucket_with_item
    base_resource, document = database_with_document
    # Initialize bucket wrapper
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.WRITE)
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBDocument)
    delete(
        table=table,
        s3_bucket=bucket,
        site_id=TEST_SITE_ID,
        parent_folder_id=TEST_PARENT_FOLDER_ID,
        document_id=TEST_DOCUMENT_ID,
    )
    items: list[dict] = base_resource.scan()["Items"]
    assert len(items) == 0


def test_delete_folder(database_with_documents_and_folders, s3_bucket_with_item):
    base_resource, _, _, _, _ = database_with_documents_and_folders
    # Initialize bucket wrapper
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.WRITE)
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBDocument)
    delete(
        table=table,
        s3_bucket=bucket,
        site_id=TEST_SITE_ID,
        parent_folder_id=TEST_PARENT_FOLDER_ID,
        document_id=TEST_DOCUMENT_FOLDER_ID,
    )
    items: list[dict] = base_resource.scan()["Items"]
    assert len(items) == 1
