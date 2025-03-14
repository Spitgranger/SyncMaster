"""
Routes for site visit APIs
"""

import base64
import json
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Optional

from aws_lambda_powertools.event_handler import Response, content_types
from aws_lambda_powertools.event_handler.api_gateway import Router
from aws_lambda_powertools.event_handler.openapi.params import Path, Query
from typing_extensions import Annotated

from ...database.db_table import DBTable
from ...exceptions import InsufficientUserPermissionException
from ...models.api.site_visit import APIListSiteVisitResponse, APISiteVisit
from ...models.db.site_visit import DBSiteVisit
from ...site_visits.site_visits import add_exit_time, create_site_entry, list_site_visits
from ...util import CORS_HEADERS, AWSAccessLevel

router = Router()


@router.post("/<site_id>/enter")
def enter_site_handler(site_id: Annotated[str, Path()]):
    """
    Adds a users site visit to the database, with their entry time

    :param site_id: The site id that the user is entering
    :return: The details of the added site visit
    """
    request_time = datetime.fromtimestamp(
        router.current_event["requestContext"]["requestTimeEpoch"] / 1000, tz=timezone.utc
    )

    # Getting user id from claims
    user_id = router.current_event["requestContext"]["authorizer"]["claims"]["sub"]

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
        headers=CORS_HEADERS,
    )


@router.patch("/<site_id>/exit")
def exit_site_handler(site_id: Annotated[str, Path()]):
    """
    Adds an exit time to an existing site visit in the database

    :param site_id: The site id that the user is exiting
    :return: The details of the updated site visit
    """
    request_time = datetime.fromtimestamp(
        router.current_event["requestContext"]["requestTimeEpoch"] / 1000, tz=timezone.utc
    )

    # Getting user id from claims
    user_id = router.current_event["requestContext"]["authorizer"]["claims"]["sub"]

    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)
    visit = add_exit_time(table=table, site_id=site_id, user_id=user_id, timestamp=request_time)

    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=visit.to_api_model().model_dump_json(),
        headers=CORS_HEADERS,
    )


@router.get("/visits")
def list_site_visits_handler(
    from_time: Annotated[Optional[datetime], Query()] = None,
    to_time: Annotated[Optional[datetime], Query()] = None,
    limit: Annotated[Optional[int], Query()] = None,
    start_key: Annotated[Optional[str], Query()] = None,
) -> Response[APIListSiteVisitResponse]:
    """
    Lists the site visits in the database, according to the passed parameters

    :param from_time: Only site visits from after this time are returned
    :param to_time: Only site visits from before this time are returned
    :param limit: The maximum amount of site visits to retrieve
    :param start_key: The key to start listing visits from, should be
        obtained from the last_key of a previous request
    :return: The details of all site visits retrieved
    """
    # Getting role from user claims
    role = router.current_event["requestContext"]["authorizer"]["claims"]["custom:role"]

    # Role check to ensure admin
    if role != "admin":
        raise InsufficientUserPermissionException(role=role, action="list site visits")

    decoded_key: Optional[dict] = None
    if start_key:
        key_bytes = base64.urlsafe_b64decode(start_key.encode("utf-8"))
        decoded_key = json.loads(key_bytes)

    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBSiteVisit)
    visits, last_eval_key = list_site_visits(
        table=table,
        from_time=from_time,
        to_time=to_time,
        limit=limit,
        start_key=decoded_key,
    )

    encoded_key = None
    if last_eval_key:
        key_bytes = json.dumps(last_eval_key).encode("utf-8")
        encoded_key = base64.urlsafe_b64encode(key_bytes).decode("utf-8")

    response_body = APIListSiteVisitResponse(
        visits=[visit.to_api_model() for visit in visits], last_key=encoded_key
    )

    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=response_body,
        headers=CORS_HEADERS,
    )
