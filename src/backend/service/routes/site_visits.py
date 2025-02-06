"""
Routes for site visit APIs
"""

import json
from datetime import datetime
from http import HTTPStatus
from typing import Optional

from aws_lambda_powertools.event_handler import Response, content_types
from aws_lambda_powertools.event_handler.api_gateway import Router
from aws_lambda_powertools.event_handler.openapi.params import Path, Query
from typing_extensions import Annotated

from ..database.db_table import DBTable
from ..models.api.site_visit import APISiteVisit
from ..models.db.site_visit import DBSiteVisit
from ..site_visits.site_visits import add_exit_time, create_site_entry, list_site_visits
from ..util import AWSAccessLevel

router = Router()


@router.post("/<site_id>/enter")
def enter_site_handler(site_id: Annotated[str, Path()]):
    """
    Adds a users site visit to the database, with their entry time

    :param site_id: The site id that the user is entering
    :return: The details of the added site visit
    """
    request_time: datetime = router.current_event["requestContext"]["requestTimeEpoch"]

    # Get user id from token once possible
    user_id = "b15b955a-0ffc-4890-9025-49f37bab09f9"

    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)
    visit = create_site_entry(table=table, site_id=site_id, user_id=user_id, timestamp=request_time)

    return Response(
        status_code=HTTPStatus.CREATED.value,
        content_type=content_types.APPLICATION_JSON,
        body=APISiteVisit(
            site_id=visit.site_id,
            user_id=visit.user_id,
            entry_time=visit.entry_time,
            exit_time=visit.exit_time,
        ).model_dump_json(),
    )


@router.patch("/<site_id>/exit")
def exit_site_handler(site_id: Annotated[str, Path()]):
    """
    Adds an exit time to an existing site visit in the database

    :param site_id: The site id that the user is exiting
    :return: The details of the updated site visit
    """
    request_time: datetime = router.current_event["requestContext"]["requestTimeEpoch"]

    # Get user id from token once possible
    user_id = "b15b955a-0ffc-4890-9025-49f37bab09f9"

    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)
    visit = add_exit_time(table=table, site_id=site_id, user_id=user_id, timestamp=request_time)

    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=visit.to_api_model().model_dump_json(),
    )


@router.get("/visits")
def list_site_visits_handler(
    from_time: Annotated[Optional[datetime], Query()] = None,
    to_time: Annotated[Optional[datetime], Query()] = None,
    limit: Annotated[Optional[int], Query()] = None,
):
    """
    Lists the site visits in the database, according to the passed parameters

    :param from_time: Only site visits from after this time are returned
    :param to_time: Only site visits from before this time are returned
    :param limit: The maximum amount of site visits to retrieve
    :return: The details of all site visits retrieved
    """
    # Add role check to ensure admin

    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBSiteVisit)
    visits = list_site_visits(
        table=table,
        from_time=from_time,
        to_time=to_time,
        limit=limit,
    )
    response_body = json.dumps([visit.to_api_model().model_dump() for visit in visits])

    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=response_body,
    )
