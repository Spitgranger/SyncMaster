import pytest
from backend.service.database.db_table import DBTable, KeySchema
from backend.service.exceptions import (
    ExitTimeConflict,
    ResourceConflict,
    ResourceNotFound,
    TimeConsistencyException,
)
from backend.service.models.db.site_visit import DBSiteVisit
from backend.service.site_visits.site_visits import (
    add_exit_time,
    create_site_entry,
    list_site_visits,
)
from backend.service.util import AWSAccessLevel

from ..constants import (
    CURRENT_DATE_TIME,
    FUTURE_DATE_TIME,
    PREV_DATE_TIME,
    TEST_SITE_ID,
    TEST_USER_ID,
)


def test_create_site_entry(empty_database):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)

    visit = create_site_entry(
        table=table, site_id=TEST_SITE_ID, user_id=TEST_USER_ID, timestamp=CURRENT_DATE_TIME
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
        )


def test_add_exit_time(database_with_two_site_visits):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)

    updated_visit = add_exit_time(
        table=table, site_id=TEST_SITE_ID, user_id=TEST_USER_ID, timestamp=FUTURE_DATE_TIME
    )

    assert table.get(key=KeySchema(pk=updated_visit.pk, sk=updated_visit.sk)) == updated_visit


def test_add_exit_time_with_time_consistency_exception(database_with_two_site_visits):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)

    with pytest.raises(TimeConsistencyException):
        add_exit_time(
            table=table, site_id=TEST_SITE_ID, user_id=TEST_USER_ID, timestamp=PREV_DATE_TIME
        )


def test_add_exit_time_with_exit_time_conflict(database_with_complete_site_visit):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)

    with pytest.raises(ExitTimeConflict):
        add_exit_time(
            table=table, site_id=TEST_SITE_ID, user_id=TEST_USER_ID, timestamp=FUTURE_DATE_TIME
        )


def test_add_exit_time_with_resource_not_found(empty_database):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)

    with pytest.raises(ResourceNotFound):
        add_exit_time(
            table=table, site_id=TEST_SITE_ID, user_id=TEST_USER_ID, timestamp=FUTURE_DATE_TIME
        )


def test_list_site_entries(database_with_two_site_visits):
    _, set_of_visits = database_with_two_site_visits
    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBSiteVisit)

    visits = list_site_visits(
        table=table,
        from_time=PREV_DATE_TIME,
        to_time=FUTURE_DATE_TIME,
        limit=10,
    )

    assert len(visits) == 2
    assert set(visits) == set_of_visits
