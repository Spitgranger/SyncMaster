from datetime import datetime, timezone

TEST_S3_FILE_KEY = "hello.txt"
TEST_S3_FILE_CONTENT = "Hello World"
TEST_USER_ID = "b15b955a-0ffc-4890-9025-49f37bab09f9"
TEST_SITE_ID = "HC059"
TEST_DOCUMENT_PATH = "some/file.txt"
TEST_DOCUMENT_PATH_ALT = "some/file2.txt"
TEST_PARENT_FOLDER_ID = "root"
TEST_DOCUMENT_ID = "18a9892797a9s9d9"
TEST_DOCUMENT_FOLDER_ID = "912fdaf8131333f"
TEST_DOCUMENT_FOLDER_IN_FOLDER_ID = "24f323423adfadf3fkj"
TEST_DOCUMENT_IN_FOLDER_ID = "41242daf8131333f"
TEST_DOCUMENT_NAME = "Test.file"
TEST_DOCUMENT_ETAG = "1234"
PREV_DATE_TIME = datetime(
    year=2022, month=1, day=21, hour=11, minute=46, second=12, microsecond=34, tzinfo=timezone.utc
)
CURRENT_DATE_TIME = datetime(
    year=2025, month=1, day=22, hour=11, minute=58, second=12, microsecond=34, tzinfo=timezone.utc
)
FUTURE_DATE_TIME = datetime(
    year=2025, month=1, day=27, hour=11, minute=59, second=12, microsecond=34, tzinfo=timezone.utc
)
