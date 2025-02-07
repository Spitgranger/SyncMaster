"""
Manages the creation, and updating of site visits
"""

from datetime import datetime
from typing import Optional

from aws_lambda_powertools.logging import Logger
from boto3.dynamodb.conditions import Attr, Key

from ..database.db_table import GSI, DBTable, KeySchema
from ..exceptions import (
    ConditionCheckFailed,
    ExitTimeConflict,
    ResourceConflict,
    ResourceNotFound,
    TimeConsistencyException,
)
from ..models.db.site_visit import DBSiteVisit
from ..util import ItemType

logger = Logger()


def create_site_entry(
    table: DBTable[DBSiteVisit], site_id: str, user_id: str, timestamp: datetime
) -> DBSiteVisit:
    """
    Creates a site visit in the database for an initial entry

    :param table: The DBTable object to use to access the database. Requires write access
    :param site_id: The identifier of the site being visited
    :param user_id: The identifier of the user visiting the site
    :param timestamp: The time at which the request for the site entry came in
    :return: The representation of the site visit in the database
    :raises ResourceConflict: There is already a site visit in the database with the same parameters
    :raises ExternalServiceException: An unexpected error occurs in AWS
    :raises PermissionException: The given table does not have write permissions
    """
    item = DBSiteVisit(
        last_modified_by=user_id,
        last_modified_time=timestamp,
        entry_time=timestamp,
        site_id=site_id,
        user_id=user_id,
    )

    condition = Attr("pk").not_exists() & Attr("sk").not_exists()

    try:
        return table.put(item=item, condition_expression=condition)
    except ConditionCheckFailed as err:
        logger.exception(err)
        raise ResourceConflict(
            resource_type=item.type.value, resource_id=str(KeySchema(pk=item.pk, sk=item.sk))
        ) from err


def add_exit_time(
    table: DBTable[DBSiteVisit], site_id: str, user_id: str, timestamp: datetime
) -> DBSiteVisit:
    """
    Updates a site visit in the database with its exit time

    :param table: The DBTable object to use to access the database. Requires write access
    :param site_id: The identifier of the site being visited
    :param user_id: The identifier of the user visiting the site
    :param timestamp: The time at which the request for the site exit came in
    :return: The representation of the site visit in the database
    :raises ResourceNotFound: The user has never visited this site before
    :raises ExitTimeConflict: The user's most recent site entry for this site already
        has an exit time
    :raises TimeConsistencyException: In the time since this update was requested, a new
        update has been made to the entry. Not sure whether to proceed with update
    :raises ExternalServiceException: An unexpected error occurs in AWS
    :raises PermissionException: The given table does not have write permissions
    """
    pk = f"{ItemType.SITE_VISIT.value}#{site_id}#{user_id}"
    key_condition = Key("pk").eq(f"{ItemType.SITE_VISIT.value}#{site_id}#{user_id}")
    items = table.query(key_condition_expression=key_condition, limit=1, scan_reverse=True)

    if not items:
        logger.info(f"No visit found for user [{user_id}] at site [{site_id}]")
        raise ResourceNotFound(resource_type=ItemType.SITE_VISIT.value, resource_id=pk)

    if items[0].exit_time:
        logger.info(
            f"Most recent entry for user [{user_id}] at site [{site_id}] already has a logged exit"
        )
        raise ExitTimeConflict(site_id=site_id, user_id=user_id)

    key = KeySchema(pk=items[0].pk, sk=items[0].sk)

    try:
        return table.update(
            key=key,
            update_attributes={"exit_time": timestamp.isoformat()},
            last_modified_by=user_id,
            last_modified_time=timestamp,
            condition_expression=Attr("last_modified_time").lt(timestamp.isoformat()),
        )
    except ConditionCheckFailed as err:
        logger.exception(err)
        raise TimeConsistencyException(key=str(key), timestamp=timestamp) from err


def list_site_visits(
    table: DBTable[DBSiteVisit],
    from_time: Optional[datetime] = None,
    to_time: Optional[datetime] = None,
    limit: Optional[int] = None,
) -> list[DBSiteVisit]:
    """
    Updates a site visit in the database with its exit time

    :param table: The DBTable object to use to access the database. Requires write access
    :param from_time: All items found in the query must have been last modified after
        this time
    :param to_time: All items found in the query must have been last modified before
        this time
    :param limit: Maximum number of visits to retrieve from the database
    :return: The list of site visits matching the criteria
    :raises ExternalServiceException: An unexpected error occurs in AWS
    """

    key_expression = Key("type").eq(ItemType.SITE_VISIT.value)
    if from_time:
        key_expression = key_expression & Key("last_modified_time").gte(from_time.isoformat())
    if to_time:
        key_expression = key_expression & Key("last_modified_time").lte(to_time.isoformat())
    return table.query(
        gsi=GSI.GSI1,
        key_condition_expression=key_expression,
        limit=limit,
        scan_reverse=True,
    )
