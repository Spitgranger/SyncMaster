from datetime import timedelta

import pytest
from backend.service.database.db_table import DBTable, KeySchema
from backend.service.exceptions import (
    LimitExceeded,
    ResourceConflict,
    ResourceNotFound,
    TimeConsistencyException,
)
from backend.service.models.db.site_visit import DBSiteVisit
from backend.service.site_visits.site_visits import (
    add_exit_time,
    create_file_attachment,
    create_site_entry,
    delete_file_attachment,
    list_site_visits,
)
from backend.service.util import AWSAccessLevel

from ..constants import (
    CURRENT_DATE_TIME,
    FUTURE_DATE_TIME,
    PREV_DATE_TIME,
    TEST_S3_FILE_KEY,
    TEST_SITE_ID,
    TEST_USER_ID,
)


def test_create_site_entry(empty_database):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)

    visit = create_site_entry(
        table=table,
        site_id=TEST_SITE_ID,
        user_id=TEST_USER_ID,
        timestamp=CURRENT_DATE_TIME,
        loc_tracking=True,
        ack_status=True,
        on_site=True,
    )

    assert table.get(key=KeySchema(pk=visit.pk, sk=visit.sk)) == visit


def test_create_site_entry_with_resource_conflict(database_with_complete_site_visit):
    _, site_visit = database_with_complete_site_visit
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)

    with pytest.raises(ResourceConflict):
        create_site_entry(
            table=table,
            site_id=site_visit.site_id,
            user_id=site_visit.user_id,
            timestamp=site_visit.entry_time,
            loc_tracking=True,
            ack_status=True,
            on_site=True,
        )


def test_add_exit_time(database_with_two_site_visits):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)

    updated_visit = add_exit_time(
        table=table,
        site_id=TEST_SITE_ID,
        user_id=TEST_USER_ID,
        timestamp=FUTURE_DATE_TIME,
        entry_time=CURRENT_DATE_TIME,
    )

    assert table.get(key=KeySchema(pk=updated_visit.pk, sk=updated_visit.sk)) == updated_visit


def test_add_exit_time_with_resource_not_found(empty_database):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)

    with pytest.raises(ResourceNotFound):
        add_exit_time(
            table=table,
            site_id=TEST_SITE_ID,
            user_id=TEST_USER_ID,
            timestamp=FUTURE_DATE_TIME,
            entry_time=CURRENT_DATE_TIME,
        )


def test_list_site_entries(database_with_two_site_visits):
    _, set_of_visits = database_with_two_site_visits
    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBSiteVisit)

    visits, _ = list_site_visits(
        table=table,
        from_time=PREV_DATE_TIME,
        to_time=FUTURE_DATE_TIME,
        limit=10,
    )

    assert len(visits) == 2
    for visit in visits:
        assert visit in set_of_visits


def test_list_site_entries_to_early_time(database_with_two_site_visits):
    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBSiteVisit)

    visits, _ = list_site_visits(
        table=table,
        to_time=PREV_DATE_TIME,
    )

    assert len(visits) == 0


def test_list_site_entries_from_future_time(database_with_two_site_visits):
    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBSiteVisit)

    visits, _ = list_site_visits(
        table=table,
        from_time=FUTURE_DATE_TIME,
    )

    assert len(visits) == 0


def test_list_site_entries_paginated(database_with_two_site_visits):
    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBSiteVisit)

    visits, last_eval = list_site_visits(
        table=table,
        limit=1,
    )

    assert len(visits) == 1
    assert last_eval is not None

    visits, last_eval = list_site_visits(table=table, limit=1, start_key=last_eval)

    assert len(visits) == 1
    assert last_eval is None


def test_add_file_attachment(database_with_two_site_visits):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)
    create_file_attachment(
        table=table,
        site_id=TEST_SITE_ID,
        user_id=TEST_USER_ID,
        entry_time=CURRENT_DATE_TIME,
        timestamp=FUTURE_DATE_TIME,
        name="text.txt",
        s3_key=TEST_S3_FILE_KEY,
    )
    visit = create_file_attachment(
        table=table,
        site_id=TEST_SITE_ID,
        user_id=TEST_USER_ID,
        entry_time=CURRENT_DATE_TIME,
        timestamp=FUTURE_DATE_TIME + timedelta(seconds=1),
        name="text2.txt",
        s3_key="2" + TEST_S3_FILE_KEY,
    )
    assert visit.attachments["text.txt"] == TEST_S3_FILE_KEY
    assert visit.attachments["text2.txt"] == "2" + TEST_S3_FILE_KEY


def test_add_file_attachment_same_name(database_with_two_site_visits):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)
    create_file_attachment(
        table=table,
        site_id=TEST_SITE_ID,
        user_id=TEST_USER_ID,
        entry_time=CURRENT_DATE_TIME,
        timestamp=FUTURE_DATE_TIME,
        name="text.txt",
        s3_key=TEST_S3_FILE_KEY,
    )
    with pytest.raises(ResourceConflict):
        create_file_attachment(
            table=table,
            site_id=TEST_SITE_ID,
            user_id=TEST_USER_ID,
            entry_time=CURRENT_DATE_TIME,
            timestamp=FUTURE_DATE_TIME + timedelta(seconds=1),
            name="text.txt",
            s3_key="2" + TEST_S3_FILE_KEY,
        )


def test_add_file_attachment_exceeds_limit(database_with_two_site_visits):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)
    # Add 10 attachments (end of range is disclusive so ends at 10)
    for i in range(1, 11):
        create_file_attachment(
            table=table,
            site_id=TEST_SITE_ID,
            user_id=TEST_USER_ID,
            entry_time=CURRENT_DATE_TIME,
            timestamp=CURRENT_DATE_TIME + timedelta(seconds=i),
            name=f"text{i}.txt",
            s3_key=f"s3_key{i}",
        )
    # See failure when adding the 11th
    with pytest.raises(LimitExceeded):
        create_file_attachment(
            table=table,
            site_id=TEST_SITE_ID,
            user_id=TEST_USER_ID,
            entry_time=CURRENT_DATE_TIME,
            timestamp=CURRENT_DATE_TIME + timedelta(seconds=20),
            name=f"text_final.txt",
            s3_key=f"s3_key_final",
        )
