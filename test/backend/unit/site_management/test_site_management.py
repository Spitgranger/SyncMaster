import pytest
from backend.service.database.db_table import DBTable, KeySchema
from backend.service.exceptions import (
    BadRequestException,
    ResourceConflict,
    ResourceNotFound,
    TimeConsistencyException,
)
from backend.service.models.db.document import DBDocument
from backend.service.models.db.site import DBSite
from backend.service.site_management.site_management import (
    create_site,
    delete_site,
    get_site,
    list_sites,
    update_site,
)
from backend.service.util import AWSAccessLevel

from ..constants import (
    CURRENT_DATE_TIME,
    FUTURE_DATE_TIME,
    PREV_DATE_TIME,
    TEST_SITE_ID,
    TEST_SITE_LATITUDE,
    TEST_SITE_LATITUDE_ALT,
    TEST_SITE_LONGITUDE,
    TEST_SITE_RANGE,
    TEST_USER_ID,
)


def test_create_site(empty_database):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSite)

    site = create_site(
        table=table,
        site_id=TEST_SITE_ID,
        longitude=TEST_SITE_LONGITUDE,
        latitude=TEST_SITE_LATITUDE,
        acceptable_range=TEST_SITE_RANGE,
        user_id=TEST_USER_ID,
        timestamp=CURRENT_DATE_TIME,
    )

    assert table.get(key=KeySchema(pk=site.pk, sk=site.sk)) == site


def test_create_site_with_conflict(database_with_site):
    resource, site = database_with_site
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSite)

    with pytest.raises(ResourceConflict):
        create_site(
            table=table,
            site_id=TEST_SITE_ID,
            longitude=TEST_SITE_LONGITUDE,
            latitude=TEST_SITE_LATITUDE,
            acceptable_range=TEST_SITE_RANGE,
            user_id=TEST_USER_ID,
            timestamp=CURRENT_DATE_TIME,
        )


def test_update_site(database_with_site):
    resource, old_site = database_with_site
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSite)

    new_site = update_site(
        table=table,
        timestamp=FUTURE_DATE_TIME,
        user_id=TEST_USER_ID,
        site_id=TEST_SITE_ID,
        latitude=TEST_SITE_LATITUDE_ALT,
    )

    site = table.get(key=KeySchema(pk=old_site.pk, sk=old_site.sk))
    assert site != old_site
    assert site == new_site


def test_update_site_time_consistency_error(database_with_site):
    resource, old_site = database_with_site
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSite)

    with pytest.raises(TimeConsistencyException):
        update_site(
            table=table,
            timestamp=PREV_DATE_TIME,
            user_id=TEST_USER_ID,
            site_id=TEST_SITE_ID,
            latitude=TEST_SITE_LATITUDE_ALT,
        )

    site = table.get(key=KeySchema(pk=old_site.pk, sk=old_site.sk))
    assert site == old_site


def test_delete_site(database_with_site):
    resource, old_site = database_with_site
    site_table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSite)
    document_table = DBTable(access=AWSAccessLevel.READ, item_schema=DBDocument)

    delete_site(
        site_table=site_table,
        document_table=document_table,
        site_id=TEST_SITE_ID,
        timestamp=FUTURE_DATE_TIME,
    )

    with pytest.raises(ResourceNotFound):
        site_table.get(key=KeySchema(pk=old_site.pk, sk=old_site.sk))


def test_delete_site_document_exists(database_with_site, database_with_document):
    resource, old_site = database_with_site
    site_table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSite)
    document_table = DBTable(access=AWSAccessLevel.READ, item_schema=DBDocument)

    with pytest.raises(BadRequestException):
        delete_site(
            site_table=site_table,
            document_table=document_table,
            site_id=TEST_SITE_ID,
            timestamp=FUTURE_DATE_TIME,
        )

    assert site_table.get(key=KeySchema(pk=old_site.pk, sk=old_site.sk)) == old_site


def test_delete_site_time_consistency_error(database_with_site):
    resource, old_site = database_with_site
    site_table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSite)
    document_table = DBTable(access=AWSAccessLevel.READ, item_schema=DBDocument)

    with pytest.raises(TimeConsistencyException):
        delete_site(
            site_table=site_table,
            document_table=document_table,
            site_id=TEST_SITE_ID,
            timestamp=PREV_DATE_TIME,
        )


def test_get_site(database_with_site):
    resource, site = database_with_site
    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBSite)
    assert site == get_site(table=table, site_id=site.site_id)


def test_get_site_not_found(empty_database):
    resource = empty_database
    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBSite)
    with pytest.raises(ResourceNotFound):
        get_site(table=table, site_id=TEST_SITE_ID)


def test_list_sites(database_with_two_sites):
    resource, sites = database_with_two_sites
    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBSite)

    result, _ = list_sites(table=table)

    assert set(result) == sites


def test_list_sites_paginated(database_with_two_sites):
    resource, sites = database_with_two_sites
    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBSite)

    result, key = list_sites(table=table, limit=1)
    assert len(result) == 1
    assert result[0] in sites
    assert key is not None

    result, key = list_sites(table=table, limit=1, start_key=key)
    assert len(result) == 1
    assert result[0] in sites
    assert key is None
