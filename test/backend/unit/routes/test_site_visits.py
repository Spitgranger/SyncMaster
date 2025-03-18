import json
from http import HTTPStatus

from backend.service.database.db_table import DBTable, KeySchema
from backend.service.handler import lambda_handler
from backend.service.models.api.site_visit import APIListSiteVisitResponse, APISiteVisit
from backend.service.models.db.site_visit import DBSiteVisit
from backend.service.util import AWSAccessLevel


def test_list_sites_handler(database_with_two_site_visits, list_site_visits_request):
    _, set_of_db_entries = database_with_two_site_visits

    response = lambda_handler(
        event=list_site_visits_request[0], context=list_site_visits_request[1]
    )

    assert response["statusCode"] == HTTPStatus.OK
    assert set(APIListSiteVisitResponse.model_validate_json(response["body"]).visits) == {
        visit.to_api_model() for visit in set_of_db_entries
    }
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_list_sites_handler_paginated(
    database_with_two_site_visits, list_site_visits_request_paginated, api_gateway_event
):
    _, set_of_db_entries = database_with_two_site_visits

    response = lambda_handler(
        event=list_site_visits_request_paginated[0], context=list_site_visits_request_paginated[1]
    )

    assert response["statusCode"] == HTTPStatus.OK
    response_body = APIListSiteVisitResponse.model_validate_json(response["body"])
    assert len(response_body.visits) == 1
    assert response_body.visits[0] in [visit.to_api_model() for visit in set_of_db_entries]
    assert response_body.last_key is not None
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]

    new_event = api_gateway_event(
        path=f"/protected/site/visits",
        method="GET",
        query_params={"limit": "1", "start_key": response_body.last_key},
        user_role="admin",
        user_groups=["admin"],
    )

    response = lambda_handler(event=new_event[0], context=new_event[1])

    assert response["statusCode"] == HTTPStatus.OK
    response_body = APIListSiteVisitResponse.model_validate_json(response["body"])
    assert len(response_body.visits) == 1
    assert response_body.visits[0] in [visit.to_api_model() for visit in set_of_db_entries]
    assert response_body.last_key is None
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_list_sites_handler_bad_role(
    database_with_two_site_visits, list_site_visits_request_bad_role
):
    _, set_of_db_entries = list_site_visits_request_bad_role

    response = lambda_handler(
        event=list_site_visits_request_bad_role[0], context=list_site_visits_request_bad_role[1]
    )

    assert response["statusCode"] == HTTPStatus.FORBIDDEN
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_exit_site_handler(
    database_with_two_site_visits, exit_site_request, db_site_visit_only_entry
):
    response = lambda_handler(event=exit_site_request[0], context=exit_site_request[1])

    table = DBTable(AWSAccessLevel.READ, item_schema=DBSiteVisit)

    assert response["statusCode"] == HTTPStatus.OK
    assert (
        APISiteVisit.model_validate_json(response["body"])
        == table.get(
            key=KeySchema(pk=db_site_visit_only_entry.pk, sk=db_site_visit_only_entry.sk)
        ).to_api_model()
    )
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]


def test_enter_site_handler(empty_database, enter_site_request, db_site_visit_only_entry):
    response = lambda_handler(event=enter_site_request[0], context=enter_site_request[1])

    table = DBTable(AWSAccessLevel.READ, item_schema=DBSiteVisit)

    validated_response_body = APISiteVisit.model_validate_json(response["body"])
    assert validated_response_body.exit_time == None

    assert response["statusCode"] == HTTPStatus.CREATED
    assert (
        validated_response_body
        == table.get(
            key=KeySchema(pk=db_site_visit_only_entry.pk, sk=db_site_visit_only_entry.sk)
        ).to_api_model()
    )
    assert response["multiValueHeaders"]["Content-Type"] == ["application/json"]
