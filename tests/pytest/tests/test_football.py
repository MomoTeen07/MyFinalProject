"""Contrats de l'API football : schémas JSON et codes de statut."""

import allure
import pytest
from jsonschema import validate

pytestmark = allure.feature("API football")


@allure.story("Championnats")
@allure.severity(allure.severity_level.CRITICAL)
def test_leagues_match_the_contract(api, api_url, schemas):
    response = api.get(f"{api_url}/api/football/leagues", timeout=10)

    assert response.status_code == 200
    payload = response.json()
    validate(payload, schemas["leagues"])
    assert {league["code"] for league in payload} == {"PL", "FL1", "PD", "SA", "BL1", "CL"}


@allure.story("Classement")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("code", ["PL", "FL1", "PD", "SA", "BL1", "CL"])
def test_standings_match_the_contract(api, api_url, schemas, code):
    response = api.get(f"{api_url}/api/football/leagues/{code}/standings", timeout=10)

    assert response.status_code == 200
    payload = response.json()
    validate(payload, schemas["standings"])
    assert [row["position"] for row in payload] == sorted(
        row["position"] for row in payload
    )


@allure.story("Calendrier")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize("code", ["PL", "FL1"])
def test_matches_match_the_contract(api, api_url, schemas, code):
    response = api.get(f"{api_url}/api/football/leagues/{code}/matches", timeout=10)

    assert response.status_code == 200
    payload = response.json()
    validate(payload, schemas["matches"])
    assert payload, "Le calendrier ne doit pas être vide en mode simulé"


@allure.story("Équipe")
@allure.severity(allure.severity_level.NORMAL)
def test_team_details_match_the_contract(api, api_url, schemas):
    response = api.get(f"{api_url}/api/football/leagues/PL/teams/57", timeout=10)

    assert response.status_code == 200
    payload = response.json()
    validate(payload, schemas["team"])
    assert payload["name"] == "Arsenal"


@allure.story("Erreurs")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize(
    "path",
    [
        "/api/football/leagues/XX/standings",
        "/api/football/leagues/ZZ/matches",
        "/api/football/leagues/PL/teams/999999",
    ],
)
def test_unknown_resources_return_404(api, api_url, path):
    response = api.get(f"{api_url}{path}", timeout=10)

    assert response.status_code == 404
    assert response.json()["detail"]


@allure.story("Erreurs")
@allure.severity(allure.severity_level.MINOR)
def test_team_id_must_be_an_integer(api, api_url):
    response = api.get(f"{api_url}/api/football/leagues/PL/teams/abc", timeout=10)

    assert response.status_code == 422
