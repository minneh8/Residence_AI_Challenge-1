from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_predict():
    response = client.post('/predict', json={
        'text': 'Esta é uma notícia de teste com texto suficiente para a análise do sistema DUAT.'
    })
    assert response.status_code == 200
    body = response.json()
    assert 'classification' in body
    assert 0 <= body['fake_probability'] <= 1
