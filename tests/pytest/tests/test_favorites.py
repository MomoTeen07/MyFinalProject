"""Favoris : scénario chaîné, isolation des comptes et validation."""

import allure
import pytest
from jsonschema import validate

pytestmark = allure.feature("Favoris")


def add_favorite(api, api_url, headers, **overrides):
    payload = {
        "team_id": 57,
        "league_code": "PL",
        "team_name": "Arsenal",
        "team_crest": "",
    }
    payload.update(overrides)
    return api.post(
        f"{api_url}/api/favorites", json=payload, headers=headers, timeout=10
    )


@allure.story("Scénario chaîné")
@allure.severity(allure.severity_level.BLOCKER)
def test_chained_scenario_add_list_delete(api, api_url, user, schemas):
    """Connexion -> ajout -> consultation -> suppression -> vérification."""
    created = add_favorite(api, api_url, user["headers"])
    assert created.status_code == 201, created.text
    favorite = created.json()
    validate(favorite, schemas["favorite"])

    listing = api.get(f"{api_url}/api/favorites", headers=user["headers"], timeout=10)
    assert listing.status_code == 200
    assert [item["id"] for item in listing.json()] == [favorite["id"]]
    validate(listing.json()[0], schemas["favorite"])

    deleted = api.delete(
        f"{api_url}/api/favorites/{favorite['id']}", headers=user["headers"], timeout=10
    )
    assert deleted.status_code == 204

    empty = api.get(f"{api_url}/api/favorites", headers=user["headers"], timeout=10)
    assert empty.status_code == 200
    assert empty.json() == []


@allure.story("Règles métier")
@allure.severity(allure.severity_level.CRITICAL)
def test_the_same_team_cannot_be_added_twice(api, api_url, user, favorite):
    duplicate = add_favorite(api, api_url, user["headers"])

    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "Team already in favorites"


@allure.story("Règles métier")
@allure.severity(allure.severity_level.CRITICAL)
def test_favorites_are_scoped_to_the_authenticated_user(
    api, api_url, user, other_user, favorite
):
    other_listing = api.get(
        f"{api_url}/api/favorites", headers=other_user["headers"], timeout=10
    )

    assert other_listing.status_code == 200
    assert other_listing.json() == []


@allure.story("Règles métier")
@allure.severity(allure.severity_level.CRITICAL)
def test_newest_favorite_is_listed_first(api, api_url, user):
    first = add_favorite(api, api_url, user["headers"], team_id=57, team_name="Arsenal")
    second = add_favorite(
        api,
        api_url,
        user["headers"],
        team_id=61,
        team_name="Chelsea",
        league_code="PL",
    )

    listing = api.get(f"{api_url}/api/favorites", headers=user["headers"], timeout=10)

    assert first.status_code == 201 and second.status_code == 201
    assert [item["team_name"] for item in listing.json()] == ["Chelsea", "Arsenal"]


@allure.story("Règles métier")
@allure.severity(allure.severity_level.NORMAL)
def test_accented_team_names_are_preserved(api, api_url, user):
    created = add_favorite(
        api, api_url, user["headers"], team_id=78, team_name="Atlético de Madrid"
    )

    assert created.status_code == 201
    assert created.json()["team_name"] == "Atlético de Madrid"


@allure.story("Validation")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize(
    "case",
    [
        "team-id-nul",
        "team-id-negatif",
        "team-id-texte",
        "nom-vide",
        "nom-espaces",
        "nom-trop-long",
        "code-championnat-minuscule",
        "code-championnat-trop-long",
        "ecusson-trop-long",
    ],
)
def test_invalid_favorites_are_rejected(api, api_url, user, dataset, case):
    entry = next(item for item in dataset["invalid_favorites"] if item["id"] == case)
    payload = dict(entry["payload"])
    if "length" in entry:
        payload[entry["champ"]] = "X" * entry["length"]

    response = api.post(
        f"{api_url}/api/favorites", json=payload, headers=user["headers"], timeout=10
    )

    assert response.status_code == 422, response.text
    fields = {error["loc"][-1] for error in response.json()["detail"]}
    assert entry["champ"] in fields


@allure.story("Sécurité")
@allure.severity(allure.severity_level.BLOCKER)
def test_favorites_require_authentication(api, api_url):
    listing = api.get(f"{api_url}/api/favorites", timeout=10)
    creation = api.post(
        f"{api_url}/api/favorites",
        json={"team_id": 57, "team_name": "Arsenal"},
        timeout=10,
    )

    assert listing.status_code == 401
    assert creation.status_code == 401


@allure.story("Sécurité")
@allure.severity(allure.severity_level.BLOCKER)
def test_a_user_cannot_delete_another_users_favorite(
    api, api_url, other_user, favorite
):
    response = api.delete(
        f"{api_url}/api/favorites/{favorite['id']}",
        headers=other_user["headers"],
        timeout=10,
    )

    assert response.status_code == 404


@allure.story("Sécurité")
@allure.severity(allure.severity_level.NORMAL)
def test_deleting_a_missing_favorite_returns_404(api, api_url, user):
    response = api.delete(
        f"{api_url}/api/favorites/999999999", headers=user["headers"], timeout=10
    )

    assert response.status_code == 404


@allure.story("Anomalies")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.xfail(
    reason="ANO-001 : l'API accepte un favori dont l'équipe n'existe pas (aucun contrôle référentiel).",
    strict=True,
)
def test_unknown_team_cannot_be_added_as_favorite(api, api_url, user):
    response = add_favorite(api, api_url, user["headers"], team_id=987654321, team_name="Ghost FC")

    assert response.status_code == 422


@allure.story("Anomalies")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.xfail(
    reason="ANO-002 : team_crest accepte un schéma d'URL arbitraire (javascript:, data:).",
    strict=True,
)
def test_crest_url_scheme_is_restricted(api, api_url, user):
    response = add_favorite(
        api, api_url, user["headers"], team_id=66, team_name="Evil", team_crest="javascript:alert(1)"
    )

    assert response.status_code == 422
