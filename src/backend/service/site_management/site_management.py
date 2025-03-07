from datetime import datetime
from typing import Optional

from aws_lambda_powertools.logging import Logger
from boto3.dynamodb.conditions import Attr, Key

from ..database.db_table import GSI, DBTable, KeySchema
from ..exceptions import ConditionCheckFailed, ResourceConflict, TimeConsistencyException
from ..models.db.site import DBSite
from ..util import ItemType

logger = Logger()


def create_site(
    table: DBTable[DBSite],
    site_id: str,
    longitude: float,
    latitude: float,
    acceptable_range: float,
    timestamp: datetime,
    user_id: str,
) -> DBSite:
    """
    Create a new site with the given parameters

    :param table: The DBTable object to use when creating the site. Requires write access.
    :param site_id: The unique identifier of the new site
    :param longitude: The longitude of the centerpoint of the site
    :param latitude: The latitude of the centerpoint of the site
    :param acceptable_range: The range around the center of the site in meters, within which
        a person would be considered to be on the site
    :param timestamp: The timestamp at which the request to create this site was issued
    :param user_id: The user who issued the request to create this site
    :return: The newly created site
    :raises ResourceConflict: There is already a site in the database with the same id
    :raises ExternalServiceException: An unexpected error occurs in AWS
    :raises PermissionException: The given table does not have write permissions
    """
    item = DBSite(
        last_modified_by=user_id,
        last_modified_time=timestamp,
        site_id=site_id,
        longitude=longitude,
        latitude=latitude,
        acceptable_range=acceptable_range,
    )
    condition = Attr("pk").not_exists() & Attr("sk").not_exists()
    try:
        return table.put(item=item, condition_expression=condition)
    except ConditionCheckFailed as err:
        logger.exception(err)
        raise ResourceConflict(
            resource_type=item.type.value, resource_id=str(KeySchema(pk=item.pk, sk=item.sk))
        ) from err


def update_site(
    table: DBTable[DBSite],
    timestamp: datetime,
    user_id: str,
    site_id: str,
    longitude: Optional[float] = None,
    latitude: Optional[float] = None,
    acceptable_range: Optional[float] = None,
) -> DBSite:
    """
    Update an existing site with the given parameters

    :param table: The DBTable object to use when updating the site. Requires write access.
    :param site_id: The unique identifier of the new site
    :param longitude: The longitude of the centerpoint of the site
    :param latitude: The latitude of the centerpoint of the site
    :param acceptable_range: The range around the center of the site in meters, within which
        a person would be considered to be on the site
    :param timestamp: The timestamp at which the request to create this site was issued
    :param user_id: The user who issued the request to create this site
    :return: The full newly updated site
    :raises TimeConsistencyException: In the time since this update was requested, a new
        update has been made to the entry. Not sure whether to proceed with update
    :raises ExternalServiceException: An unexpected error occurs in AWS
    :raises PermissionException: The given table does not have write permissions
    """
    condition = (
        Attr("pk").exists()
        & Attr("sk").exists()
        & Attr("last_modified_time").lt(timestamp.isoformat())
    )
    key = KeySchema(pk=DBSite.item_type().value, sk=site_id)
    update_attrs = {}
    if longitude:
        update_attrs["longitude"] = longitude
    if latitude:
        update_attrs["latitude"] = latitude
    if acceptable_range:
        update_attrs["acceptable_range"] = acceptable_range
    try:
        return table.update(
            key=key,
            update_attributes=update_attrs,
            last_modified_time=timestamp,
            last_modified_by=user_id,
            condition_expression=condition,
        )
    except ConditionCheckFailed as err:
        logger.exception(err)
        raise TimeConsistencyException(key=str(key), timestamp=timestamp) from err


def delete_site(table: DBTable[DBSite], site_id: str, timestamp: datetime) -> None:
    """
    Delete a site from the database

    :param table: The table to use when deleting the site. Requires write permissions
    :param site_id: The unique identifier of the site to delete
    :param timestamp: The time at which the request to delete the site was issued
    :raises TimeConsistencyException: In the time since this delete was requested, a new
        update has been made to the entry. Not sure whether to proceed with delete
    :raises ExternalServiceException: An unexpected error occurs in AWS
    :raises PermissionException: The given table does not have write permissions
    """
    key = KeySchema(pk=DBSite.item_type().value, sk=site_id)
    condition = (
        Attr("pk").exists()
        & Attr("sk").exists
        & Attr("last_modified_time").lt(timestamp.isoformat())
    )

    try:
        table.delete(key=key, condition_expression=condition)
    except ConditionCheckFailed as err:
        logger.exception(err)
        raise TimeConsistencyException(key=str(key), timestamp=timestamp) from err


def get_site(table: DBTable[DBSite], site_id: str) -> DBSite:
    """
    Get a site from the database

    :param table: The table to use when getting the site
    :param site_id: The unique identifier of the site to get
    :return: The details of the requested site
    :raises ResourceNotFound: No site with the given ID exists
    :raises ExternalServiceException: An unexpected error occurs in AWS
    """
    key = KeySchema(pk=DBSite.item_type().value, sk=site_id)
    return table.get(key=key)


def list_sites(table: DBTable[DBSite], limit: int) -> tuple[list[DBSite], Optional[dict]]:
    """
    Get a list of all sites from the database

    :param table: The table to use when getting the sites
    :param limit: The maximum number of sites to get
    :return: The list of all sites within the given limit, and the last evaluated key
    :raises ExternalServiceException: An unexpected error occurs in AWS
    """
    key_expression = Key("type").eq(ItemType.SITE.value)
    return table.query(
        gsi=GSI.GSI1,
        key_condition_expression=key_expression,
        limit=limit,
        scan_reverse=True,
    )
