import datetime
import uuid

import pytest


@pytest.fixture()
def api_gateway_event():
    def _api_gateway_event(path: str, method: str):
        request_id = str(uuid.uuid4())

        request_context = {
            "accountId": "123456789012",
            "apiId": "id",
            "authorizer": {"claims": None, "scopes": None},
            "domainName": "id.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "id",
            "extendedRequestId": "request-id",
            "httpMethod": method,
            "identity": {
                "accessKey": None,
                "accountId": None,
                "caller": None,
                "cognitoAuthenticationProvider": None,
                "cognitoAuthenticationType": None,
                "cognitoIdentityId": None,
                "cognitoIdentityPoolId": None,
                "principalOrgId": None,
                "sourceIp": "IP",
                "user": None,
                "userAgent": "user-agent",
                "userArn": None,
                "clientCert": {
                    "clientCertPem": "CERT_CONTENT",
                    "subjectDN": "www.example.com",
                    "issuerDN": "Example issuer",
                    "serialNumber": "a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1",
                    "validity": {
                        "notBefore": "May 28 12:30:02 2019 GMT",
                        "notAfter": "Aug  5 09:36:04 2021 GMT",
                    },
                },
            },
            "path": path,
            "protocol": "HTTP/1.1",
            "requestId": request_id,
            "requestTime": datetime.datetime.now().timestamp(),
            "requestTimeEpoch": datetime.datetime.now(),
            "resourceId": None,
            "resourcePath": path,
            "stage": "$default",
        }

        event = {
            "resource": path,
            "path": path,
            "httpMethod": method,
            "headers": {},
            "multiValueHeaders": {},
            "queryStringParameters": {},
            "multiValueQueryStringParameters": {},
            "requestContext": request_context,
            "pathParameters": None,
            "stageVariables": None,
            "body": "",
            "isBase64Encoded": False,
        }

        class Context:
            aws_request_id = event["requestContext"]["requestId"]
            function_name = "function_name"
            memory_limit_in_mb = 1
            invoked_function_arn = "function_arn"

        return event, Context()

    return _api_gateway_event


@pytest.fixture()
def get_request(api_gateway_event):
    event, context = api_gateway_event("/test", "GET")
    yield event, context
