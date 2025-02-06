import json
from http import HTTPStatus

from backend.service.handler import lambda_handler
from backend.service.user_authentication.user_authentication import CognitoClient


def test_signup(cognito_mock, post_signup_request):
    event, context = post_signup_request

    response = lambda_handler(event=event, context=context)

    # Check the response
    assert response["statusCode"] == 500
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_signin(cognito_mock, post_signin_request):
    event, context = post_signin_request

    response = lambda_handler(event=event, context=context)

    # Check the response
    assert response["statusCode"] == 500
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_create_user(cognito_mock, post_create_user_request):
    event, context = post_create_user_request

    response = lambda_handler(event=event, context=context)

    # Check the response
    assert response["statusCode"] == 500
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_get_users(cognito_mock, post_get_users_request):
    event, context = post_get_users_request

    response = lambda_handler(event=event, context=context)

    # Check the response
    assert response["statusCode"] == 500
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_update_user(cognito_mock, post_update_user_request):
    event, context = post_update_user_request

    response = lambda_handler(event=event, context=context)

    # Check the response
    assert response["statusCode"] == 500
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]
