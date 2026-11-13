"""Fixtures partagées de la suite API.

Les tests s'exécutent contre l'application réellement démarrée (Docker
Compose), pas contre un mock : c'est ce qui permet de détecter les anomalies
de bout en bout. L'URL de base se règle avec ``API_URL``.
"""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

import pytest
import requests

DEFAULT_API_URL = "http://localhost:8001"
DEFAULT_PASSWORD = "Password123!"
SCHEMAS_DIR = Path(__file__).resolve().parent / "schemas"
DATA_DIR = Path(__file__).resolve().parent / "data"


@pytest.fixture(scope="session")
def schemas() -> dict[str, dict]:
    """Schémas JSON de contrat, indexés par nom de fichier sans extension."""
    return {
        path.stem.removesuffix("_schema"): json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(SCHEMAS_DIR.glob("*.json"))
    }


@pytest.fixture(scope="session")
def dataset() -> dict[str, list[dict]]:
    """Jeux de données négatifs, indexés par nom de fichier sans extension."""
    return {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(DATA_DIR.glob("*.json"))
    }


@pytest.fixture(scope="session")
def api_url() -> str:
    return os.getenv("API_URL", DEFAULT_API_URL).rstrip("/")


@pytest.fixture()
def api() -> requests.Session:
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    return session


def register(session: requests.Session, api_url: str) -> dict:
    """Crée un compte unique et renvoie ses identifiants et son jeton."""
    email = f"qa.{uuid.uuid4().hex[:12]}@example.com"
    response = session.post(
        f"{api_url}/api/auth/register",
        json={"email": email, "password": DEFAULT_PASSWORD, "name": "QA Automation"},
        timeout=10,
    )
    assert response.status_code == 201, response.text
    payload = response.json()
    return {
        "email": email,
        "password": DEFAULT_PASSWORD,
        "token": payload["access_token"],
        "headers": {"Authorization": f"Bearer {payload['access_token']}"},
    }


@pytest.fixture()
def user(api: requests.Session, api_url: str) -> dict:
    return register(api, api_url)


@pytest.fixture()
def other_user(api: requests.Session, api_url: str) -> dict:
    return register(api, api_url)


@pytest.fixture()
def favorite(api: requests.Session, api_url: str, user: dict) -> dict:
    """Favori Arsenal (Premier League) créé pour l'utilisateur courant."""
    payload = {
        "team_id": 57,
        "league_code": "PL",
        "team_name": "Arsenal",
        "team_crest": "",
    }
    response = api.post(
        f"{api_url}/api/favorites", json=payload, headers=user["headers"], timeout=10
    )
    assert response.status_code == 201, response.text
    return response.json()
