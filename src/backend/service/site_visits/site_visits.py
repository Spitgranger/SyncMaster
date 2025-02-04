"""
Manages the creation, and updating of site visits
"""

from datetime import datetime

from aws_lambda_powertools.logging import Logger
from boto3.dynamodb.conditions import Attr, Key

from ..database.db_table import DBTable, KeySchema
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


def update_exit_time(table: DBTable[DBSiteVisit], site_id: str, user_id: str, timestamp: datetime):
    pk = f"{ItemType.SITE_VISIT.value}#{site_id}#{user_id}"
    key_condition = Key("pk").eq(f"{ItemType.SITE_VISIT.value}#{site_id}#{user_id}")
    items = table.query(key_condition_expression=key_condition, limit=1)

    if not items:
        raise ResourceNotFound(resource_type=ItemType.SITE_VISIT.value, resource_id=pk)

    if items[0].exit_time:
        raise ExitTimeConflict(site_id=site_id, user_id=user_id)
