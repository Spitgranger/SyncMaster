"""
Manages the creation, and updating of site visits
"""

from datetime import datetime

from aws_lambda_powertools.logging import Logger
from boto3.dynamodb.conditions import Attr, Key

from ..database.db_table import GSI, DBTable, KeySchema
from ..exceptions import ConditionCheckFailed, ExitTimeConflict, ResourceConflict, ResourceNotFound
from ..models.db.site_visit import DBSiteVisit
from ..util import ItemType

logger = Logger()


def create_site_visit(
    table: DBTable[DBSiteVisit], site_id: str, user_id: str, timestamp: datetime
) -> DBSiteVisit:
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
            resource_type=item.item_type().value, resource_id=str(KeySchema(pk=item.pk, sk=item.sk))
        ) from err


def update_exit_time(
    table: DBTable[DBSiteVisit], site_id: str, user_id: str, timestamp: datetime
) -> DBSiteVisit:
    pk = f"{ItemType.SITE_VISIT.value}#{site_id}#{user_id}"
    key_condition = Key("pk").eq(f"{ItemType.SITE_VISIT.value}#{site_id}#{user_id}")
    items = table.query(key_condition_expression=key_condition, limit=1)

    if not items:
        raise ResourceNotFound(resource_type=ItemType.SITE_VISIT.value, resource_id=pk)

    if items[0].exit_time:
        raise ExitTimeConflict(site_id=site_id, user_id=user_id)

    return table.update(
        key=KeySchema(pk=items[0].pk, sk=items[0].sk),
        update_attributes={"exit_time": timestamp.isoformat()},
        last_modified_by=user_id,
        last_modified_time=timestamp,
        condition_expression=Attr("last_modified_time").lt(timestamp.isoformat()),
    )


def list_site_visits(
    table: DBTable[DBSiteVisit], from_time: datetime, to_time: datetime, limit: int = 20
) -> list[DBSiteVisit]:
    return table.query(
        gsi=GSI.GSI1,
        key_condition_expression=Key("type").eq(ItemType.SITE_VISIT.value)
        & Key("last_modified_time").gte(from_time.isoformat())
        & Key("last_modified_time").lte(to_time.isoformat()),
        limit=limit,
    )
