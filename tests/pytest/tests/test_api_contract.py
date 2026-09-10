import os, requests
from jsonschema import validate
BASE=os.getenv("API_URL","http://localhost:8000")

def test_health():
    r=requests.get(f"{BASE}/health",timeout=5); assert r.status_code==200; assert r.json()["status"]=="ok"

def test_leagues_schema():
    r=requests.get(f"{BASE}/api/football/leagues",timeout=5); assert r.status_code==200
    schema={"type":"array","items":{"type":"object","required":["code","name","country"],"properties":{"code":{"type":"string"},"name":{"type":"string"},"country":{"type":"string"}}}}
    validate(r.json(),schema)
