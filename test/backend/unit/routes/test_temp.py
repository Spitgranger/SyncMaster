import json
from http import HTTPStatus

from backend.service.handler import lambda_handler
from backend.service.user_authentication.user_authentication import CognitoClient


def test_temp(get_request):
    response = lambda_handler(event=get_request[0], context=get_request[1])
    assert response["statusCode"] == HTTPStatus.OK
    assert json.loads(response["body"]) == {"Hello": "World"}
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


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
