import pytest
from backend.service.models.db.user_request import DBUserRequest

from ....constants import (
    CURRENT_DATE_TIME,
    TEST_COMPANY_NAME,
    TEST_USER_EMAIL,
    TEST_USER_EMAIL_ALT,
    TEST_USER_NAME,
    TEST_USER_ROLE,
)


@pytest.fixture()
def db_user_request():
    return DBUserRequest(
        email=TEST_USER_EMAIL,
        company=TEST_COMPANY_NAME,
        name=TEST_USER_NAME,
        role_requested=TEST_USER_ROLE,
        last_modified_by="system",
        last_modified_time=CURRENT_DATE_TIME,
    )


@pytest.fixture()
def db_user_request_new():
    return DBUserRequest(
        email=TEST_USER_EMAIL_ALT,
        company=TEST_COMPANY_NAME,
        name=TEST_USER_NAME,
        role_requested=TEST_USER_ROLE,
        last_modified_by="system",
        last_modified_time=CURRENT_DATE_TIME,
    )
