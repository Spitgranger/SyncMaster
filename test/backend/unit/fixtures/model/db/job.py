import pytest
from ....constants import TEST_JOB_DESCRIPTION, TEST_JOB_TYPE, TEST_USER_ID, TEST_WORK_ORDER

from backend.models.db.job import DBJob


@pytest.fixture()
def db_job_all_attributes():
    return DBJob(
        user_id=TEST_USER_ID,
        job_type=TEST_JOB_TYPE,
        work_order=TEST_WORK_ORDER,
        description=TEST_JOB_DESCRIPTION
    )

@pytest.fixture()
def db_job_no_description():
    return DBJob(
        user_id=TEST_USER_ID,
        job_type=TEST_JOB_TYPE,
        work_order=TEST_WORK_ORDER
    )