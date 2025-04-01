"""
Routes for site management APIs
"""

from http import HTTPStatus
from typing import Optional

from aws_lambda_powertools.event_handler import Response, content_types
from aws_lambda_powertools.event_handler.api_gateway import Router
from aws_lambda_powertools.event_handler.openapi.params import Body, Path, Query
from typing_extensions import Annotated

from ...database.db_table import DBTable
from ...models.api.site import APIListSitesResponse, APISite, APISitePartial
from ...models.db.document import DBDocument
from ...models.db.site import DBSite
from ...site_management.site_management import (
    create_site,
    delete_site,
    get_site,
    list_sites,
    update_site,
)
from ...util import (
    CORS_HEADERS,
    AWSAccessLevel,
    UserType,
    create_open_api_error_response,
    create_open_api_response,
    decode_db_key,
    encode_db_key,
    time_epoch_to_datetime,
    verify_user_role,
)

router = Router()


@router.post(
    "/",
    security=[{"bearer": [UserType.ADMIN.value]}],
    responses={
        201: create_open_api_response(description="Created Site", response_body_schema=APISite),
        409: create_open_api_error_response(description="Site with same id already exists"),
    },
)
def create_site_handler(site: Annotated[APISite, Body()]):
    """
    Adds a site to the database

    :param site: The details of the site to create
    :return: The details of the added site
    """
    request_time = time_epoch_to_datetime(
        router.current_event["requestContext"]["requestTimeEpoch"]
    )

    verify_user_role(
        user_groups=router.current_event["requestContext"]["authorizer"]["claims"][
            "cognito:groups"
        ],
        acceptable_roles=[UserType.ADMIN],
        action="create site",
    )

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
        headers=CORS_HEADERS,
    )


@router.patch(
    "/<site_id>",
    security=[{"bearer": [UserType.ADMIN.value]}],
    responses={
        200: create_open_api_response(description="Updated Site", response_body_schema=APISite)
    },
)
def update_site_handler(
    site_id: Annotated[str, Path(min_length=5, max_length=5)],
    site_update_attrs: Annotated[APISitePartial, Body()],
):
    """
    Updates the details of a site existing in the database

    :param site_id: The ID of the site that should be updated
    :param site_update_attrs: The attributes of the site that must be updated
    :return: The details of the updated site
    """
    request_time = time_epoch_to_datetime(
        router.current_event["requestContext"]["requestTimeEpoch"]
    )

    verify_user_role(
        user_groups=router.current_event["requestContext"]["authorizer"]["claims"][
            "cognito:groups"
        ],
        acceptable_roles=[UserType.ADMIN],
        action="update site",
    )

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
        headers=CORS_HEADERS,
    )


@router.get(
    "/<site_id>",
    security=[{"bearer": [UserType.ADMIN.value, UserType.EMPLOYEE.value]}],
    responses={
        200: create_open_api_response(description="Requested Site", response_body_schema=APISite),
        404: create_open_api_error_response(description="Requested site does not exist"),
    },
)
def get_site_handler(
    site_id: Annotated[str, Path(min_length=5, max_length=5)],
):
    """
    Get the details of a site

    :param site_id: The ID of the site to fetch
    :return: The details of the fetched site
    """

    verify_user_role(
        user_groups=router.current_event["requestContext"]["authorizer"]["claims"][
            "cognito:groups"
        ],
        acceptable_roles=[UserType.ADMIN, UserType.EMPLOYEE],
        action="get site",
    )

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
        headers=CORS_HEADERS,
    )


@router.delete(
    "/<site_id>",
    security=[{"bearer": [UserType.ADMIN.value]}],
    responses={204: create_open_api_response(description="No Content", response_body_schema={})},
)
def delete_site_handler(site_id: Annotated[str, Path(min_length=5, max_length=5)]):
    """
    Delete a site

    :param site_id: The ID of the site that should be deleted
    """
    request_time = time_epoch_to_datetime(
        router.current_event["requestContext"]["requestTimeEpoch"]
    )
    verify_user_role(
        user_groups=router.current_event["requestContext"]["authorizer"]["claims"][
            "cognito:groups"
        ],
        acceptable_roles=[UserType.ADMIN],
        action="delete site",
    )

    site_table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSite)
    document_table = DBTable(access=AWSAccessLevel.READ, item_schema=DBDocument)
    delete_site(
        site_table=site_table,
        document_table=document_table,
        site_id=site_id,
        timestamp=request_time,
    )

    return Response(
        status_code=HTTPStatus.NO_CONTENT.value,
        content_type=content_types.APPLICATION_JSON,
        headers=CORS_HEADERS,
    )


@router.get(
    "/",
    security=[{"bearer": [UserType.ADMIN.value, UserType.EMPLOYEE.value]}],
    responses={
        200: create_open_api_response(
            description="List of all sites", response_body_schema=APIListSitesResponse
        )
    },
)
def list_sites_handler(
    limit: Annotated[Optional[int], Query(le=100)] = None,
    start_key: Annotated[Optional[str], Query()] = None,
):
    """
    List the available sites from the database

    :param limit: The maximum amount of sites to recieve
    :param start_key: A key to start from, should be recieved from a previous request
    :return: The list of sites and their details
    """
    verify_user_role(
        user_groups=router.current_event["requestContext"]["authorizer"]["claims"][
            "cognito:groups"
        ],
        acceptable_roles=[UserType.ADMIN, UserType.EMPLOYEE],
        action="list sites",
    )

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
        headers=CORS_HEADERS,
    )
