from datetime import timedelta
from http import HTTPStatus

import pytest
from backend.service.database.db_table import DBTable, KeySchema
from backend.service.exceptions import (
    ConflictException,
    ExternalServiceException,
    ResourceConflict,
    ResourceNotFound,
)
from backend.service.models.db.user_request import DBUserRequest
from backend.service.user_requests.user_requests import (
    action_user_request,
    create_user_request,
    get_user_requests,
)
from backend.service.util import AWSAccessLevel, UserRequestAction

from ..constants import (
    CURRENT_DATE_TIME,
    TEST_COMPANY_NAME,
    TEST_USER_EMAIL,
    TEST_USER_NAME,
    TEST_USER_ROLE,
)


def test_create_user_request(empty_database, cognito_client_admin):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBUserRequest)

    request = create_user_request(
        table=table,
        email=TEST_USER_EMAIL,
        company=TEST_COMPANY_NAME,
        name=TEST_USER_NAME,
        requested_role=TEST_USER_ROLE,
        time=CURRENT_DATE_TIME,
        cognito_client=cognito_client_admin,
    )

    assert table.get(key=KeySchema(pk=request.pk, sk=request.sk)) == request


def test_create_user_request_conflict(database_with_user_request, cognito_client_admin):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBUserRequest)
    with pytest.raises(ResourceConflict):
        create_user_request(
            table=table,
            email=TEST_USER_EMAIL,
            company=TEST_COMPANY_NAME,
            name=TEST_USER_NAME,
            requested_role=TEST_USER_ROLE,
            time=CURRENT_DATE_TIME,
            cognito_client=cognito_client_admin,
        )


def test_create_user_request_conflict_with_existing_user(
    empty_database, admin_cognito_client_with_user
):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBUserRequest)
    cognito_client, _, _ = admin_cognito_client_with_user
    with pytest.raises(ConflictException):
        create_user_request(
            table=table,
            email=TEST_USER_EMAIL,
            company=TEST_COMPANY_NAME,
            name=TEST_USER_NAME,
            requested_role=TEST_USER_ROLE,
            time=CURRENT_DATE_TIME,
            cognito_client=cognito_client,
        )


def test_create_user_request_cognito_exception(empty_database, cognito_client_admin_fake):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBUserRequest)
    with pytest.raises(ExternalServiceException):
        create_user_request(
            table=table,
            email=TEST_USER_EMAIL,
            company=TEST_COMPANY_NAME,
            name=TEST_USER_NAME,
            requested_role=TEST_USER_ROLE,
            time=CURRENT_DATE_TIME,
            cognito_client=cognito_client_admin_fake,
        )


def test_get_user_request(database_with_user_request):
    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBUserRequest)
    user_request, _ = get_user_requests(table)
    assert user_request[0].email == TEST_USER_EMAIL
    assert user_request[0].company == TEST_COMPANY_NAME
    assert user_request[0].name == TEST_USER_NAME
    assert user_request[0].role_requested == TEST_USER_ROLE.lower()
    assert user_request[0].last_modified_by == "system"


def test_action_user_request_approve(database_with_user_request, cognito_client_admin):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBUserRequest)
    response = action_user_request(
        cognito_client=cognito_client_admin,
        table=table,
        email=TEST_USER_EMAIL,
        action=UserRequestAction.APPROVE.value,
    )
    assert response["User"]["Username"] == TEST_USER_EMAIL


def test_action_user_request_reject(database_with_user_request, cognito_client_admin):
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBUserRequest)
    response = action_user_request(
        cognito_client=cognito_client_admin,
        table=table,
        email=TEST_USER_EMAIL,
        action=UserRequestAction.REJECT.value,
    )
    assert response == {}


def test_action_user_request_conflict(database_with_user_request, admin_cognito_client_with_user):
    cognito_client, _, _ = admin_cognito_client_with_user
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBUserRequest)
    with pytest.raises(ConflictException):
        response = action_user_request(
            cognito_client=cognito_client,
            table=table,
            email=TEST_USER_EMAIL,
            action=UserRequestAction.APPROVE.value,
        )


def test_action_user_request_empty(empty_database, admin_cognito_client_with_user):
    cognito_client, _, _ = admin_cognito_client_with_user
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBUserRequest)
    with pytest.raises(ResourceNotFound):
        response = action_user_request(
            cognito_client=cognito_client,
            table=table,
            email=TEST_USER_EMAIL,
            action=UserRequestAction.APPROVE.value,
        )


def test_action_user_request_bad_action(database_with_user_request, admin_cognito_client_with_user):
    cognito_client, _, _ = admin_cognito_client_with_user
    table = DBTable(access=AWSAccessLevel.WRITE, item_schema=DBUserRequest)
    with pytest.raises(ValueError):
        response = action_user_request(
            cognito_client=cognito_client,
            table=table,
            email=TEST_USER_EMAIL,
            action="dsa",
        )
