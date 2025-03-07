from datetime import datetime, timezone
from http import HTTPStatus
from typing import Optional

from aws_lambda_powertools.event_handler import Response, content_types
from aws_lambda_powertools.event_handler.api_gateway import Router
from aws_lambda_powertools.event_handler.openapi.params import Body, Path, Query
from typing_extensions import Annotated

from ...database.db_table import DBTable
from ...exceptions import InsufficientUserPermissionException
from ...models.api.site import APIListSitesResponse, APISite, APISitePartial
from ...models.db.site import DBSite
from ...site_management.site_management import create_site, delete_site, update_site
from ...util import AWSAccessLevel, decode_db_key, encode_db_key

router = Router()


@router.post("/")
def create_site_handler(site: Annotated[APISite, Body()]) -> Response[APISite]:
    """
    Adds a site to the database

    :param site: The details of the site to create
    :return: The details of the added site
    """
    request_time = datetime.fromtimestamp(
        router.current_event["requestContext"]["requestTimeEpoch"] / 1000, tz=timezone.utc
    )

    # Getting role from user claims
    role = router.current_event["requestContext"]["authorizer"]["claims"]["custom:role"]

    # Role check to ensure admin
    if role != "admin":
        raise InsufficientUserPermissionException(role=role, action="list site visits")

    # Getting user id from claims
    user_id = router.current_event["requestContext"]["authorizer"]["claims"]["sub"]

    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSite)
    new_site = create_site(
        table=table,
        site_id=site.site_id,
        longitude=site.longitude,
        latitude=site.latitude,
        acceptable_range=site.acceptable_range,
        timestamp=request_time,
        user_id=user_id,
    )

    return Response(
        status_code=HTTPStatus.CREATED.value,
        content_type=content_types.APPLICATION_JSON,
        body=APISite(
            site_id=new_site.site_id,
            longitude=new_site.longitude,
            latitude=new_site.latitude,
            acceptable_range=new_site.acceptable_range,
        ),
    )


@router.patch("/<site_id>")
def update_site_handler(
    site_id: Annotated[str, Path()], site_update_attrs: Annotated[APISitePartial, Body()]
) -> Response[APISite]:
    """
    Updates the details of a site existing in the database

    :param site_id: The ID of the site that should be updated
    :param site_update_attrs: The attributes of the site that must be updated
    :return: The details of the updated site
    """
    request_time = datetime.fromtimestamp(
        router.current_event["requestContext"]["requestTimeEpoch"] / 1000, tz=timezone.utc
    )

    # Getting role from user claims
    role = router.current_event["requestContext"]["authorizer"]["claims"]["custom:role"]

    # Role check to ensure admin
    if role != "admin":
        raise InsufficientUserPermissionException(role=role, action="list site visits")

    # Getting user id from claims
    user_id = router.current_event["requestContext"]["authorizer"]["claims"]["sub"]

    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSite)
    new_site = update_site(
        table=table,
        timestamp=request_time,
        user_id=user_id,
        site_id=site_id,
        longitude=site_update_attrs.longitude,
        latitude=site_update_attrs.latitude,
        acceptable_range=site_update_attrs.acceptable_range,
    )

    return Response(
        status_code=HTTPStatus.CREATED.value,
        content_type=content_types.APPLICATION_JSON,
        body=APISite(
            site_id=new_site.site_id,
            longitude=new_site.longitude,
            latitude=new_site.latitude,
            acceptable_range=new_site.acceptable_range,
        ),
    )


@router.delete("/<site_id>")
def delete_site_handler(site_id: Annotated[str, Path()]) -> Response:
    """
    Delete a site

    :param site_id: The ID of the site that should be deleted
    """
    request_time = datetime.fromtimestamp(
        router.current_event["requestContext"]["requestTimeEpoch"] / 1000, tz=timezone.utc
    )

    # Getting role from user claims
    role = router.current_event["requestContext"]["authorizer"]["claims"]["custom:role"]

    # Role check to ensure admin
    if role != "admin":
        raise InsufficientUserPermissionException(role=role, action="list site visits")

    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSite)
    delete_site(table=table, site_id=site_id, timestamp=request_time)

    return Response(
        status_code=HTTPStatus.NO_CONTENT.value,
        content_type=content_types.APPLICATION_JSON,
    )
