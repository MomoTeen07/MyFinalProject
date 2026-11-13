"""Cas de sécurité : jetons, cloisonnement des comptes et robustesse."""

import base64
import json
import time

import allure
import pytest

pytestmark = allure.feature("Sécurité")


def _b64(value: dict) -> str:
    raw = json.dumps(value, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _unsigned_token(user_id: str = "1") -> str:
    header = _b64({"alg": "none", "typ": "JWT"})
    payload = _b64({"sub": user_id, "exp": int(time.time()) + 600})
    return f"{header}.{payload}."


@allure.story("Jetons")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.parametrize(
    "token",
    [
        "",
        "abc",
        "abc.def",
        "abc.def.ghi",
        _unsigned_token(),
    ],
)
def test_invalid_tokens_are_rejected(api, api_url, token):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = api.get(f"{api_url}/api/users/me", headers=headers, timeout=10)

    assert response.status_code == 401


@allure.story("Jetons")
@allure.severity(allure.severity_level.CRITICAL)
def test_token_payload_cannot_be_tampered(api, api_url, user):
    """Modifier le sujet d'un jeton valide doit invalider la signature."""
    header, payload, signature = user["token"].split(".")

    def decode(segment: str) -> dict:
        padding = "=" * (-len(segment) % 4)
        return json.loads(base64.urlsafe_b64decode(segment + padding))

    claims = decode(payload)
    claims["sub"] = str(int(claims["sub"]) + 1)
    forged = ".".join([header, _b64(claims), signature])

    response = api.get(
        f"{api_url}/api/users/me",
        headers={"Authorization": f"Bearer {forged}"},
        timeout=10,
    )

    assert response.status_code == 401


@allure.story("Cloisonnement")
@allure.severity(allure.severity_level.BLOCKER)
def test_a_user_cannot_read_another_users_favorites(
    api, api_url, user, other_user, favorite
):
    other_listing = api.get(
        f"{api_url}/api/favorites", headers=other_user["headers"], timeout=10
    )

    assert other_listing.status_code == 200
    assert all(item["id"] != favorite["id"] for item in other_listing.json())


@allure.story("Robustesse")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.xfail(
    reason="ANO-004 : aucune limitation du nombre de tentatives de connexion (brute force possible).",
    strict=True,
)
def test_repeated_failed_logins_are_throttled(api, api_url, user):
    statuses = []
    for _ in range(12):
        response = api.post(
            f"{api_url}/api/auth/login",
            json={"email": user["email"], "password": "MauvaisMotDePasse1!"},
            timeout=10,
        )
        statuses.append(response.status_code)
        if response.status_code == 429:
            break

    assert 429 in statuses
