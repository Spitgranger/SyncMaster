"""
Routes for site visit APIs
"""

import json
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Optional

from aws_lambda_powertools.event_handler import Response, content_types
from aws_lambda_powertools.event_handler.api_gateway import Router
from aws_lambda_powertools.event_handler.openapi.params import Path, Query
from typing_extensions import Annotated

from ..database.db_table import DBTable
from ..exceptions import InsufficientUserPermissionException
from ..models.api.site_visit import APISiteVisit
from ..models.db.site_visit import DBSiteVisit
from ..site_visits.site_visits import add_exit_time, create_site_entry, list_site_visits
from ..util import AWSAccessLevel

router = Router()

cors_headers = {
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, PUT, PATCH, DELETE",
}


@router.post("/<site_id>/enter")
def enter_site_handler(site_id: Annotated[str, Path()], user_id: Annotated[str, Query()]):
    """
    Adds a users site visit to the database, with their entry time

    :param user_id: Temporary param for determining user's id
    :param site_id: The site id that the user is entering
    :return: The details of the added site visit
    """
    request_time = datetime.fromtimestamp(
        router.current_event["requestContext"]["requestTimeEpoch"] / 1000, tz=timezone.utc
    )

    # Get user id from token here once possible

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
        headers=cors_headers,
    )


@router.patch("/<site_id>/exit")
def exit_site_handler(site_id: Annotated[str, Path()], user_id: Annotated[str, Query()]):
    """
    Adds an exit time to an existing site visit in the database

    :param user_id: Temporary param for determining user's id
    :param site_id: The site id that the user is exiting
    :return: The details of the updated site visit
    """
    request_time = datetime.fromtimestamp(
        router.current_event["requestContext"]["requestTimeEpoch"] / 1000, tz=timezone.utc
    )

    # Get user id from token once possible

    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)
    visit = add_exit_time(table=table, site_id=site_id, user_id=user_id, timestamp=request_time)

    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=visit.to_api_model().model_dump_json(),
        headers=cors_headers,
    )


@router.get("/visits")
def list_site_visits_handler(
    user_role: Annotated[str, Query()],
    from_time: Annotated[Optional[datetime], Query()] = None,
    to_time: Annotated[Optional[datetime], Query()] = None,
    limit: Annotated[Optional[int], Query()] = None,
):
    """
    Lists the site visits in the database, according to the passed parameters

    :param user_role: Temporary param for determining user's role
    :param from_time: Only site visits from after this time are returned
    :param to_time: Only site visits from before this time are returned
    :param limit: The maximum amount of site visits to retrieve
    :return: The details of all site visits retrieved
    """
    # Add getting role from user claims here once possible

    # Add role check to ensure admin
    if user_role != "admin":
        raise InsufficientUserPermissionException(role=user_role, action="list site visits")

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
        headers=cors_headers,
    )
