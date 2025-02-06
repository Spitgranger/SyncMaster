from http import HTTPStatus

import pytest
from backend.service.exceptions import (
    BadRequestException,
    ConflictException,
    ResourceNotFound,
    UnauthorizedException,
    ForceChangePasswordException,
)
from backend.service.user_authentication.user_authentication import (
    admin_update_user_attributes_handler,
    signin_user_handler,
    signup_user_handler,
    admin_create_user_handler,
    admin_get_users_handler,
)


def test_signup_success(cognito_client, signup_request):
    response = signup_user_handler(signup_request, cognito_client)
    print(response.body)
    assert response.status_code == HTTPStatus.CREATED.value
    assert "UserConfirmed" in response.body


def test_create_user_success(cognito_client_admin, create_user_request):
    response = admin_create_user_handler(create_user_request, cognito_client_admin)
    print(response.body)
    assert response.status_code == HTTPStatus.CREATED.value
    assert "User" in response.body


def test_create_user_existing_user(cognito_client_admin, create_user_request):
    admin_create_user_handler(create_user_request, cognito_client_admin)
    with pytest.raises(ConflictException) as excinfo:
        admin_create_user_handler(create_user_request, cognito_client_admin)
    assert "User with this username already exists" in str(excinfo.value)


def test_get_users_success(cognito_client_admin, get_users_request, create_user_request):
    admin_create_user_handler(create_user_request, cognito_client_admin)
    for i in range(0, 100):
        create_user_request.email = f"test{i}@test.com"
        admin_create_user_handler(create_user_request, cognito_client_admin)
    response = admin_get_users_handler(get_users_request, cognito_client_admin)
    print(response.body)
    assert response.status_code == HTTPStatus.OK.value
    assert response.body


def test_update_user_attribute(
    cognito_client_admin,
    get_users_request_changed,
    create_user_request,
    update_user_attribute_request,
):
    admin_create_user_handler(create_user_request, cognito_client_admin)
    response = admin_update_user_attributes_handler(
        update_user_attribute_request, cognito_client_admin
    )
    response = admin_get_users_handler(get_users_request_changed, cognito_client_admin)
    print(response.body)
    assert response.status_code == HTTPStatus.OK.value
    assert response.body


def test_update_user_attribute_not_existing(
    cognito_client_admin,
    update_user_attribute_request,
):
    with pytest.raises(ResourceNotFound) as excinfo:
        admin_update_user_attributes_handler(update_user_attribute_request, cognito_client_admin)
    assert "Resource [username] of type [user] not found" in str(excinfo.value)


def test_signup_existing_user(cognito_client, signup_request):
    cognito_client.signup_user(signup_request.email, signup_request.password, [])
    with pytest.raises(ConflictException) as excinfo:
        signup_user_handler(signup_request, cognito_client)
    assert "User with this username already exists" in str(excinfo.value)


def test_signup_bad_password(cognito_client, signup_request_bad_password):
    with pytest.raises(BadRequestException) as excinfo:
        signup_user_handler(signup_request_bad_password, cognito_client)
    assert "Password does not meet organization policy requirements" in str(excinfo.value)


def test_signin_success(cognito_client_with_user):
    cognito_client, _, signin_request_location = cognito_client_with_user
    response = signin_user_handler(signin_request_location, cognito_client)
    assert response.status_code == HTTPStatus.OK.value
    assert "AccessToken" in response.body
    assert "IdToken" in response.body


def test_signin_fail_location(cognito_client_with_user):
    cognito_client, signin_request, _ = cognito_client_with_user
    with pytest.raises(UnauthorizedException) as excinfo:
        signin_user_handler(signin_request, cognito_client)
    assert "Location not provided for contractor" in str(excinfo.value)


def test_signin_password_challenge(
    cognito_client_admin, cognito_client, create_user_request, signin_request
):
    cognito_client_admin.admin_create_user(create_user_request.email, [], "TestTest123!")
    with pytest.raises(ForceChangePasswordException) as excinfo:
        signin_user_handler(signin_request, cognito_client)
    assert "Password has expired and must be reset" in str(excinfo.value)


def test_signin_wrong_password(cognito_client_with_user):
    cognito_client, signin_request, _ = cognito_client_with_user
    signin_request.password = "test12341!"
    with pytest.raises(UnauthorizedException) as excinfo:
        signin_user_handler(signin_request, cognito_client)
    assert "Incorrect Credentials" in str(excinfo.value)


def test_signin_does_not_exist(cognito_client, signin_request):
    with pytest.raises(ResourceNotFound):
        signin_user_handler(signin_request, cognito_client)
