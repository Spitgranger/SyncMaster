"""
Manages the creation, and updating of site visits
"""

from datetime import datetime
from typing import Optional

from aws_lambda_powertools.logging import Logger
from boto3.dynamodb.conditions import Attr, Key

from ..database.db_table import GSI, DBTable, KeySchema
from ..exceptions import (
    BadRequestException,
    ConditionCheckFailed,
    LimitExceeded,
    ResourceConflict,
    ResourceNotFound,
    TimeConsistencyException,
)
from ..file_storage.s3_bucket import S3Bucket
from ..models.api.site_visit import EditableSiteVisitDetails
from ..models.db.site_visit import DBSiteVisit
from ..util import ItemType

logger = Logger()


def create_site_entry(
    table: DBTable[DBSiteVisit],
    site_id: str,
    user_id: str,
    user_email: str,
    loc_tracking: bool,
    ack_status: bool,
    timestamp: datetime,
    on_site: Optional[bool] = None,
    employee_id: Optional[str] = None,
) -> DBSiteVisit:
    """
    Creates a site visit in the database for an initial entry

    :param table: The DBTable object to use to access the database. Requires write access
    :param site_id: The identifier of the site being visited
    :param user_id: The identifier of the user visiting the site
    :param user_email: The email of the user entering the site
    :param timestamp: The time at which the request for the site entry came in
    :param ack_status: Whether or not all documents were acknowledged before entering the site
    :param loc_tracking: Whether or not the user allowed us to track their location
    :param on_site: Whether or not the user was on site
    :param employee_id: The id of the employee accompanying the user
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
        user_email=user_email,
        loc_tracking=loc_tracking,
        ack_status=ack_status,
        on_site=on_site,
        employee_id=employee_id,
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
    table: DBTable[DBSiteVisit],
    site_id: str,
    user_id: str,
    entry_time: datetime,
    timestamp: datetime,
) -> DBSiteVisit:
    """
    Updates a site visit in the database with its exit time

    :param table: The DBTable object to use to access the database. Requires write access
    :param site_id: The identifier of the site being visited
    :param user_id: The identifier of the user visiting the site
    :param entry_time: The entry time of the site visit entry
    :param timestamp: The time at which the request for the site exit came in
    :return: The representation of the site visit in the database
    :raises ResourceNotFound: The user has never visited this site before
    :raises ExternalServiceException: An unexpected error occurs in AWS
    :raises PermissionException: The given table does not have write permissions
    """
    key = KeySchema(
        pk=f"{ItemType.SITE_VISIT.value}#{site_id}#{user_id}", sk=entry_time.isoformat()
    )

    try:
        return table.update(
            key=key,
            update_attributes={"exit_time": timestamp.isoformat()},
            last_modified_by=user_id,
            last_modified_time=timestamp,
            condition_expression=Attr("pk").exists()
            & Attr("sk").exists()
            & Attr("last_modified_time").lt(timestamp.isoformat()),
        )
    except ConditionCheckFailed as err:
        logger.exception(err)
        raise ResourceNotFound(
            resource_type=ItemType.SITE_VISIT.value, resource_id=str(key)
        ) from err


def get_site_visit(
    table: DBTable[DBSiteVisit],
    site_id: str,
    user_id: str,
    entry_time: datetime,
) -> DBSiteVisit:
    """
    Get a site visit from the database
    :param table: The DBTable object to use to access the database. Requires write access
    :param site_id: The site id that was visited
    :param user_id: The user visiting the site
    :param entry_time: The time the site was entered
    :return: The details of the specified site visit
    :raises ResourceNotFound: No site visit found matching requirements
    :raises ExternalServiceException: An unexpected error occurs in AWS
    """
    key = KeySchema(
        pk=f"{ItemType.SITE_VISIT.value}#{site_id}#{user_id}", sk=entry_time.isoformat()
    )
    return table.get(key=key)


def list_site_visits(
    table: DBTable[DBSiteVisit],
    from_time: Optional[datetime] = None,
    to_time: Optional[datetime] = None,
    limit: Optional[int] = None,
    start_key: Optional[dict] = None,
) -> tuple[list[DBSiteVisit], Optional[dict]]:
    """
    Updates a site visit in the database with its exit time

    :param table: The DBTable object to use to access the database. Requires write access
    :param from_time: All items found in the query must have been last modified after
        this time
    :param to_time: All items found in the query must have been last modified before
        this time
    :param limit: Maximum number of visits to retrieve from the database
    :param start_key: The key to start getting new visits from
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
        start_key=start_key,
    )


def create_file_attachment(
    table: DBTable[DBSiteVisit],
    site_id: str,
    user_id: str,
    entry_time: datetime,
    timestamp: datetime,
    name: str,
    s3_key: str,
) -> DBSiteVisit:
    """
    Adds a file attachment to a site visit in the database

    :param table: The DBTable object to use to access the database. Requires write access
    :param site_id: The identifier of the site being visited
    :param user_id: The identifier of the user visiting the site
    :param entry_time: The entry time of the site visit entry
    :param timestamp: The time at which the request came in
    :param name: The display name of the attachment
    :param s3_key: The s3_key that the attachment has been uploaded to
    :return: The representation of the attachment in the database
    :raises ResourceConflict: An attachment with the same name exists for the visit
    :raises LimitExceeded: Only 10 attachments can be uploaded to a site visit,
        so this error is raised, when this limit is exceeded
    :raises ExternalServiceException: An unexpected error occurs in AWS
    :raises PermissionException: The given table does not have write permissions
    """
    pk = f"{ItemType.SITE_VISIT.value}#{site_id}#{user_id}"
    sk = entry_time.isoformat()
    key = KeySchema(pk=pk, sk=sk)

    # Condition expression in the high-level boto3 dynamodb resource don't allow for the use
    # of expression attribute names in the condition. This means if the name of an attribute
    # contains a ".", then it won't work in the condition expression as "." is reserved to
    # access members of a map.
    # This means that we can't check that a name exists in the attachments map from the
    # condition expression. Instead getting it here to do the check.
    existing_item = table.get(key=key)

    if name in existing_item.attachments:
        logger.info(f"Attachment [{name}] already exists for visit [{str(key)}]")
        raise ResourceConflict(resource_type="file_attachment", resource_id=name)

    # There is also an added check here to see that the item hasn't been modified
    # since we got it earlier, so we know that no changes have been made in between
    condition = (
        Attr("pk").exists()
        & Attr("sk").exists()
        & (Attr("attachments").not_exists() | Attr("attachments").size().lt(10))
        & Attr("last_modified_time").lt(timestamp.isoformat())
        & Attr("last_modified_time").lte(existing_item.last_modified_time.isoformat())
    )

    try:
        return table.update(
            key=key,
            update_attributes={"attachments.#key": s3_key},
            expression_attribute_names={
                "#key": name,
            },
            last_modified_time=timestamp,
            last_modified_by=user_id,
            condition_expression=condition,
        )
    except ConditionCheckFailed as err:
        logger.exception(err)
        raise LimitExceeded(resource_type="file_attachment", limit=10) from err


def delete_file_attachment(
    table: DBTable[DBSiteVisit],
    bucket: S3Bucket,
    site_id: str,
    user_id: str,
    entry_time: datetime,
    timestamp: datetime,
    name: str,
) -> DBSiteVisit:
    """
    Deletes a file attachment from a site visit in the database

    :param table: The DBTable object to use to access the database. Requires write access
    :param bucket: The S3Bucket object to use to access the bucket. Requires write access
    :param site_id: The identifier of the site being visited
    :param user_id: The identifier of the user visiting the site
    :param entry_time: The entry time of the site visit entry
    :param timestamp: The time at which the request for the site exit came in
    :param name: The display name of the attachment
    :return: The representation of the attachment in the database
    :raises TimeConsistencyException: In the time since this update was requested, a new
        update has been made to the entry. Not sure whether to proceed with update
    :raises ExternalServiceException: An unexpected error occurs in AWS
    :raises PermissionException: The given table does not have write permissions
    """
    pk = f"{ItemType.SITE_VISIT.value}#{site_id}#{user_id}"
    sk = entry_time.isoformat()
    key = KeySchema(pk=pk, sk=sk)

    existing_visit = table.get(key=key)
    s3_key = existing_visit.attachments.get(name)

    condition = (
        Attr("pk").exists()
        & Attr("sk").exists()
        & Attr("last_modified_time").lt(timestamp.isoformat())
        & Attr("last_modified_time").lte(existing_visit.last_modified_time.isoformat())
    )

    try:
        new_visit = table.update(
            key=key,
            update_attributes={"attachments.#key": None},
            expression_attribute_names={
                "#key": name,
            },
            last_modified_time=timestamp,
            last_modified_by=user_id,
            condition_expression=condition,
        )
    except ConditionCheckFailed as err:
        logger.exception(err)
        raise TimeConsistencyException(key=str(key), timestamp=timestamp) from err

    if s3_key:
        bucket.delete(key=s3_key)

    return new_visit


def update_visit_details(
    table: DBTable[DBSiteVisit],
    site_id: str,
    user_id: str,
    entry_time: datetime,
    timestamp: datetime,
    updated_details: EditableSiteVisitDetails,
) -> DBSiteVisit:
    """
    Updates a site visit in the database with its exit time

    :param table: The DBTable object to use to access the database. Requires write access
    :param site_id: The identifier of the site being visited
    :param user_id: The identifier of the user visiting the site
    :param entry_time: The entry time of the site visit entry
    :param timestamp: The time at which the request came in
    :param updated_details: Contains the editable site visit details to be updated
    :return: The representation of the site visit in the database
    :raises TimeConsistencyException: In the time since this update was requested, a new
        update has been made to the entry. Not sure whether to proceed with update
    :raises BadRequestException: There are no explicitly set details to update
    :raises ExternalServiceException: An unexpected error occurs in AWS
    :raises PermissionException: The given table does not have write permissions
    """
    key = KeySchema(
        pk=f"{ItemType.SITE_VISIT.value}#{site_id}#{user_id}", sk=entry_time.isoformat()
    )

    if not updated_details.model_fields_set:
        raise BadRequestException("No attributes provided for update")

    # Extract fields explicitly set on the model, this avoids updating an attribute
    # to None, if it was not explicitly set to None
    update_attrs = {
        k: v
        for k, v in updated_details.model_dump(exclude_none=False).items()
        if k in updated_details.model_fields_set
    }

    try:
        return table.update(
            key=key,
            update_attributes=update_attrs,
            last_modified_by=user_id,
            last_modified_time=timestamp,
            condition_expression=Attr("pk").exists()
            & Attr("sk").exists()
            & Attr("last_modified_time").lt(timestamp.isoformat()),
        )
    except ConditionCheckFailed as err:
        logger.exception(err)
        raise TimeConsistencyException(key=str(key), timestamp=timestamp) from err
