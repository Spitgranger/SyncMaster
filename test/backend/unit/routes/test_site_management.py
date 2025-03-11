from http import HTTPStatus

import pytest
from backend.service.database.db_table import DBTable, KeySchema
from backend.service.exceptions import ResourceNotFound
from backend.service.handler import lambda_handler
from backend.service.models.api.site import APIListSitesResponse, APISite
from backend.service.models.db.site import DBSite
from backend.service.util import AWSAccessLevel


def test_list_sites_handler(database_with_two_sites, list_sites_request):
    _, set_of_db_entries = database_with_two_sites

    response = lambda_handler(event=list_sites_request[0], context=list_sites_request[1])

    assert response["statusCode"] == HTTPStatus.OK
    assert set(APIListSitesResponse.model_validate_json(response["body"]).sites) == {
        site.to_api_model() for site in set_of_db_entries
    }
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_list_sites_handler_paginated(
    database_with_two_sites, list_sites_request_paginated, api_gateway_event
):
    _, set_of_db_entries = database_with_two_sites

    response = lambda_handler(
        event=list_sites_request_paginated[0], context=list_sites_request_paginated[1]
    )

    print(response["body"])

    assert response["statusCode"] == HTTPStatus.OK
    response_body = APIListSitesResponse.model_validate_json(response["body"])
    assert len(response_body.sites) == 1
    assert response_body.sites[0] in {site.to_api_model() for site in set_of_db_entries}
    assert response_body.last_key is not None
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]

    new_event = api_gateway_event(
        path=f"/protected/site-management",
        method="GET",
        query_params={"limit": "1", "start_key": response_body.last_key},
        user_role="admin",
    )

    response = lambda_handler(event=new_event[0], context=new_event[1])

    assert response["statusCode"] == HTTPStatus.OK
    response_body = APIListSitesResponse.model_validate_json(response["body"])
    assert len(response_body.sites) == 1
    assert response_body.sites[0] in {site.to_api_model() for site in set_of_db_entries}
    assert response_body.last_key is None
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_list_sites_handler_bad_role(database_with_two_sites, list_sites_request_bad_role):
    _, set_of_db_entries = database_with_two_sites

    response = lambda_handler(
        event=list_sites_request_bad_role[0], context=list_sites_request_bad_role[1]
    )

    assert response["statusCode"] == HTTPStatus.FORBIDDEN
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_create_site_handler(empty_database, create_site_request):
    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBSite)

    response = lambda_handler(event=create_site_request[0], context=create_site_request[1])

    validated_response_body = APISite.model_validate_json(response["body"])

    assert response["statusCode"] == HTTPStatus.CREATED
    assert (
        validated_response_body
        == table.get(
            key=KeySchema(pk=DBSite.item_type().value, sk=validated_response_body.site_id)
        ).to_api_model()
    )
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_create_site_handler_bad_role(empty_database, create_site_request_bad_role):
    response = lambda_handler(
        event=create_site_request_bad_role[0], context=create_site_request_bad_role[1]
    )

    assert response["statusCode"] == HTTPStatus.FORBIDDEN
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_update_site_handler(database_with_site, update_site_request):
    resource, old_site = database_with_site
    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBSite)

    response = lambda_handler(event=update_site_request[0], context=update_site_request[1])

    validated_response_body = APISite.model_validate_json(response["body"])

    assert response["statusCode"] == HTTPStatus.OK
    assert (
        validated_response_body
        == table.get(key=KeySchema(pk=old_site.pk, sk=old_site.sk)).to_api_model()
    )
    assert validated_response_body != old_site.to_api_model()
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_update_site_handler_bad_role(database_with_site, update_site_request_bad_role):
    resource, old_site = database_with_site
    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBSite)

    response = lambda_handler(
        event=update_site_request_bad_role[0], context=update_site_request_bad_role[1]
    )

    assert response["statusCode"] == HTTPStatus.FORBIDDEN
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_delete_site_handler(database_with_site, delete_site_request):
    resource, old_site = database_with_site
    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBSite)

    response = lambda_handler(event=delete_site_request[0], context=delete_site_request[1])

    assert response["statusCode"] == HTTPStatus.NO_CONTENT
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]
    with pytest.raises(ResourceNotFound):
        table.get(key=KeySchema(pk=old_site.pk, sk=old_site.sk))


def test_delete_site_handler_bad_role(database_with_site, delete_site_request_bad_role):
    resource, old_site = database_with_site
    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBSite)

    response = lambda_handler(
        event=delete_site_request_bad_role[0], context=delete_site_request_bad_role[1]
    )

    assert response["statusCode"] == HTTPStatus.FORBIDDEN
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_get_site_handler(database_with_site, get_site_request):
    resource, site = database_with_site
    table = DBTable(access=AWSAccessLevel.READ, item_schema=DBSite)

    response = lambda_handler(event=get_site_request[0], context=get_site_request[1])

    validated_response_body = APISite.model_validate_json(response["body"])

    assert response["statusCode"] == HTTPStatus.OK
    assert validated_response_body == site.to_api_model()
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_get_site_handler_bad_role(database_with_site, get_site_request_bad_role):
    resource, site = database_with_site

    response = lambda_handler(
        event=get_site_request_bad_role[0], context=get_site_request_bad_role[1]
    )

    assert response["statusCode"] == HTTPStatus.FORBIDDEN
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]
