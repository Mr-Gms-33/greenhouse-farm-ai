# -*- coding: utf-8 -*-
import json
import urllib.error
import urllib.request

checks = []

def get(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        body = r.read().decode()
        return r.status, body

def post_json(url, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.status, json.loads(r.read().decode())

# health
for name, url in [
    ("api_health", "http://localhost:8000/health"),
    ("web", "http://localhost:3000/"),
    ("api_docs", "http://localhost:8000/docs"),
    ("responder", "http://localhost:8089/health"),
]:
    try:
        status, body = get(url)
        ok = status == 200
        if name == "web":
            ok = ok and "الفلاحة برو" in body and "manager@farm.ma" in body and "btn-demo-staff" not in body
        checks.append((name, ok, status))
    except Exception as e:
        checks.append((name, False, str(e)))

# API farm manager login
try:
    status, body = post_json(
        "http://localhost:8000/api/v1/auth/login",
        {"email": "manager@farm.ma", "password": "Manager123!"},
    )
    token = body.get("access_token")
    ok = status == 200 and bool(token)
    checks.append(("api_manager_login", ok, status))
    if token:
        req = urllib.request.Request(
            "http://localhost:8000/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            me = json.loads(r.read().decode())
        checks.append(
            (
                "api_manager_me",
                me.get("email") == "manager@farm.ma" and me.get("role") == "manager",
                me,
            )
        )
except Exception as e:
    checks.append(("api_manager_login", False, str(e)))

# Reject staff login on frontend credentials (API has no amine user)
try:
    post_json(
        "http://localhost:8000/api/v1/auth/login",
        {"email": "amine@filaha.ma", "password": "1234"},
    )
    checks.append(("api_staff_rejected", False, "unexpected success"))
except urllib.error.HTTPError as e:
    checks.append(("api_staff_rejected", e.code in (401, 404, 422), e.code))
except Exception as e:
    checks.append(("api_staff_rejected", False, str(e)))

print("SMOKE RESULTS")
all_ok = True
for row in checks:
    name, ok, detail = row
    all_ok = all_ok and bool(ok)
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail if not isinstance(detail, dict) else detail.get('email')}")
raise SystemExit(0 if all_ok else 1)
