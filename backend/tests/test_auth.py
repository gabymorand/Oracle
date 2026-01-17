def test_validate_code_success(client):
    response = client.post("/api/v1/auth/validate-code", json={"code": "oracle2026", "role": "coach"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "coach"


def test_validate_code_invalid(client):
    response = client.post("/api/v1/auth/validate-code", json={"code": "wrong", "role": "coach"})
    assert response.status_code == 401


def test_validate_code_invalid_role(client):
    response = client.post("/api/v1/auth/validate-code", json={"code": "oracle2026", "role": "invalid"})
    assert response.status_code == 400
