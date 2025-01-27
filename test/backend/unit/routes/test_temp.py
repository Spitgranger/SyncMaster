import json
from http import HTTPStatus

from backend.service.handler import lambda_handler


def test_temp(get_request):
    response = lambda_handler(event=get_request[0], context=get_request[1])
    assert response["statusCode"] == HTTPStatus.OK
    assert json.loads(response["body"]) == {"Hello": "World"}
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]
