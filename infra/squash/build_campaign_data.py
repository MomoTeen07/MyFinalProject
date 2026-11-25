"""Génère `campaign_data.json` à partir des documents QA.

Sources (relatives à la racine du dépôt) :
    docs/TEST_CASES.md     -> cas de test, techniques, étapes, attendus, statuts
    docs/TRACEABILITY.md   -> exigences et rattachement cas <-> exigences

Utilisation :
    python infra/squash/build_campaign_data.py

Le fichier produit est consommé par `infra/squash/seed_campaign.py`. À relancer
après toute modification des cas, des exigences ou de la traçabilité.
"""

from __future__ import annotations

import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CASES_FILE = ROOT / "docs" / "TEST_CASES.md"
TRACE_FILE = ROOT / "docs" / "TRACEABILITY.md"
OUTPUT_FILE = ROOT / "infra" / "squash" / "campaign_data.json"

TC_PATTERN = re.compile(r"TC-[A-Z0-9]+-\d+")
FOLDER_BY_PREFIX = {
    "AUTH": "Authentification",
    "FOOT": "Football",
    "FAV": "Favoris",
    "SEC": "Sécurité et robustesse",
    # V2 : buteurs, actualités, presse et détail de match.
    "SCOR": "Football",
    "NEWS": "Football",
    "PRESS": "Football",
    "MATCH": "Football",
    # V3 : parcours enrichis (prochains matchs, fiche équipe, favoris, match).
    "V3": "V3 — parcours enrichis",
}
CRITICAL_REQUIREMENTS = {"R-14", "R-15"}
MAJOR_NON_FUNCTIONAL = {"R-16"}
HIGH_IMPORTANCE_CASES = {
    "TC-AUTH-01",
    "TC-AUTH-09",
    "TC-AUTH-11",
    "TC-FAV-01",
    "TC-FAV-04",
    "TC-FAV-06",
    "TC-FAV-07",
    "TC-V3-01",
    "TC-V3-03",
    "TC-V3-05",
    "TC-V3-07",
}
PREREQUISITE = (
    "Application démarrée (docker compose up --build --detach --wait), "
    "données réelles ou simulées selon le mode de la campagne, compte de test "
    "créé si nécessaire."
)


def cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def read_test_cases() -> list[dict]:
    cases = []
    for line in CASES_FILE.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| TC-"):
            continue
        parts = cells(line)
        if len(parts) < 7:
            continue
        tc_id, title, technique, steps, expected, obtained, status = parts[:7]
        clean_status = re.sub(r"[*`]", "", status)
        prefix = tc_id.split("-")[1]
        cases.append(
            {
                "id": tc_id,
                "name": f"{tc_id} — {title}",
                "reference": tc_id,
                "folder": FOLDER_BY_PREFIX[prefix],
                "technique": technique,
                "steps": [{"action": steps, "expected": expected}],
                "obtained": obtained,
                "status": "SUCCESS" if clean_status.lower().startswith("pass") else "FAILURE",
                "anomalies": sorted(set(re.findall(r"ANO-\d{3}", clean_status))),
                "importance": (
                    "VERY_HIGH"
                    if prefix == "SEC" or tc_id in HIGH_IMPORTANCE_CASES
                    else "HIGH"
                ),
                "prerequisite": PREREQUISITE,
            }
        )
    if not cases:
        raise SystemExit(f"Aucun cas de test reconnu dans {CASES_FILE}")
    return cases


def read_requirements() -> tuple[list[dict], dict[str, list[str]]]:
    requirements = []
    case_to_requirements: dict[str, list[str]] = {}
    for line in TRACE_FILE.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| R-"):
            continue
        parts = cells(line)
        if len(parts) < 3:
            continue
        requirement_id, requirement_name, manual_cases = parts[:3]
        if requirement_id in CRITICAL_REQUIREMENTS:
            criticality, category = "CRITICAL", "CAT_NON_FUNCTIONAL"
        elif requirement_id in MAJOR_NON_FUNCTIONAL:
            criticality, category = "MAJOR", "CAT_NON_FUNCTIONAL"
        else:
            criticality, category = "MAJOR", "CAT_FUNCTIONAL"
        requirements.append(
            {
                "id": requirement_id,
                "name": f"{requirement_id} — {requirement_name}",
                "description": f"<p>{html.escape(requirement_name)}</p>",
                "criticality": criticality,
                "category": category,
                "status": "APPROVED",
            }
        )
        for tc_id in TC_PATTERN.findall(manual_cases):
            case_to_requirements.setdefault(tc_id, []).append(requirement_id)
    if not requirements:
        raise SystemExit(f"Aucune exigence reconnue dans {TRACE_FILE}")
    return requirements, case_to_requirements


def main() -> int:
    test_cases = read_test_cases()
    requirements, case_to_requirements = read_requirements()

    for case in test_cases:
        case["requirement_ids"] = case_to_requirements.get(case["id"], [])
        case["description"] = (
            f"<p><strong>Technique :</strong> {html.escape(case['technique'])}</p>"
            f"<p><strong>Résultat obtenu :</strong> {html.escape(case['obtained'])}</p>"
            f"<p><strong>Exigences :</strong> "
            f"{', '.join(case['requirement_ids']) or 'non tracée'}</p>"
        )

    untraced = [case["id"] for case in test_cases if not case["requirement_ids"]]
    if untraced:
        print(f"Cas sans exigence : {', '.join(untraced)}", file=sys.stderr)

    success = sum(1 for case in test_cases if case["status"] == "SUCCESS")
    failure = len(test_cases) - success

    payload = {
        "project": {
            "name": "Football QA",
            "label": "Projet final QA — BStorm 2026",
            "description": (
                "<p>Campagne finale de test de l'application Football QA : plan "
                f"de test, {len(test_cases)} cas manuels, traçabilité exigence → "
                "cas → exécution → anomalie.</p>"
            ),
        },
        "campaign": {
            "name": "Campagne finale V3 — Football QA",
            "reference": "CAMP-V3",
            "status": "PLANNED",
            "description": (
                "<p>Campagne finale du 25/11/2026 sur la V3 (commit 3ba1ec9, tag "
                f"v3.0). {len(requirements)} exigences, {len(test_cases)} cas : "
                f"{success} conformes, {failure} en anomalie (ANO-001 à ANO-005). "
                "Les campagnes V1 (36 cas) et V2 (14 cas) sont intégrées à ce "
                "périmètre final.</p>"
            ),
        },
        "iteration": {
            "name": "Itération 1 — campagne finale V3",
            "reference": "IT-V3",
            "status": "PLANNED",
            "description": f"<p>Exécution des {len(test_cases)} cas de la campagne finale V3.</p>",
        },
        "execution_date": "25/11/2026",
        "test_suite_name": f"Suite complète — {len(test_cases)} cas",
        "requirements": requirements,
        "test_cases": test_cases,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"{len(requirements)} exigences, {len(test_cases)} cas "
        f"({success} SUCCESS, {failure} FAILURE) -> {OUTPUT_FILE.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
