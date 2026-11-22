"""Contrats de l'API football : schémas JSON et codes de statut.

La suite s'exécute contre l'application réellement démarrée, alimentée par le
fournisseur de données (ou par le mode simulé si ``MOCK_FOOTBALL_API=true``).
Les assertions de ce fichier portent donc sur des invariants — schéma, ordre,
cohérence, bornes — et non sur des valeurs figées : le nombre d'équipes et les
noms évoluent avec la saison.
"""

import os
import time

import allure
import pytest
from jsonschema import validate

pytestmark = allure.feature("API football")

# Positions le mode réel : certaines attentes de contrat diffèrent de ce que
# produit le jeu de données simulé (voir ANO-005).
REAL_DATA = os.getenv("REAL_FOOTBALL_DATA", "").strip().lower() in {"1", "true", "yes"}
FOOTBALL_TIMEOUT = 30
# Le fournisseur public peut renvoyer un 5xx transitoire : on retente un nombre
# borné de fois avant de conclure à une anomalie.
TRANSIENT_STATUSES = {502, 503, 504}
RETRY_ATTEMPTS = 3


def _retry_delay(response, attempt: int) -> int:
    """Respecte ``Retry-After`` quand le fournisseur limite le débit."""
    retry_after = response.headers.get("Retry-After")
    if retry_after and retry_after.isdigit():
        return min(int(retry_after), 60)
    return 2 * attempt


def get_football(api, url: str):
    """GET sur les données football avec reprise bornée sur erreur transitoire."""
    response = api.get(url, timeout=FOOTBALL_TIMEOUT)
    for attempt in range(1, RETRY_ATTEMPTS):
        if response.status_code not in TRANSIENT_STATUSES:
            break
        time.sleep(_retry_delay(response, attempt))
        response = api.get(url, timeout=FOOTBALL_TIMEOUT)
    return response


@allure.story("Championnats")
@allure.severity(allure.severity_level.CRITICAL)
def test_leagues_match_the_contract(api, api_url, schemas):
    response = get_football(api, f"{api_url}/api/football/leagues")

    assert response.status_code == 200
    payload = response.json()
    validate(payload, schemas["leagues"])
    assert {league["code"] for league in payload} == {"PL", "FL1", "PD", "SA", "BL1", "CL"}


@allure.story("Classement")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("code", ["PL", "FL1", "PD", "SA", "BL1", "CL"])
def test_standings_match_the_contract(api, api_url, schemas, code):
    response = get_football(api, f"{api_url}/api/football/leagues/{code}/standings")

    assert response.status_code == 200
    payload = response.json()
    validate(payload, schemas["standings"])
    assert payload, f"Le classement {code} ne doit pas être vide"
    assert [row["position"] for row in payload] == sorted(
        row["position"] for row in payload
    )
    assert payload[0]["position"] == 1


@allure.story("Calendrier")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize("code", ["PL", "FL1"])
def test_matches_match_the_contract(api, api_url, schemas, code):
    response = get_football(api, f"{api_url}/api/football/leagues/{code}/matches")

    assert response.status_code == 200
    payload = response.json()
    validate(payload, schemas["matches"])
    assert payload, f"Le calendrier {code} ne doit pas être vide"


@allure.story("Équipe")
@allure.severity(allure.severity_level.NORMAL)
def test_team_details_match_the_contract(api, api_url, schemas):
    response = get_football(api, f"{api_url}/api/football/leagues/PL/teams/57")

    assert response.status_code == 200
    payload = response.json()
    validate(payload, schemas["team"])
    # L'identifiant est stable ; le libellé dépend du fournisseur
    # (« Arsenal » en simulé, « Arsenal FC » en réel).
    assert payload["id"] == 57
    assert "Arsenal" in payload["name"]


@allure.story("Erreurs")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize(
    "path",
    [
        "/api/football/leagues/XX/standings",
        "/api/football/leagues/ZZ/matches",
    ],
)
def test_unknown_championship_returns_404(api, api_url, path):
    response = api.get(f"{api_url}{path}", timeout=FOOTBALL_TIMEOUT)

    assert response.status_code == 404
    assert response.json()["detail"]


@allure.story("Erreurs")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.xfail(
    condition=REAL_DATA,
    strict=True,
    reason=(
        "ANO-005 : en mode réel, un identifiant d'équipe inconnu renvoyé par le "
        "fournisseur (HTTP 400) est traduit en 502 par l'API au lieu de 404."
    ),
)
def test_unknown_team_returns_404(api, api_url):
    response = api.get(
        f"{api_url}/api/football/leagues/PL/teams/999999", timeout=FOOTBALL_TIMEOUT
    )

    assert response.status_code == 404
    assert response.json()["detail"]


@allure.story("Erreurs")
@allure.severity(allure.severity_level.MINOR)
def test_team_id_must_be_an_integer(api, api_url):
    response = api.get(f"{api_url}/api/football/leagues/PL/teams/abc", timeout=FOOTBALL_TIMEOUT)

    assert response.status_code == 422


def _assert_ranking(items: list[dict], metric: str) -> None:
    """Vérifie l'ordre imposé par la spécification V2, sans valeur figée."""
    keys = [
        (
            -item[metric],
            -item["goals"],
            item["playedMatches"],
            item["player"]["name"].casefold(),
        )
        for item in items
    ]
    assert keys == sorted(keys), f"classement par {metric} non déterministe"


@allure.story("Buteurs")
@allure.severity(allure.severity_level.CRITICAL)
def test_scorers_match_the_contract(api, api_url, schemas):
    response = get_football(api, f"{api_url}/api/football/leagues/PL/scorers?limit=10")

    assert response.status_code == 200
    payload = response.json()
    validate(payload, schemas["scorers"])
    assert payload["competition"]["code"] == "PL"
    assert payload["sort"] == "goals"
    assert payload["items"], "Le classement des buteurs ne doit pas être vide"
    assert len(payload["items"]) <= 10


@allure.story("Buteurs")
@allure.severity(allure.severity_level.CRITICAL)
def test_scorers_ranking_is_deterministic(api, api_url):
    response = get_football(api, f"{api_url}/api/football/leagues/PL/scorers?limit=10")

    assert response.status_code == 200
    items = response.json()["items"]
    _assert_ranking(items, "goals")
    assert [item["position"] for item in items] == list(range(1, len(items) + 1))


@allure.story("Buteurs")
@allure.severity(allure.severity_level.NORMAL)
def test_scorers_assists_are_never_null(api, api_url):
    """Le fournisseur renvoie ``null`` quand la passe est inconnue (cf. spec V2)."""
    response = get_football(api, f"{api_url}/api/football/leagues/PL/scorers?limit=20")

    assert response.status_code == 200
    for item in response.json()["items"]:
        assert isinstance(item["assists"], int), item
        assert item["assists"] >= 0


@allure.story("Buteurs")
@allure.severity(allure.severity_level.NORMAL)
def test_scorers_can_be_sorted_by_assists(api, api_url):
    response = get_football(
        api, f"{api_url}/api/football/leagues/PL/scorers?limit=10&sort=assists"
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["sort"] == "assists"
    _assert_ranking(payload["items"], "assists")


@allure.story("Buteurs")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize(
    "query",
    [
        "limit=0",
        "limit=51",
        "limit=abc",
        "sort=penalties",
    ],
)
def test_scorers_reject_invalid_parameters(api, api_url, query):
    response = api.get(
        f"{api_url}/api/football/leagues/PL/scorers?{query}", timeout=FOOTBALL_TIMEOUT
    )

    assert response.status_code == 422


@allure.story("Buteurs")
@allure.severity(allure.severity_level.NORMAL)
def test_scorers_unknown_championship_returns_404(api, api_url):
    response = api.get(
        f"{api_url}/api/football/leagues/XX/scorers", timeout=FOOTBALL_TIMEOUT
    )

    assert response.status_code == 404
