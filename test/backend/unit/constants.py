from datetime import datetime, timezone
from decimal import Decimal

TEST_S3_FILE_KEY = "hello.txt"
TEST_S3_FILE_CONTENT = "Hello World"
TEST_USER_ID = "b15b955a-0ffc-4890-9025-49f37bab09f9"
TEST_SITE_ID = "HC059"
TEST_SITE_ID_ALT = "HC309"
TEST_DOCUMENT_PATH = "some/file.txt"
TEST_DOCUMENT_PATH_ALT = "some/file2.txt"
TEST_SITE_LONGITUDE = Decimal("1.0")
TEST_SITE_LATITUDE = Decimal("1.0")
TEST_SITE_LATITUDE_ALT = Decimal("2.0")
TEST_SITE_RANGE = Decimal("100.0")
PREV_DATE_TIME = datetime(
    year=2022, month=1, day=21, hour=11, minute=46, second=12, microsecond=34, tzinfo=timezone.utc
)
CURRENT_DATE_TIME = datetime(
    year=2025, month=1, day=22, hour=11, minute=58, second=12, microsecond=34, tzinfo=timezone.utc
)
FUTURE_DATE_TIME = datetime(
    year=2025, month=1, day=27, hour=11, minute=59, second=12, microsecond=34, tzinfo=timezone.utc
)
