from http import HTTPStatus

from backend.service.database.db_table import DBTable, KeySchema
from backend.service.environment import DOCUMENT_STORAGE_BUCKET_NAME
from backend.service.file_storage.s3_bucket import S3Bucket
from backend.service.handler import lambda_handler
from backend.service.models.api.site_visit import APIListSiteVisitResponse, APISiteVisit
from backend.service.models.api.user_requests import APIGetUserRequestsResponse, APIUserRequest
from backend.service.models.db.site_visit import DBSiteVisit
from backend.service.util import AWSAccessLevel, ItemType

from ..constants import (
    CURRENT_DATE_TIME,
    PREV_DATE_TIME,
    TEST_ATTACHMENT_NAME,
    TEST_COMPANY_NAME,
    TEST_SITE_ID,
    TEST_USER_EMAIL,
    TEST_USER_ID,
)


def test_create_user_request_handler(empty_database, create_user_request_request):
    response = lambda_handler(
        event=create_user_request_request[0], context=create_user_request_request[1]
    )
    print(response["body"])
    request = APIUserRequest.model_validate_json(response["body"])

    assert response["statusCode"] == HTTPStatus.CREATED
    assert request.company == TEST_COMPANY_NAME
    assert request.email == TEST_USER_EMAIL
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_get_user_requests_paginated(
    database_with_two_user_requests, get_user_request_request_paginated, api_gateway_event
):
    _, set_of_db_entries = database_with_two_user_requests

    response = lambda_handler(
        event=get_user_request_request_paginated[0], context=get_user_request_request_paginated[1]
    )

    assert response["statusCode"] == HTTPStatus.OK
    response_body = APIGetUserRequestsResponse.model_validate_json(response["body"])
    assert len(response_body.requests) == 1
    assert response_body.requests[0] in [request.to_api_model() for request in set_of_db_entries]
    assert response_body.last_key is not None
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]

    new_event = api_gateway_event(
        path=f"/protected/user-requests/get-requests",
        method="GET",
        query_params={"limit": "1", "start_key": response_body.last_key},
        user_role="admin",
        user_groups=["admin"],
    )

    response = lambda_handler(event=new_event[0], context=new_event[1])

    assert response["statusCode"] == HTTPStatus.OK
    response_body = APIGetUserRequestsResponse.model_validate_json(response["body"])
    assert len(response_body.requests) == 1
    assert response_body.requests[0] in [request.to_api_model() for request in set_of_db_entries]
    assert response_body.last_key is None
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_get_user_requests(
    database_with_user_request, get_user_request_request_paginated, api_gateway_event
):
    _, request = database_with_user_request

    response = lambda_handler(
        event=get_user_request_request_paginated[0], context=get_user_request_request_paginated[1]
    )

    assert response["statusCode"] == HTTPStatus.OK
    response_body = APIGetUserRequestsResponse.model_validate_json(response["body"])
    assert len(response_body.requests) == 1
    assert response_body.requests[0] in [request.to_api_model()]
    assert response_body.last_key is None
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_get_user_requests_bad_role(database_with_user_request, get_user_request_request_bad_role):
    response = lambda_handler(
        event=get_user_request_request_bad_role[0], context=get_user_request_request_bad_role[1]
    )

    assert response["statusCode"] == HTTPStatus.FORBIDDEN
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_action_user_request_bad_role(
    database_with_user_request, action_user_request_request_bad_role
):
    response = lambda_handler(
        event=action_user_request_request_bad_role[0],
        context=action_user_request_request_bad_role[1],
    )

    assert response["statusCode"] == HTTPStatus.FORBIDDEN
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_action_user(database_with_user_request, cognito_client_admin, action_user_request_request):
    response = lambda_handler(
        event=action_user_request_request[0], context=action_user_request_request[1]
    )

    assert response["statusCode"] == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]
