from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
TEXT = 'Esta é uma notícia de teste com texto suficiente para a análise do sistema DUAT.'


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert 'pipelines' in response.json()


def test_pipeline_status():
    response = client.get('/pipelines')
    assert response.status_code == 200
    assert set(response.json()['supported']) == {'svm', 'kmeans', 'dbscan', 'isolation_forest'}


def test_predict_without_artifact():
    response = client.post('/predict', json={'text': TEXT, 'pipeline': 'svm'})
    assert response.status_code == 200
    assert response.json()['pipeline'] == 'svm'


def test_anomaly_without_artifact():
    response = client.post('/anomaly', json={'text': TEXT, 'pipeline': 'isolation_forest'})
    assert response.status_code == 200
    assert response.json()['pipeline'] == 'isolation_forest'
