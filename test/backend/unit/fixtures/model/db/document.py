from datetime import datetime

import pytest
from backend.service.environment import DOCUMENT_STORAGE_BUCKET_NAME
from backend.service.models.db.document import DBDocument
from backend.service.util import FileType

from ....constants import (
    CURRENT_DATE_TIME,
    PREV_DATE_TIME,
    TEST_DOCUMENT_FOLDER_ID,
    TEST_DOCUMENT_FOLDER_IN_FOLDER_ID,
    TEST_DOCUMENT_ID,
    TEST_DOCUMENT_IN_FOLDER_ID,
    TEST_DOCUMENT_NAME,
    TEST_DOCUMENT_PATH,
    TEST_PARENT_FOLDER_ID,
    TEST_S3_FILE_KEY,
    TEST_SITE_ID,
    TEST_USER_ID,
)


@pytest.fixture()
def db_document(s3_bucket_with_item):
    _, metadata = s3_bucket_with_item
    e_tag = metadata["ETag"]
    return DBDocument(
        parent_folder_id=TEST_PARENT_FOLDER_ID,
        document_id=TEST_DOCUMENT_ID,
        document_name=TEST_DOCUMENT_NAME,
        document_type=FileType.FILE,
        last_modified_by=TEST_USER_ID,
        last_modified_time=CURRENT_DATE_TIME,
        document_path=TEST_DOCUMENT_PATH,
        s3_bucket=DOCUMENT_STORAGE_BUCKET_NAME,
        expiry_date=CURRENT_DATE_TIME,
        s3_key=TEST_S3_FILE_KEY,
        s3_e_tag=e_tag,
        requires_ack=True,
        site_id=TEST_SITE_ID,
    )


@pytest.fixture()
def db_document_folder(s3_bucket_with_item):
    _, metadata = s3_bucket_with_item
    e_tag = metadata["ETag"]
    return DBDocument(
        parent_folder_id=TEST_PARENT_FOLDER_ID,
        document_id=TEST_DOCUMENT_FOLDER_ID,
        document_name=TEST_DOCUMENT_NAME,
        document_type=FileType.FOLDER,
        last_modified_by=TEST_USER_ID,
        last_modified_time=CURRENT_DATE_TIME,
        document_path=TEST_DOCUMENT_PATH,
        s3_bucket=DOCUMENT_STORAGE_BUCKET_NAME,
        s3_key=TEST_S3_FILE_KEY,
        s3_e_tag=e_tag,
        requires_ack=True,
        site_id=TEST_SITE_ID,
    )


@pytest.fixture()
def db_document_folder_in_folder(s3_bucket_with_item):
    _, metadata = s3_bucket_with_item
    e_tag = metadata["ETag"]
    return DBDocument(
        parent_folder_id=TEST_DOCUMENT_FOLDER_ID,
        document_id=TEST_DOCUMENT_FOLDER_IN_FOLDER_ID,
        document_name=TEST_DOCUMENT_NAME,
        document_type=FileType.FOLDER,
        last_modified_by=TEST_USER_ID,
        last_modified_time=CURRENT_DATE_TIME,
        document_path=TEST_DOCUMENT_PATH,
        s3_bucket=DOCUMENT_STORAGE_BUCKET_NAME,
        s3_key=TEST_S3_FILE_KEY,
        s3_e_tag=e_tag,
        requires_ack=True,
        site_id=TEST_SITE_ID,
    )


@pytest.fixture()
def db_document_file_in_folder(s3_bucket_with_item):
    _, metadata = s3_bucket_with_item
    e_tag = metadata["ETag"]
    return DBDocument(
        parent_folder_id=TEST_DOCUMENT_FOLDER_ID,
        document_id=TEST_DOCUMENT_IN_FOLDER_ID,
        document_name=TEST_DOCUMENT_NAME,
        document_type=FileType.FILE,
        last_modified_by=TEST_USER_ID,
        last_modified_time=CURRENT_DATE_TIME,
        document_path=TEST_DOCUMENT_PATH,
        expiry_date=CURRENT_DATE_TIME,
        s3_bucket=DOCUMENT_STORAGE_BUCKET_NAME,
        s3_key=TEST_S3_FILE_KEY,
        s3_e_tag=e_tag,
        requires_ack=True,
        site_id=TEST_SITE_ID,
    )


@pytest.fixture()
def db_document_old(s3_bucket_with_item):
    _, metadata = s3_bucket_with_item
    e_tag = metadata["ETag"]
    return DBDocument(
        parent_folder_id=TEST_PARENT_FOLDER_ID,
        document_id=TEST_DOCUMENT_ID,
        document_name=TEST_DOCUMENT_NAME,
        document_type=FileType.FILE,
        last_modified_by=TEST_USER_ID,
        last_modified_time=PREV_DATE_TIME,
        document_path=TEST_DOCUMENT_PATH,
        s3_bucket=DOCUMENT_STORAGE_BUCKET_NAME,
        s3_key=TEST_S3_FILE_KEY,
        s3_e_tag=e_tag,
        requires_ack=True,
        site_id=TEST_SITE_ID,
    )
