import json
import uuid
from datetime import datetime

import pytest

from ..constants import (
    CURRENT_DATE_TIME,
    FUTURE_DATE_TIME,
    PREV_DATE_TIME,
    TEST_DOCUMENT_ID,
    TEST_PARENT_FOLDER_ID,
    TEST_S3_FILE_KEY,
    TEST_SITE_ID,
    TEST_SITE_LATITUDE,
    TEST_SITE_LATITUDE_ALT,
    TEST_SITE_LONGITUDE,
    TEST_SITE_RANGE,
    TEST_USER_ID,
)


@pytest.fixture()
def api_gateway_event():
    def _api_gateway_event(
        path: str,
        method: str,
        body: str = "",
        path_params: dict[str, str] = {},
        query_params: dict[str, str] = {},
        time: datetime = CURRENT_DATE_TIME,
        user_role: str = "contractor",
    ):
        request_id = str(uuid.uuid4())

        request_context = {
            "accountId": "123456789012",
            "apiId": "id",
            "authorizer": {
                "claims": {
                    "sub": TEST_USER_ID,
                    "email_verified": False,
                    "iss": "https://cognito-idp.us-east-2.amazonaws.com/us-east-2_AAAAAAAA",
                    "cognito:username": "Test@gmail.com",
                    "custom:company": "testcompany",
                    "origin_jti": "555555aa-5aa5-5555-a555-a5aaa5a555a5",
                    "aud": "55aaaa5a5a555aa5aa5a5aaa5a",
                    "event_id": "555555aa-5aa5-5555-a555-a5aaa5a555a5",
                    "token_use": "id",
                    "auth_time": 1738377493,
                    "exp": 1738420693,
                    "custom:role": user_role,
                    "iat": 1738377493,
                    "jti": "555555aa-5aa5-5555-a555-a5aaa5a555a5",
                    "email": "Test@gmail.com",
                },
                "scopes": None,
            },
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
            "requestTime": time.isoformat(),
            "requestTimeEpoch": time.timestamp() * 1000,
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
            "queryStringParameters": query_params,
            "multiValueQueryStringParameters": {},
            "requestContext": request_context,
            "pathParameters": path_params,
            "stageVariables": None,
            "body": body,
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
def enter_site_request(api_gateway_event):
    event, context = api_gateway_event(
        path=f"/protected/site/{TEST_SITE_ID}/enter",
        method="POST",
        path_params={"site_id": TEST_SITE_ID},
    )
    yield event, context


@pytest.fixture()
def exit_site_request(api_gateway_event):
    event, context = api_gateway_event(
        path=f"/protected/site/{TEST_SITE_ID}/exit",
        method="PATCH",
        path_params={"site_id": TEST_SITE_ID},
        time=FUTURE_DATE_TIME,
    )
    yield event, context


@pytest.fixture()
def list_site_visits_request(api_gateway_event):
    event, context = api_gateway_event(
        path=f"/protected/site/visits",
        method="GET",
        query_params={
            "from_time": PREV_DATE_TIME.isoformat(),
            "to_time": FUTURE_DATE_TIME.isoformat(),
            "limit": "2",
        },
        user_role="admin",
    )
    yield event, context


@pytest.fixture()
def list_site_visits_request_paginated(api_gateway_event):
    event, context = api_gateway_event(
        path=f"/protected/site/visits",
        method="GET",
        query_params={
            "limit": "1",
        },
        user_role="admin",
    )
    yield event, context


@pytest.fixture()
def list_site_visits_request_bad_role(api_gateway_event):
    event, context = api_gateway_event(
        path=f"/protected/site/visits", method="GET", user_role="contractor"
    )
    yield event, context


@pytest.fixture()
def post_signup_request(api_gateway_event):
    body = json.dumps(
        {
            "email": "test@gmail.com",
            "name": "Test test",
            "password": "test1234!",
            "attributes": {"custom:role": "contractor", "custom:company": "testcompany"},
        }
    )
    event, context = api_gateway_event("/protected/users/signup", "POST", body)
    yield event, context


@pytest.fixture()
def post_signin_request(api_gateway_event):
    body = json.dumps({"email": "Test@gmail.com", "password": "GougGoug123!"})
    event, context = api_gateway_event("/unprotected/auth/signin", "POST", body)
    yield event, context


@pytest.fixture()
def post_create_user_request(api_gateway_event):
    body = json.dumps(
        {
            "email": "test@gmail.com",
            "password": "test1234!",
            "attributes": {
                "custom:role": "contractor",
                "custom:company": "testcompany",
                "name": "test",
            },
        }
    )
    event, context = api_gateway_event("/protected/users/create_user", "POST", body)
    yield event, context


@pytest.fixture()
def post_get_users_request(api_gateway_event):
    body = json.dumps({"attributes": {}})
    event, context = api_gateway_event("/protected/users/get_users", "POST", body)
    yield event, context


@pytest.fixture()
def post_update_user_request(api_gateway_event):
    body = json.dumps({"email": "test@test.com", "attributes": [{"Name": "name", "Value": "test"}]})
    event, context = api_gateway_event("/protected/users/update_user", "POST", body)
    yield event, context


@pytest.fixture()
def get_signout_user_request(api_gateway_event):
    event, context = api_gateway_event('/protected/users/update_user?user_token="eyqq81712"', "GET")
    yield event, context


@pytest.fixture()
def get_presigned_url_request(api_gateway_event):
    event, context = api_gateway_event(
        path=f"/protected/documents/get_presigned_url/{TEST_S3_FILE_KEY}",
        method="GET",
        path_params={"s3_key": TEST_S3_FILE_KEY},
    )
    yield event, context


@pytest.fixture()
def upload_document_request(api_gateway_event, db_document):
    event, context = api_gateway_event(
        path="/protected/documents/upload",
        method="POST",
        body=json.dumps(
            {
                "document_name": db_document.document_name,
                "document_type": db_document.document_type,
                "parent_folder_id": db_document.parent_folder_id,
                "site_id": db_document.site_id,
                "document_path": db_document.document_path,
                "s3_key": db_document.s3_key,
                "e_tag": db_document.s3_e_tag,
                "user_id": db_document.last_modified_by,
                "requires_ack": db_document.requires_ack,
                "document_expiry": db_document.document_expiry,
            }
        ),
    )
    yield event, context


@pytest.fixture()
def get_files_request(api_gateway_event):
    event, context = api_gateway_event(
        path=f"/protected/documents/{TEST_SITE_ID}/{TEST_PARENT_FOLDER_ID}/get_files",
        method="GET",
        path_params={"site_id": TEST_S3_FILE_KEY, "folder": TEST_PARENT_FOLDER_ID},
    )
    yield event, context


@pytest.fixture()
def delete_files_request(api_gateway_event):
    event, context = api_gateway_event(
        path=f"/protected/documents/delete",
        method="DELETE",
        query_params={
            "document_id": TEST_DOCUMENT_ID,
            "parent_folder_id": TEST_PARENT_FOLDER_ID,
            "site_id": TEST_SITE_ID,
        },
        user_role="admin",
    )
    yield event, context


@pytest.fixture()
def delete_files_bad_role_request(api_gateway_event):
    event, context = api_gateway_event(
        path=f"/protected/documents/delete",
        method="DELETE",
        query_params={
            "document_id": TEST_DOCUMENT_ID,
            "parent_folder_id": TEST_PARENT_FOLDER_ID,
            "site_id": TEST_SITE_ID,
        },
        user_role="contractor",
    )
    yield event, context


@pytest.fixture()
def create_site_request(api_gateway_event):
    event, context = api_gateway_event(
        path=f"/protected/site-management",
        method="POST",
        user_role="admin",
        body=json.dumps(
            {
                "site_id": TEST_SITE_ID,
                "longitude": str(TEST_SITE_LONGITUDE),
                "latitude": str(TEST_SITE_LATITUDE),
                "acceptable_range": str(TEST_SITE_RANGE),
            }
        ),
    )
    yield event, context


@pytest.fixture()
def create_site_request_bad_role(api_gateway_event):
    event, context = api_gateway_event(
        path=f"/protected/site-management",
        method="POST",
        user_role="contractor",
        body=json.dumps(
            {
                "site_id": TEST_SITE_ID,
                "longitude": str(TEST_SITE_LONGITUDE),
                "latitude": str(TEST_SITE_LATITUDE),
                "acceptable_range": str(TEST_SITE_RANGE),
            }
        ),
    )
    yield event, context


@pytest.fixture()
def update_site_request(api_gateway_event):
    event, context = api_gateway_event(
        path=f"/protected/site-management/{TEST_SITE_ID}",
        method="PATCH",
        user_role="admin",
        time=FUTURE_DATE_TIME,
        path_params={"site_id": TEST_SITE_ID},
        body=json.dumps(
            {
                "latitude": str(TEST_SITE_LATITUDE_ALT),
            }
        ),
    )
    yield event, context


@pytest.fixture()
def update_site_request_bad_role(api_gateway_event):
    event, context = api_gateway_event(
        path=f"/protected/site-management/{TEST_SITE_ID}",
        method="PATCH",
        user_role="contractor",
        time=FUTURE_DATE_TIME,
        path_params={"site_id": TEST_SITE_ID},
        body=json.dumps(
            {
                "latitude": str(TEST_SITE_LATITUDE_ALT),
            }
        ),
    )
    yield event, context


@pytest.fixture()
def delete_site_request(api_gateway_event):
    event, context = api_gateway_event(
        path=f"/protected/site-management/{TEST_SITE_ID}",
        method="DELETE",
        user_role="admin",
        time=FUTURE_DATE_TIME,
        path_params={"site_id": TEST_SITE_ID},
    )
    yield event, context


@pytest.fixture()
def delete_site_request_bad_role(api_gateway_event):
    event, context = api_gateway_event(
        path=f"/protected/site-management/{TEST_SITE_ID}",
        method="DELETE",
        user_role="contractor",
        time=FUTURE_DATE_TIME,
        path_params={"site_id": TEST_SITE_ID},
    )
    yield event, context


@pytest.fixture()
def get_site_request(api_gateway_event):
    event, context = api_gateway_event(
        path=f"/protected/site-management/{TEST_SITE_ID}",
        method="GET",
        user_role="admin",
        path_params={"site_id": TEST_SITE_ID},
    )
    yield event, context


@pytest.fixture()
def get_site_request_bad_role(api_gateway_event):
    event, context = api_gateway_event(
        path=f"/protected/site-management/{TEST_SITE_ID}",
        method="GET",
        user_role="contractor",
        path_params={"site_id": TEST_SITE_ID},
    )
    yield event, context


@pytest.fixture()
def list_sites_request(api_gateway_event):
    event, context = api_gateway_event(
        path=f"/protected/site-management", method="GET", user_role="admin"
    )
    yield event, context


@pytest.fixture()
def list_sites_request_paginated(api_gateway_event):
    event, context = api_gateway_event(
        path=f"/protected/site-management",
        method="GET",
        user_role="admin",
        query_params={"limit": "1"},
    )
    yield event, context


@pytest.fixture()
def list_sites_request_bad_role(api_gateway_event):
    event, context = api_gateway_event(
        path=f"/protected/site-management", method="GET", user_role="contractor"
    )
    yield event, context
