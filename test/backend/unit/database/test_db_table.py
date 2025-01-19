
from backend.database.db_table import DBTable
from backend.models.db.job import DBJob
from backend.environment import JOB_TABLE_NAME, JOB_TABLE_WRITE_ROLE

from ..constants import TEST_JOB_DESCRIPTION, TEST_JOB_TYPE, TEST_USER_ID, TEST_WORK_ORDER

def test_put_item(empty_job_database):
    job = DBJob(user_id=TEST_USER_ID, job_type=TEST_JOB_TYPE, work_order=TEST_WORK_ORDER, description=TEST_JOB_DESCRIPTION)

    table = DBTable(table_name=JOB_TABLE_NAME, role=JOB_TABLE_WRITE_ROLE, item_schema=DBJob)

    table.put(item=job)

    assert table.get(key=DBJob.create_key(work_order=job.work_order)) == job

