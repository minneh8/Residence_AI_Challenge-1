from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_validation_requires_text():
    response = client.post("/api/v1/analyze", json={"user_evaluation": "n"})
    assert response.status_code == 422


def test_invalid_evaluation():
    response = client.post("/api/v1/analyze", json={"text": "noticia", "user_evaluation": "x"})
    assert response.status_code == 422


def test_legacy_features_validation():
    response = client.post("/features", json={"user_evaluation": "n"})
    assert response.status_code == 422
