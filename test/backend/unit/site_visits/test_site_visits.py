from datetime import timedelta
from http import HTTPStatus

import pytest
from backend.service.database.db_table import DBTable, KeySchema
from backend.service.environment import DOCUMENT_STORAGE_BUCKET_NAME
from backend.service.exceptions import (
    BadRequestException,
    LimitExceeded,
    ResourceConflict,
    ResourceNotFound,
    TimeConsistencyException,
)
from backend.service.file_storage.s3_bucket import S3Bucket
from backend.service.models.api.site_visit import EditableSiteVisitDetails
from backend.service.models.db.site_visit import DBSiteVisit
from backend.service.site_visits.site_visits import (
    add_exit_time,
    create_file_attachment,
    create_site_entry,
    delete_file_attachment,
    list_site_visits,
    update_visit_details,
)
from backend.service.util import AWSAccessLevel, ItemType
from botocore.exceptions import ClientError

from ..constants import (
    CURRENT_DATE_TIME,
    FUTURE_DATE_TIME,
    PREV_DATE_TIME,
    TEST_ATTACHMENT_NAME,
    TEST_S3_FILE_KEY,
    TEST_SITE_ID,
    TEST_USER_EMAIL,
    TEST_USER_ID,
    TEST_VISIT_DESCRIPTION,
    TEST_WORK_ORDER,
)


def test_create_site_entry(empty_database):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)

    visit = create_site_entry(
        table=table,
        site_id=TEST_SITE_ID,
        user_id=TEST_USER_ID,
        user_email=TEST_USER_EMAIL,
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
            user_email=TEST_USER_EMAIL,
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
        name=TEST_ATTACHMENT_NAME,
        s3_key=TEST_S3_FILE_KEY,
    )
    visit = create_file_attachment(
        table=table,
        site_id=TEST_SITE_ID,
        user_id=TEST_USER_ID,
        entry_time=CURRENT_DATE_TIME,
        timestamp=FUTURE_DATE_TIME + timedelta(seconds=1),
        name="2" + TEST_ATTACHMENT_NAME,
        s3_key="2" + TEST_S3_FILE_KEY,
    )
    assert visit.attachments[TEST_ATTACHMENT_NAME] == TEST_S3_FILE_KEY
    assert visit.attachments["2" + TEST_ATTACHMENT_NAME] == "2" + TEST_S3_FILE_KEY


def test_add_file_attachment_same_name(database_with_two_site_visits):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)
    create_file_attachment(
        table=table,
        site_id=TEST_SITE_ID,
        user_id=TEST_USER_ID,
        entry_time=CURRENT_DATE_TIME,
        timestamp=FUTURE_DATE_TIME,
        name=TEST_ATTACHMENT_NAME,
        s3_key=TEST_S3_FILE_KEY,
    )
    with pytest.raises(ResourceConflict):
        create_file_attachment(
            table=table,
            site_id=TEST_SITE_ID,
            user_id=TEST_USER_ID,
            entry_time=CURRENT_DATE_TIME,
            timestamp=FUTURE_DATE_TIME + timedelta(seconds=1),
            name=TEST_ATTACHMENT_NAME,
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


def test_delete_file_attachment(database_with_two_site_visits, s3_bucket_with_item):
    client, _ = s3_bucket_with_item
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.WRITE)
    updated_visit = delete_file_attachment(
        table=table,
        bucket=bucket,
        site_id=TEST_SITE_ID,
        user_id=TEST_USER_ID,
        entry_time=PREV_DATE_TIME,
        timestamp=FUTURE_DATE_TIME,
        name=TEST_ATTACHMENT_NAME,
    )

    assert TEST_ATTACHMENT_NAME not in updated_visit.attachments

    with pytest.raises(ClientError) as client_error:
        client.head_object(Bucket=bucket.name, Key=TEST_S3_FILE_KEY)

    assert client_error.value.response["Error"]["Code"] == str(HTTPStatus.NOT_FOUND.value)


def test_delete_file_attachment_attachment_does_not_exist_on_visit(
    database_with_two_site_visits, s3_bucket_with_item
):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.WRITE)
    original_visit = table.get(
        key=KeySchema(
            pk=f"{ItemType.SITE_VISIT.value}#{TEST_SITE_ID}#{TEST_USER_ID}",
            sk=CURRENT_DATE_TIME.isoformat(),
        )
    )
    assert TEST_ATTACHMENT_NAME not in original_visit.attachments
    updated_visit = delete_file_attachment(
        table=table,
        bucket=bucket,
        site_id=TEST_SITE_ID,
        user_id=TEST_USER_ID,
        entry_time=CURRENT_DATE_TIME,
        timestamp=FUTURE_DATE_TIME,
        name=TEST_ATTACHMENT_NAME,
    )
    assert original_visit.attachments == updated_visit.attachments


def test_delete_file_attachment_time_consistency_exception(
    database_with_two_site_visits, s3_bucket_with_item
):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.WRITE)
    with pytest.raises(TimeConsistencyException):
        delete_file_attachment(
            table=table,
            bucket=bucket,
            site_id=TEST_SITE_ID,
            user_id=TEST_USER_ID,
            entry_time=PREV_DATE_TIME,
            timestamp=PREV_DATE_TIME,
            name=TEST_ATTACHMENT_NAME,
        )


def test_update_site_visit_details(database_with_two_site_visits):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)
    updated_visit = update_visit_details(
        table=table,
        site_id=TEST_SITE_ID,
        user_id=TEST_USER_ID,
        entry_time=CURRENT_DATE_TIME,
        timestamp=FUTURE_DATE_TIME,
        updated_details=EditableSiteVisitDetails(
            work_order=TEST_WORK_ORDER, description=TEST_VISIT_DESCRIPTION
        ),
    )
    assert updated_visit.description == TEST_VISIT_DESCRIPTION
    assert updated_visit.work_order == TEST_WORK_ORDER

    assert updated_visit == table.get(key=KeySchema(pk=updated_visit.pk, sk=updated_visit.sk))


def test_update_site_visit_details_unset_attributes(database_with_two_site_visits):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)
    updated_visit = update_visit_details(
        table=table,
        site_id=TEST_SITE_ID,
        user_id=TEST_USER_ID,
        entry_time=PREV_DATE_TIME,
        timestamp=FUTURE_DATE_TIME,
        updated_details=EditableSiteVisitDetails(
            work_order=None,
        ),
    )
    assert updated_visit.description == TEST_VISIT_DESCRIPTION
    assert updated_visit.work_order == None

    assert updated_visit == table.get(key=KeySchema(pk=updated_visit.pk, sk=updated_visit.sk))


def test_update_site_visit_details_nothing_to_change(database_with_two_site_visits):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)
    with pytest.raises(BadRequestException):
        update_visit_details(
            table=table,
            site_id=TEST_SITE_ID,
            user_id=TEST_USER_ID,
            entry_time=PREV_DATE_TIME,
            timestamp=FUTURE_DATE_TIME,
            updated_details=EditableSiteVisitDetails(),
        )


def test_update_site_visit_details_time_consistency_exception(database_with_two_site_visits):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)
    with pytest.raises(TimeConsistencyException):
        update_visit_details(
            table=table,
            site_id=TEST_SITE_ID,
            user_id=TEST_USER_ID,
            entry_time=CURRENT_DATE_TIME,
            timestamp=CURRENT_DATE_TIME,
            updated_details=EditableSiteVisitDetails(
                work_order=TEST_WORK_ORDER, description=TEST_VISIT_DESCRIPTION
            ),
        )
