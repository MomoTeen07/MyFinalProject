"""Crée la campagne Squash TM du projet final QA à partir de campaign_data.json.

Prérequis :
    docker compose -f infra/squash/docker-compose.yml up -d
    # attendre que http://localhost:8090/squash réponde (1 à 3 minutes)

Utilisation :
    python infra/squash/seed_campaign.py
    SQUASH_URL=http://localhost:8090 python infra/squash/seed_campaign.py

Le script est idempotent dans la limite de l'API : si un projet nommé
« Football QA » existe déjà, il s'arrête sans rien modifier. Pour repartir de
zéro :
    docker compose -f infra/squash/docker-compose.yml down --volumes
    docker compose -f infra/squash/docker-compose.yml up -d

Aucune dépendance externe : uniquement la bibliothèque standard Python 3.12.
"""

from __future__ import annotations

import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "campaign_data.json"
BASE_URL = os.getenv("SQUASH_URL", "http://localhost:8090").rstrip("/")
API = f"{BASE_URL}/squash/api/rest/latest"
USER = os.getenv("SQUASH_USER", "admin")
PASSWORD = os.getenv("SQUASH_PASSWORD", "admin")
AUTH = "Basic " + base64.b64encode(f"{USER}:{PASSWORD}".encode()).decode()


def call(method: str, path: str, body: dict | None = None) -> tuple[int, dict | str]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(API + path, data=data, method=method)
    request.add_header("Authorization", AUTH)
    request.add_header("Accept", "application/json")
    if data is not None:
        request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8")
            return response.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", errors="replace")[:600]
    except urllib.error.URLError as error:
        raise SystemExit(f"Squash TM injoignable sur {BASE_URL} : {error.reason}") from error


def expect(method: str, path: str, body: dict | None = None) -> dict:
    status, payload = call(method, path, body)
    if status >= 400 or not isinstance(payload, dict):
        raise SystemExit(f"Échec {method} {path} -> HTTP {status}\n{payload}")
    return payload


def main() -> int:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    execution_date = data.get("execution_date", "25/11/2026")

    status, listing = call("GET", "/projects?size=100")
    if status >= 400:
        raise SystemExit(
            f"API inaccessible (HTTP {status}). Vérifier que Squash TM est démarré "
            f"et que l'authentification Basic est autorisée.\n{listing}"
        )
    projects = (listing.get("_embedded", {}) or {}).get("projects", [])
    if any(project.get("name") == data["project"]["name"] for project in projects):
        raise SystemExit(
            "Le projet existe déjà. Pour le recréer : "
            "docker compose -f infra/squash/docker-compose.yml down --volumes puis up -d."
        )

    project = expect("POST", "/projects", {"_type": "project", **data["project"]})
    project_id = project["id"]
    print(f"Projet « {project['name']} » créé (id {project_id})")

    folders: dict[str, int] = {}
    for name in dict.fromkeys(case["folder"] for case in data["test_cases"]):
        folder = expect(
            "POST",
            "/test-case-folders",
            {"_type": "test-case-folder", "name": name, "parent": {"_type": "project", "id": project_id}},
        )
        folders[name] = folder["id"]
    print(f"{len(folders)} dossiers de cas de test créés")

    requirements: dict[str, int] = {}
    for requirement in data["requirements"]:
        created = expect(
            "POST",
            "/requirements",
            {
                "_type": "requirement",
                "current_version": {
                    "_type": "requirement-version",
                    "name": requirement["name"],
                    "criticality": requirement["criticality"],
                    "status": requirement["status"],
                    "description": requirement["description"],
                },
                "parent": {"_type": "project", "id": project_id},
            },
        )
        requirements[requirement["id"]] = created["current_version"]["id"]
    print(f"{len(requirements)} exigences créées")

    test_cases: list[dict] = []
    for case in data["test_cases"]:
        created = expect(
            "POST",
            "/test-cases",
            {
                "_type": "test-case",
                "name": case["name"],
                "reference": case["reference"],
                "parent": {"_type": "test-case-folder", "id": folders[case["folder"]]},
                "importance": case["importance"],
                "status": "APPROVED",
                "prerequisite": case["prerequisite"],
                "description": case["description"],
                "steps": [
                    {
                        "_type": "action-step",
                        "action": f"<p>{step['action']}</p>",
                        "expected_result": f"<p>{step['expected']}</p>",
                    }
                    for step in case["steps"]
                ],
            },
        )
        version_ids = [requirements[req] for req in case["requirement_ids"] if req in requirements]
        if version_ids:
            expect(
                "POST",
                f"/test-cases/{created['id']}/coverages/" + ",".join(str(v) for v in version_ids),
            )
        test_cases.append({**case, "squash_id": created["id"]})
    print(f"{len(test_cases)} cas de test créés et rattachés aux exigences")

    campaign = expect(
        "POST",
        "/campaigns",
        {
            "_type": "campaign",
            **data["campaign"],
            "parent": {"_type": "project", "id": project_id},
        },
    )
    print(f"Campagne « {campaign['name']} » créée (id {campaign['id']})")

    iteration = expect(
        "POST",
        f"/campaigns/{campaign['id']}/iterations",
        {
            "_type": "iteration",
            **data["iteration"],
            "parent": {"_type": "campaign", "id": campaign["id"]},
        },
    )
    print(f"Itération « {iteration['name']} » créée (id {iteration['id']})")

    plan_items: list[int] = []
    for case in test_cases:
        item = expect(
            "POST",
            f"/iterations/{iteration['id']}/test-plan",
            {"_type": "test-plan-item", "test_case": {"_type": "test-case", "id": case["squash_id"]}},
        )
        plan_items.append(item["id"])

    suite = expect(
        "POST",
        "/test-suites",
        {
            "_type": "test-suite",
            "name": data["test_suite_name"],
            "description": (
                f"<p>{data['iteration']['name']} : "
                f"{len(plan_items)} cas manuels.</p>"
            ),
            "parent": {"_type": "iteration", "id": iteration["id"]},
            "test_plan": [{"_type": "test-plan-item", "id": item_id} for item_id in plan_items],
        },
    )
    print(f"Suite « {suite['name']} » créée (id {suite['id']}, {len(plan_items)} cas)")

    success = failure = 0
    for case, item_id in zip(test_cases, plan_items):
        execution = expect("POST", f"/test-plan-items/{item_id}/executions")
        step_status = "Success" if case["status"] == "SUCCESS" else "Failure"
        for step in execution.get("execution_steps", []):
            call("PATCH", f"/execution-steps/{step['id']}/execution-status/{step_status}")

        if case["status"] == "SUCCESS":
            comment = f"Exécuté le {execution_date} — conforme : {case['obtained']}"
            success += 1
        else:
            anomalies = ", ".join(case["anomalies"]) or "anomalie documentée"
            comment = (
                f"Exécuté le {execution_date} — non conforme : {case['obtained']} "
                f"({anomalies}, voir docs/ANOMALIES.md)"
            )
            failure += 1
        expect(
            "PATCH",
            f"/executions/{execution['id']}?fields=execution_status,comment",
            {"execution_status": case["status"], "comment": comment},
        )

    print(f"{success} exécutions réussies, {failure} exécutions en échec")
    print("")
    print("Campagne disponible :")
    print(f"  {BASE_URL}/squash/project/{project_id}/campaign-workspace")
    print(f"  Projet {project_id} | Campagne {campaign['id']} | Itération {iteration['id']} | Suite {suite['id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
