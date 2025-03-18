import pytest
from backend.service.models.db.site import DBSite

from ....constants import (
    CURRENT_DATE_TIME,
    FUTURE_DATE_TIME,
    TEST_SITE_ID,
    TEST_SITE_ID_ALT,
    TEST_SITE_LATITUDE,
    TEST_SITE_LATITUDE_ALT,
    TEST_SITE_LONGITUDE,
    TEST_SITE_RANGE,
    TEST_USER_ID,
)


@pytest.fixture()
def db_site():
    return DBSite(
        last_modified_by=TEST_USER_ID,
        last_modified_time=CURRENT_DATE_TIME,
        site_id=TEST_SITE_ID,
        longitude=TEST_SITE_LONGITUDE,
        latitude=TEST_SITE_LATITUDE,
        acceptable_range=TEST_SITE_RANGE,
    )


@pytest.fixture()
def db_site_new():
    return DBSite(
        last_modified_by=TEST_USER_ID,
        last_modified_time=CURRENT_DATE_TIME,
        site_id=TEST_SITE_ID_ALT,
        longitude=TEST_SITE_LONGITUDE,
        latitude=TEST_SITE_LATITUDE_ALT,
        acceptable_range=TEST_SITE_RANGE,
    )
