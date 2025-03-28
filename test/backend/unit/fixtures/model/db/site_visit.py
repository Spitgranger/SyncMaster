import pytest
from backend.service.models.db.site_visit import DBSiteVisit

from ....constants import (
    CURRENT_DATE_TIME,
    PREV_DATE_TIME,
    TEST_ATTACHMENT_NAME,
    TEST_EMPLOYEE_ID,
    TEST_S3_FILE_KEY,
    TEST_SITE_ID,
    TEST_USER_EMAIL,
    TEST_USER_ID,
    TEST_VISIT_DESCRIPTION,
    TEST_WORK_ORDER,
)


@pytest.fixture()
def db_site_visit_complete():
    return DBSiteVisit(
        last_modified_by=TEST_USER_ID,
        last_modified_time=CURRENT_DATE_TIME,
        site_id=TEST_SITE_ID,
        user_id=TEST_USER_ID,
        user_email=TEST_USER_EMAIL,
        entry_time=PREV_DATE_TIME,
        exit_time=CURRENT_DATE_TIME,
        loc_tracking=True,
        ack_status=True,
        on_site=True,
        work_order=TEST_WORK_ORDER,
        description=TEST_VISIT_DESCRIPTION,
        employee_id=TEST_EMPLOYEE_ID,
        attachments={TEST_ATTACHMENT_NAME: TEST_S3_FILE_KEY},
    )


@pytest.fixture()
def db_site_visit_only_entry():
    return DBSiteVisit(
        last_modified_by=TEST_USER_ID,
        last_modified_time=CURRENT_DATE_TIME,
        site_id=TEST_SITE_ID,
        user_id=TEST_USER_ID,
        user_email=TEST_USER_EMAIL,
        entry_time=CURRENT_DATE_TIME,
        loc_tracking=True,
        ack_status=True,
        on_site=True,
        employee_id=TEST_EMPLOYEE_ID,
    )
