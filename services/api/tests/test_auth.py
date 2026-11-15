from sqlalchemy import select

from app.models import User


def test_auth_login_me_logout(client):
    login = client.post("/api/v1/auth/login", json={"email": "owner@farm.ma", "password": "Owner123!"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "owner@farm.ma"
    logout = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout.status_code == 200


def test_auth_invalid_credentials(client):
    bad = client.post("/api/v1/auth/login", json={"email": "owner@farm.ma", "password": "wrong"})
    assert bad.status_code == 401
    assert bad.json()["detail"] == "Invalid credentials"


def test_deactivated_user_blocked(client, db):
    manager = db.scalar(select(User).where(User.email == "manager@farm.ma"))
    manager.active = False
    db.commit()
    blocked = client.post("/api/v1/auth/login", json={"email": "manager@farm.ma", "password": "Manager123!"})
    assert blocked.status_code == 403
