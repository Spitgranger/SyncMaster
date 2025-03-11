"""
Routes for site management APIs
"""

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
from ...site_management.site_management import (
    create_site,
    delete_site,
    get_site,
    list_sites,
    update_site,
)
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
        raise InsufficientUserPermissionException(role=role, action="create site")

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
    site_id: Annotated[str, Path(min_length=5, max_length=5)],
    site_update_attrs: Annotated[APISitePartial, Body()],
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
        raise InsufficientUserPermissionException(role=role, action="update site")

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
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=APISite(
            site_id=new_site.site_id,
            longitude=new_site.longitude,
            latitude=new_site.latitude,
            acceptable_range=new_site.acceptable_range,
        ),
    )


@router.get("/<site_id>")
def get_site_handler(
    site_id: Annotated[str, Path(min_length=5, max_length=5)],
) -> Response[APISite]:
    """
    Get the details of a site

    :param site_id: The ID of the site to fetch
    :return: The details of the fetched site
    """
    # Getting role from user claims
    role = router.current_event["requestContext"]["authorizer"]["claims"]["custom:role"]

    # Role check to ensure admin
    if role != "admin":
        raise InsufficientUserPermissionException(role=role, action="get site")

    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBSite)
    new_site = get_site(table=table, site_id=site_id)

    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=APISite(
            site_id=new_site.site_id,
            longitude=new_site.longitude,
            latitude=new_site.latitude,
            acceptable_range=new_site.acceptable_range,
        ),
    )


@router.delete("/<site_id>")
def delete_site_handler(site_id: Annotated[str, Path(min_length=5, max_length=5)]) -> Response:
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
        raise InsufficientUserPermissionException(role=role, action="delete site")

    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSite)
    delete_site(table=table, site_id=site_id, timestamp=request_time)

    return Response(
        status_code=HTTPStatus.NO_CONTENT.value,
        content_type=content_types.APPLICATION_JSON,
    )


@router.get("/")
def list_sites_handler(
    limit: Annotated[Optional[int], Query(le=100)] = None,
    start_key: Annotated[Optional[str], Query()] = None,
) -> Response[APIListSitesResponse]:
    """
    List the available sites from the database

    :param limit: The maximum amount of sites to recieve
    :param start_key: A key to start from, should be recieved from a previous request
    :return: The list of sites and their details
    """
    # Getting role from user claims
    role = router.current_event["requestContext"]["authorizer"]["claims"]["custom:role"]

    # Role check to ensure admin
    if role != "admin":
        raise InsufficientUserPermissionException(role=role, action="list sites")

    decoded_start_key = decode_db_key(key=start_key) if start_key else None

    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBSite)
    sites, last_key = list_sites(table=table, limit=limit, start_key=decoded_start_key)

    encoded_key = encode_db_key(last_key) if last_key else None

    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=APIListSitesResponse(
            sites=[site.to_api_model() for site in sites], last_key=encoded_key
        ),
    )
