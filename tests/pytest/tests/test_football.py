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
    assert payload["items"], f"Le calendrier {code} ne doit pas être vide"
    assert payload["page"] == 1
    assert payload["page_size"] == 50
    assert payload["total"] >= len(payload["items"])
    assert payload["total_pages"] == (
        payload["total"] + payload["page_size"] - 1
    ) // payload["page_size"]


@allure.story("Pagination")
@allure.severity(allure.severity_level.NORMAL)
def test_matches_pagination_is_stable(api, api_url):
    """Deux appels identiques donnent la même page, sans recouvrement."""
    url = f"{api_url}/api/football/leagues/PL/matches?page=1&page_size=5&sort=date"
    first = get_football(api, url)
    again = get_football(api, url)

    assert first.status_code == 200
    assert again.status_code == 200
    first_ids = [match["id"] for match in first.json()["items"]]
    assert [match["id"] for match in again.json()["items"]] == first_ids
    assert len(first_ids) <= 5

    total = first.json()["total"]
    if total > 5:
        second = get_football(
            api,
            f"{api_url}/api/football/leagues/PL/matches?page=2&page_size=5&sort=date",
        )
        assert second.status_code == 200
        second_ids = [match["id"] for match in second.json()["items"]]
        assert set(first_ids).isdisjoint(second_ids)


@allure.story("Pagination")
@allure.severity(allure.severity_level.NORMAL)
def test_matches_page_beyond_last_is_empty(api, api_url):
    response = get_football(
        api, f"{api_url}/api/football/leagues/PL/matches?page=9999&page_size=100"
    )

    assert response.status_code == 200
    assert response.json()["items"] == []


@allure.story("Pagination")
@allure.severity(allure.severity_level.NORMAL)
def test_matches_can_be_filtered_by_status_and_team(api, api_url):
    finished = get_football(
        api,
        f"{api_url}/api/football/leagues/PL/matches?status=FINISHED&page_size=100",
    )

    assert finished.status_code == 200
    items = finished.json()["items"]
    assert items, "Aucun match terminé renvoyé pour la Premier League"
    assert all(match["status"] == "FINISHED" for match in items)

    team_id = items[0]["homeTeam"]["id"]
    by_team = get_football(
        api,
        f"{api_url}/api/football/leagues/PL/matches?team_id={team_id}&page_size=100",
    )

    assert by_team.status_code == 200
    assert by_team.json()["items"]
    for match in by_team.json()["items"]:
        assert team_id in (match["homeTeam"]["id"], match["awayTeam"]["id"]), match


@allure.story("Pagination")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize("sort,descending", [("date", False), ("date_desc", True)])
def test_matches_sort_is_deterministic(api, api_url, sort, descending):
    response = get_football(
        api,
        f"{api_url}/api/football/leagues/PL/matches?sort={sort}&page_size=100",
    )

    assert response.status_code == 200
    keys = [(match["utcDate"], match["id"]) for match in response.json()["items"]]
    assert keys == sorted(keys, reverse=descending)


@allure.story("Pagination")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.parametrize(
    "query",
    [
        "page=0",
        "page=abc",
        "page_size=0",
        "page_size=101",
        "sort=alpha",
        "team_id=-1",
        "status=UNKNOWN",
    ],
)
def test_matches_reject_invalid_parameters(api, api_url, query):
    response = api.get(
        f"{api_url}/api/football/leagues/PL/matches?{query}", timeout=FOOTBALL_TIMEOUT
    )

    assert response.status_code == 422


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


@allure.story("Actualités")
@allure.severity(allure.severity_level.CRITICAL)
def test_news_match_the_contract(api, api_url, schemas):
    response = get_football(api, f"{api_url}/api/football/news?days=7&limit=10")

    assert response.status_code == 200
    payload = response.json()
    validate(payload, schemas["news"])
    assert payload["window"]["days"] == 7
    assert payload["window"]["from"] <= payload["window"]["to"]
    assert len(payload["items"]) <= 10


@allure.story("Actualités")
@allure.severity(allure.severity_level.NORMAL)
def test_news_only_contains_supported_competitions(api, api_url):
    response = get_football(api, f"{api_url}/api/football/news?days=7&limit=20")

    assert response.status_code == 200
    codes = {item["competition"]["code"] for item in response.json()["items"]}
    assert codes <= {"PL", "FL1", "PD", "SA", "BL1", "CL"}, codes


@allure.story("Actualités")
@allure.severity(allure.severity_level.NORMAL)
def test_news_is_sorted_from_newest_to_oldest(api, api_url):
    response = get_football(api, f"{api_url}/api/football/news?days=7&limit=20")

    assert response.status_code == 200
    items = response.json()["items"]
    keys = [(item["utcDate"], item["id"]) for item in items]
    assert keys == sorted(keys, reverse=True)


@allure.story("Actualités")
@allure.severity(allure.severity_level.NORMAL)
def test_news_headlines_follow_the_three_branches(api, api_url):
    """Le titre est reconstruit depuis le score : aucune valeur figée."""
    response = get_football(api, f"{api_url}/api/football/news?days=7&limit=20")

    assert response.status_code == 200
    for item in response.json()["items"]:
        home = item["homeTeam"]["name"]
        away = item["awayTeam"]["name"]
        home_goals = item["score"]["home"]
        away_goals = item["score"]["away"]
        if home_goals > away_goals:
            expected = f"{home} s'impose {home_goals}-{away_goals} face à {away}"
        elif away_goals > home_goals:
            expected = (
                f"{away} s'impose {away_goals}-{home_goals} sur le terrain de {home}"
            )
        else:
            expected = f"{home} et {away} se quittent dos à dos ({home_goals}-{away_goals})"
        assert item["headline"] == expected, item


@allure.story("Actualités")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize(
    "query",
    [
        "days=0",
        "days=11",
        "days=abc",
        "limit=0",
        "limit=21",
    ],
)
def test_news_rejects_invalid_parameters(api, api_url, query):
    """``days=11`` dépasse la plage acceptée par le fournisseur (10 jours)."""
    response = api.get(f"{api_url}/api/football/news?{query}", timeout=FOOTBALL_TIMEOUT)

    assert response.status_code == 422


@allure.story("Presse")
@allure.severity(allure.severity_level.NORMAL)
def test_press_always_returns_the_contract(api, api_url, schemas):
    """Source non contractuelle : la route répond 200, disponible ou non."""
    response = api.get(f"{api_url}/api/football/press?limit=5", timeout=FOOTBALL_TIMEOUT)

    assert response.status_code == 200, response.text
    payload = response.json()
    validate(payload, schemas["press"])
    assert payload["source"]["name"] == "RMC Sport"
    assert isinstance(payload["available"], bool)
    assert len(payload["items"]) <= 5


@allure.story("Presse")
@allure.severity(allure.severity_level.NORMAL)
def test_press_items_are_clean_and_attributable(api, api_url):
    response = api.get(f"{api_url}/api/football/press?limit=10", timeout=FOOTBALL_TIMEOUT)

    assert response.status_code == 200
    payload = response.json()
    for item in payload["items"]:
        assert item["link"].startswith(("http://", "https://")), item
        assert "<" not in item["title"], item
        assert len(item["title"]) <= 140, item


@allure.story("Presse")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.parametrize("query", ["limit=0", "limit=11", "limit=abc"])
def test_press_rejects_invalid_parameters(api, api_url, query):
    response = api.get(f"{api_url}/api/football/press?{query}", timeout=FOOTBALL_TIMEOUT)

    assert response.status_code == 422


@allure.story("Match")
@allure.severity(allure.severity_level.NORMAL)
def test_match_details_match_the_contract(api, api_url, schemas):
    calendar = get_football(api, f"{api_url}/api/football/leagues/PL/matches")
    assert calendar.status_code == 200
    match = calendar.json()["items"][0]

    response = get_football(api, f"{api_url}/api/football/matches/{match['id']}")

    assert response.status_code == 200
    payload = response.json()
    validate(payload, schemas["match"])
    assert payload["id"] == match["id"]
    assert payload["homeTeam"]["name"] == match["homeTeam"]["name"]
    assert payload["awayTeam"]["name"] == match["awayTeam"]["name"]
    assert payload["competition"]["code"] == "PL"


@allure.story("Match")
@allure.severity(allure.severity_level.NORMAL)
def test_unknown_match_returns_404(api, api_url):
    """La nouvelle route traduit l'erreur fournisseur en 404 (ANO-005 reste sur /teams)."""
    response = api.get(
        f"{api_url}/api/football/matches/999999999", timeout=FOOTBALL_TIMEOUT
    )

    assert response.status_code == 404
    assert response.json()["detail"]


@allure.story("Match")
@allure.severity(allure.severity_level.MINOR)
def test_match_id_must_be_an_integer(api, api_url):
    response = api.get(f"{api_url}/api/football/matches/abc", timeout=FOOTBALL_TIMEOUT)

    assert response.status_code == 422
