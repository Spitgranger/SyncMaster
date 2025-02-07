import pytest
from backend.service.models.db.site_visit import DBSiteVisit

from ....constants import (
    CURRENT_DATE_TIME,
    PREV_DATE_TIME,
    TEST_DOCUMENT_PATH,
    TEST_S3_FILE_KEY,
    TEST_SITE_ID,
    TEST_USER_ID,
)


@pytest.fixture()
def db_site_visit_complete():
    return DBSiteVisit(
        last_modified_by=TEST_USER_ID,
        last_modified_time=CURRENT_DATE_TIME,
        site_id=TEST_SITE_ID,
        user_id=TEST_USER_ID,
        entry_time=PREV_DATE_TIME,
        exit_time=CURRENT_DATE_TIME,
    )


@pytest.fixture()
def db_site_visit_only_entry():
    return DBSiteVisit(
        last_modified_by=TEST_USER_ID,
        last_modified_time=CURRENT_DATE_TIME,
        site_id=TEST_SITE_ID,
        user_id=TEST_USER_ID,
        entry_time=CURRENT_DATE_TIME,
    )
