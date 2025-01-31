import pytest
from ....constants import TEST_USER_ID, CURRENT_DATE_TIME, PREV_DATE_TIME, TEST_S3_FILE_KEY, TEST_DOCUMENT_PATH, TEST_SITE_ID

from backend.service.models.db.document import DBDocument
from backend.service.environment import DOCUMENT_STORAGE_BUCKET_NAME


@pytest.fixture()
def db_document(s3_bucket_with_item):
    _, metadata = s3_bucket_with_item
    e_tag = metadata["ETag"]
    return DBDocument(last_modified_by=TEST_USER_ID, last_modified_time=CURRENT_DATE_TIME, document_path=TEST_DOCUMENT_PATH, s3_bucket=DOCUMENT_STORAGE_BUCKET_NAME, s3_key=TEST_S3_FILE_KEY, s3_e_tag=e_tag, requires_ack=True, site_id=TEST_SITE_ID)

@pytest.fixture()
def db_document_old(s3_bucket_with_item):
    _, metadata = s3_bucket_with_item
    e_tag = metadata["ETag"]
    return DBDocument(last_modified_by=TEST_USER_ID, last_modified_time=PREV_DATE_TIME, document_path=TEST_DOCUMENT_PATH, s3_bucket=DOCUMENT_STORAGE_BUCKET_NAME, s3_key=TEST_S3_FILE_KEY, s3_e_tag=e_tag, requires_ack=True, site_id=TEST_SITE_ID)