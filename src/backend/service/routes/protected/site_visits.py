"""
Routes for site visit APIs
"""

from datetime import datetime, timezone
from http import HTTPStatus
from typing import Optional

from aws_lambda_powertools.event_handler import Response, content_types
from aws_lambda_powertools.event_handler.api_gateway import Router
from aws_lambda_powertools.event_handler.openapi.params import Body, Path, Query
from typing_extensions import Annotated

from ...database.db_table import DBTable
from ...environment import DOCUMENT_STORAGE_BUCKET_NAME
from ...exceptions import InsufficientUserPermissionException
from ...file_storage.s3_bucket import S3Bucket
from ...models.api.file_attachment import APIAddFileAttachment, APIRemoveFileAttachment
from ...models.api.site_visit import (
    APIEnterSiteRequest,
    APIListSiteVisitResponse,
    EditableSiteVisitDetails,
)
from ...models.db.site_visit import DBSiteVisit
from ...site_visits.site_visits import (
    add_exit_time,
    create_file_attachment,
    create_site_entry,
    delete_file_attachment,
    list_site_visits,
    update_visit_details,
)
from ...util import CORS_HEADERS, AWSAccessLevel, UserType, decode_db_key, encode_db_key

router = Router()


@router.post("/<site_id>/enter")
def enter_site_handler(
    site_id: Annotated[str, Path()], visit_details: Annotated[APIEnterSiteRequest, Body()]
):
    """
    Adds a users site visit to the database, with their entry time

    :param site_id: The site id that the user is entering
    :param visit_details: Details of the visit which are available on entry
    :return: The details of the added site visit
    """
    request_time = datetime.fromtimestamp(
        router.current_event["requestContext"]["requestTimeEpoch"] / 1000, tz=timezone.utc
    )

    # Getting user id from claims
    user_id = router.current_event["requestContext"]["authorizer"]["claims"]["sub"]

    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)
    visit = create_site_entry(
        table=table,
        site_id=site_id,
        user_id=user_id,
        loc_tracking=visit_details.allowed_tracking,
        ack_status=visit_details.ack_status,
        timestamp=request_time,
        on_site=visit_details.on_site,
    )

    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.READ)

    return Response(
        status_code=HTTPStatus.CREATED.value,
        content_type=content_types.APPLICATION_JSON,
        body=visit.to_api_model(bucket=bucket).model_dump_json(),
        headers=CORS_HEADERS,
    )


@router.patch("/<site_id>/visit/<entry_time>")
def edit_visit_details_handler(
    site_id: Annotated[str, Path()],
    entry_time: Annotated[datetime, Path()],
    visit_details: Annotated[EditableSiteVisitDetails, Body()],
):
    """
    Adds additional details to an existing site visit in the database

    :param site_id: The site id for the visit
    :param entry_time: The entry time of the visit to add the details to
    :param visit_details: The details of the visit to update/add
    :return: The details of the updated site visit
    """
    request_time = datetime.fromtimestamp(
        router.current_event["requestContext"]["requestTimeEpoch"] / 1000, tz=timezone.utc
    )

    # Getting user id from claims
    user_id = router.current_event["requestContext"]["authorizer"]["claims"]["sub"]

    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)
    visit = update_visit_details(
        table=table,
        site_id=site_id,
        user_id=user_id,
        entry_time=entry_time,
        timestamp=request_time,
        updated_details=visit_details,
    )

    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.READ)

    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=visit.to_api_model(bucket=bucket).model_dump_json(),
        headers=CORS_HEADERS,
    )


@router.patch("/<site_id>/visit/<entry_time>/attachments/add")
def add_file_attachment_handler(
    site_id: Annotated[str, Path()],
    entry_time: Annotated[datetime, Path()],
    attachment_details: Annotated[APIAddFileAttachment, Body()],
):
    """
    Adds a file attachment to an existing site visit in the database

    :param site_id: The site id for the visit
    :param entry_time: The entry time of the visit to add the attachment to
    :param attachment_details: The details of the attachment to add
    :return: The details of the updated site visit
    """
    request_time = datetime.fromtimestamp(
        router.current_event["requestContext"]["requestTimeEpoch"] / 1000, tz=timezone.utc
    )

    # Getting user id from claims
    user_id = router.current_event["requestContext"]["authorizer"]["claims"]["sub"]

    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)
    visit = create_file_attachment(
        table=table,
        site_id=site_id,
        user_id=user_id,
        entry_time=entry_time,
        timestamp=request_time,
        name=attachment_details.name,
        s3_key=attachment_details.s3_key,
    )

    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.READ)

    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=visit.to_api_model(bucket=bucket).model_dump_json(),
        headers=CORS_HEADERS,
    )


@router.patch("/<site_id>/visit/<entry_time>/attachments/remove")
def remove_file_attachment_handler(
    site_id: Annotated[str, Path()],
    entry_time: Annotated[datetime, Path()],
    attachment_details: Annotated[APIRemoveFileAttachment, Body()],
):
    """
    Remove a file attachment from an existing site visit in the database

    :param site_id: The site id for the visit
    :param entry_time: The entry time of the visit to remove the attachment from
    :param attachment_details: The details of the attachment to remove
    :return: The details of the updated site visit
    """
    request_time = datetime.fromtimestamp(
        router.current_event["requestContext"]["requestTimeEpoch"] / 1000, tz=timezone.utc
    )

    # Getting user id from claims
    user_id = router.current_event["requestContext"]["authorizer"]["claims"]["sub"]

    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.WRITE)
    visit = delete_file_attachment(
        table=table,
        bucket=bucket,
        site_id=site_id,
        user_id=user_id,
        entry_time=entry_time,
        timestamp=request_time,
        name=attachment_details.name,
    )

    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=visit.to_api_model(bucket=bucket).model_dump_json(),
        headers=CORS_HEADERS,
    )


@router.patch("/<site_id>/exit/<entry_time>")
def exit_site_handler(site_id: Annotated[str, Path()], entry_time: Annotated[datetime, Path()]):
    """
    Adds an exit time to an existing site visit in the database

    :param site_id: The site id that the user is exiting
    :param entry_time: The entry time of the visit to add the exit time to
    :return: The details of the updated site visit
    """
    request_time = datetime.fromtimestamp(
        router.current_event["requestContext"]["requestTimeEpoch"] / 1000, tz=timezone.utc
    )

    # Getting user id from claims
    user_id = router.current_event["requestContext"]["authorizer"]["claims"]["sub"]

    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBSiteVisit)
    visit = add_exit_time(
        table=table, site_id=site_id, user_id=user_id, entry_time=entry_time, timestamp=request_time
    )

    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.READ)

    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=visit.to_api_model(bucket=bucket).model_dump_json(),
        headers=CORS_HEADERS,
    )


@router.get("/visits")
def list_site_visits_handler(
    from_time: Annotated[Optional[datetime], Query()] = None,
    to_time: Annotated[Optional[datetime], Query()] = None,
    limit: Annotated[Optional[int], Query(le=100)] = None,
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
    roles = router.current_event["requestContext"]["authorizer"]["claims"]["cognito:groups"]

    # Role check to ensure admin
    if UserType.ADMIN.value not in roles:
        raise InsufficientUserPermissionException(role=roles, action="list site visits")

    decoded_key = decode_db_key(key=start_key) if start_key else None

    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBSiteVisit)
    visits, last_eval_key = list_site_visits(
        table=table,
        from_time=from_time,
        to_time=to_time,
        limit=limit,
        start_key=decoded_key,
    )

    encoded_key = encode_db_key(key=last_eval_key) if last_eval_key else None

    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.READ)

    response_body = APIListSiteVisitResponse(
        visits=[visit.to_api_model(bucket=bucket) for visit in visits], last_key=encoded_key
    )

    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=response_body,
        headers=CORS_HEADERS,
    )
