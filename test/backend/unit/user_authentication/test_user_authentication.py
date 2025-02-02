from http import HTTPStatus

from backend.service.user_authentication.user_authentication import (
    signin_user_handler,
    signup_user_handler,
)


def test_signup_success(cognito_client, signup_request):
    response = signup_user_handler(signup_request, cognito_client)
    print(response.body)
    assert response.status_code == HTTPStatus.CREATED.value
    assert "UserConfirmed" in response.body


def test_signup_existing_user(cognito_client, signup_request):
    cognito_client.signup_user(signup_request.email, signup_request.password, [])
    response = signup_user_handler(signup_request, cognito_client)
    assert response.status_code == HTTPStatus.CONFLICT.value
    assert "UsernameExistsException" in response.body["error"]


def test_signup_bad_password(cognito_client, signup_request_bad_password):
    response = signup_user_handler(signup_request_bad_password, cognito_client)
    print(response.body)
    assert response.status_code == HTTPStatus.BAD_REQUEST.value
    assert "InvalidPasswordException" in response.body["error"]


def test_signin_success(cognito_client_with_user):
    cognito_client, signin_request = cognito_client_with_user
    response = signin_user_handler(signin_request, cognito_client)
    print(response.body)
    assert response.status_code == HTTPStatus.OK.value
    assert "AccessToken" in response.body
    assert "IdToken" in response.body


def test_signin_wrong_password(cognito_client_with_user):
    cognito_client, signin_request = cognito_client_with_user
    signin_request.password = "test12341!"
    response = signin_user_handler(signin_request, cognito_client)
    assert response.status_code == HTTPStatus.UNAUTHORIZED.value
    assert "NotAuthorizedException" in response.body["error"]


def test_signin_does_not_exist(cognito_client, signin_request):
    response = signin_user_handler(signin_request, cognito_client)
    assert response.status_code == HTTPStatus.NOT_FOUND.value
    assert "UserNotFoundException" in response.body["error"]
