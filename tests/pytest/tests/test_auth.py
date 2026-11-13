"""Authentification : inscription, connexion, session et validation."""

import allure
import pytest
from conftest import DEFAULT_PASSWORD
from jsonschema import validate

pytestmark = allure.feature("Authentification")


@allure.story("Inscription")
@allure.severity(allure.severity_level.BLOCKER)
def test_registration_returns_a_usable_token(api, api_url, schemas, user):
    validate({"access_token": user["token"], "token_type": "bearer"}, schemas["token"])

    session = api.get(f"{api_url}/api/users/me", headers=user["headers"], timeout=10)

    assert session.status_code == 200
    assert session.json()["email"] == user["email"]


@allure.story("Inscription")
@allure.severity(allure.severity_level.NORMAL)
def test_registration_normalizes_the_email(api, api_url):
    import uuid

    email = f"qa.MixedCase.{uuid.uuid4().hex[:8]}@Example.COM"
    response = api.post(
        f"{api_url}/api/auth/register",
        json={"email": email, "password": DEFAULT_PASSWORD, "name": "Mixed Case"},
        timeout=10,
    )

    assert response.status_code == 201
    login = api.post(
        f"{api_url}/api/auth/login",
        json={"email": email.strip().lower(), "password": DEFAULT_PASSWORD},
        timeout=10,
    )
    assert login.status_code == 200


@allure.story("Inscription")
@allure.severity(allure.severity_level.CRITICAL)
def test_duplicate_email_is_rejected_case_insensitively(api, api_url, user):
    response = api.post(
        f"{api_url}/api/auth/register",
        json={
            "email": user["email"].upper(),
            "password": DEFAULT_PASSWORD,
            "name": "Doublon",
        },
        timeout=10,
    )

    assert response.status_code == 409


@allure.story("Inscription")
@allure.severity(allure.severity_level.NORMAL)
def test_registration_never_returns_the_password(api, api_url):
    import uuid

    email = f"qa.secret.{uuid.uuid4().hex[:8]}@example.com"
    response = api.post(
        f"{api_url}/api/auth/register",
        json={"email": email, "password": DEFAULT_PASSWORD, "name": "Secret Check"},
        timeout=10,
    )

    body = response.text.lower()
    assert response.status_code == 201
    assert DEFAULT_PASSWORD.lower() not in body
    assert "password" not in response.json()


@allure.story("Connexion")
@allure.severity(allure.severity_level.BLOCKER)
def test_login_returns_a_valid_session(api, api_url, user, schemas):
    response = api.post(
        f"{api_url}/api/auth/login",
        json={"email": user["email"], "password": user["password"]},
        timeout=10,
    )

    assert response.status_code == 200
    validate(response.json(), schemas["token"])

    me = api.get(
        f"{api_url}/api/users/me",
        headers={"Authorization": f"Bearer {response.json()['access_token']}"},
        timeout=10,
    )
    assert me.status_code == 200


@allure.story("Connexion")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize(
    "email, password",
    [
        ("utilisateur-inconnu@example.com", DEFAULT_PASSWORD),
        ("utilisateur-inconnu@example.com", "MauvaisMotDePasse1!"),
    ],
)
def test_unknown_account_and_wrong_password_are_indistinguishable(
    api, api_url, email, password
):
    response = api.post(
        f"{api_url}/api/auth/login",
        json={"email": email, "password": password},
        timeout=10,
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Adresse e-mail ou mot de passe incorrect."


@allure.story("Validation")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize(
    "case",
    [
        "email-invalide",
        "email-vide",
        "mot-de-passe-court",
        "mot-de-passe-absent",
        "nom-d-un-caractere",
        "nom-uniquement-des-espaces",
        "nom-de-plus-de-100-caracteres",
    ],
)
def test_invalid_registrations_are_rejected(api, api_url, dataset, case):
    entry = next(item for item in dataset["invalid_registrations"] if item["id"] == case)

    response = api.post(
        f"{api_url}/api/auth/register", json=entry["payload"], timeout=10
    )

    assert response.status_code == 422, response.text
    fields = {error["loc"][-1] for error in response.json()["detail"]}
    assert entry["champ"] in fields


@allure.story("Session")
@allure.severity(allure.severity_level.CRITICAL)
def test_profile_requires_a_token(api, api_url):
    response = api.get(f"{api_url}/api/users/me", timeout=10)

    assert response.status_code == 401
