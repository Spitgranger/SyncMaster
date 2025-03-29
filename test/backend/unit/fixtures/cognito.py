import boto3
import pytest
from backend.service.environment import COGNITO_ACCESS_ROLE
from backend.service.models.user_authentication.user_request_response import (
    AdminSignupRequest,
    GetUsersByAttributeRequest,
    SigninRequest,
    SignupRequest,
    UpdateUserAttributeRequest,
)
from backend.service.user_authentication.user_authentication import (
    AdminCognitoClient,
    CognitoClient,
)
from backend.service.util import create_client_with_role
from moto import mock_aws

from ..constants import TEST_SITE_ID, TEST_USER_EMAIL


@pytest.fixture
def cognito_mock():
    """Creates a mock Cognito client."""
    with mock_aws():
        client = boto3.client("cognito-idp")
        response = client.create_user_pool(PoolName="test-user-pool")
        user_pool_id = response["UserPool"]["Id"]
        response = client.create_user_pool_client(UserPoolId=user_pool_id, ClientName="test-client")
        client_id = response["UserPoolClient"]["ClientId"]
        response = client.create_group(UserPoolId=user_pool_id, GroupName="admin")
        response = client.create_group(UserPoolId=user_pool_id, GroupName="employee")
        response = client.create_group(UserPoolId=user_pool_id, GroupName="contractor")
        yield client, client_id, user_pool_id


@pytest.fixture
def cognito_mock_admin():
    """Creates a mock Cognito client with IAM role"""
    with mock_aws():
        client = create_client_with_role("cognito-idp", COGNITO_ACCESS_ROLE)
        response = client.create_user_pool(PoolName="test-user-pool")
        user_pool_id = response["UserPool"]["Id"]
        response = client.create_user_pool_client(UserPoolId=user_pool_id, ClientName="test-client")
        client_id = response["UserPoolClient"]["ClientId"]
        response = client.create_group(UserPoolId=user_pool_id, GroupName="admin")
        response = client.create_group(UserPoolId=user_pool_id, GroupName="employee")
        response = client.create_group(UserPoolId=user_pool_id, GroupName="contractor")
        yield client, client_id, user_pool_id


@pytest.fixture
def cognito_client(cognito_mock):
    """Returns a CognitoClient instance with the mocked Cognito client."""
    client, client_id, _ = cognito_mock
    cognito_client = CognitoClient(client_id)
    cognito_client._client = client  # Override with mock
    yield cognito_client


@pytest.fixture
def cognito_client_admin(cognito_mock):
    """Returns a AdminCognitoClient instance with the mocked Cognito client."""
    client, client_id, user_pool_id = cognito_mock
    cognito_client = AdminCognitoClient(client_id, user_pool_id)
    cognito_client._client = client  # Override with mock
    yield cognito_client


@pytest.fixture
def cognito_client_admin_fake(cognito_mock):
    """Returns a AdminCognitoClient instance with the mocked Cognito client."""
    client, client_id, user_pool_id = cognito_mock
    cognito_client = AdminCognitoClient(client_id, "awaww2")
    cognito_client._client = client  # Override with mock
    yield cognito_client


@pytest.fixture
def signup_request():
    """Creates a mock signup request."""
    yield SignupRequest(
        email="testuser@example.com",
        password="TestTest123!",
        attributes={"custom:role": "contractor", "name": "test"},
    )


@pytest.fixture
def create_user_request():
    """Creates a mock create user request."""
    yield AdminSignupRequest(
        email="testuser@example.com",
        attributes={"custom:role": "admin", "name": "test"},
    )


@pytest.fixture
def get_users_request():
    """Creates a mock create user request."""
    yield GetUsersByAttributeRequest(
        attributes={"custom:role": "admin"},
    )


@pytest.fixture
def get_users_request_changed():
    """Creates a mock create user request."""
    yield GetUsersByAttributeRequest(
        attributes={"custom:role": "contractor"},
    )


@pytest.fixture
def update_user_attribute_request():
    """Creates a mock create user request."""
    yield UpdateUserAttributeRequest(
        email="testuser@example.com",
        attributes=[{"Name": "custom:role", "Value": "contractor"}],
    )


@pytest.fixture
def signup_request_bad_password():
    """Creates a mock signup request with bad password"""
    yield SignupRequest(
        email="testuser@example.com",
        password="testtest",
        attributes={"custom:role": "admin", "name": "test"},
    )


@pytest.fixture
def signin_request():
    """Creates a mock signin request."""
    yield SigninRequest(email="testuser@example.com", password="TestTest123!")


@pytest.fixture
def admin_cognito_client_with_user(cognito_mock):
    """Creates and registers a user in the mock Cognito user pool."""
    client, client_id, user_pool_id = cognito_mock
    cognito_client = AdminCognitoClient(client_id, user_pool_id)
    cognito_client._client = client

    email = TEST_USER_EMAIL
    password = "TestPassword123!"

    client.admin_create_user(
        UserPoolId=user_pool_id,
        Username=email,
        UserAttributes=[
            {"Name": "email", "Value": email},
            {"Name": "custom:role", "Value": "contractor"},
        ],
        MessageAction="SUPPRESS",  # Suppresses email verification in the mock
    )

    client.admin_set_user_password(
        UserPoolId=user_pool_id,
        Username=email,
        Password=password,
        Permanent=True,
    )

    yield (
        cognito_client,
        SigninRequest(email=email, password=password),
        SigninRequest(
            email=email,
            password=password,
            location=[43.2588581564085, -79.92097591189501],
            site_id=TEST_SITE_ID,
        ),
    )


@pytest.fixture
def cognito_client_with_user(cognito_mock):
    """Creates and registers a user in the mock Cognito user pool."""
    client, client_id, user_pool_id = cognito_mock
    cognito_client = CognitoClient(client_id)
    cognito_client._client = client

    email = TEST_USER_EMAIL
    password = "TestPassword123!"

    client.admin_create_user(
        UserPoolId=user_pool_id,
        Username=email,
        UserAttributes=[
            {"Name": "email", "Value": email},
            {"Name": "custom:role", "Value": "contractor"},
        ],
        MessageAction="SUPPRESS",  # Suppresses email verification in the mock
    )

    client.admin_set_user_password(
        UserPoolId=user_pool_id,
        Username=email,
        Password=password,
        Permanent=True,
    )

    yield (
        cognito_client,
        SigninRequest(email=email, password=password),
        SigninRequest(
            email=email,
            password=password,
            location=[43.2588581564085, -79.92097591189501],
            site_id=TEST_SITE_ID,
        ),
    )
