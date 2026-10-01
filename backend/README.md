# DUAT Backend + Frontend

A aplicação possui uma API FastAPI e um frontend estático em HTML/CSS/JavaScript.

## Rodar localmente

Na raiz do repositório:

```bash
python -m venv .venv
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
# Linux/macOS
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Em outro terminal, sirva o frontend:

```bash
python -m http.server 5500 --directory frontend
```

Abra `http://localhost:5500`. A API fica em `http://localhost:8000/docs`.

## Pipelines

Coloque os artefatos treinados em `backend/app/models/`:

```text
svm.joblib
kmeans.joblib
dbscan.joblib
isolation_forest.joblib
```

Reinicie a API depois de colocar ou substituir os arquivos. Consulte o status em `http://localhost:8000/pipelines`.

## Contrato usado pelo frontend

Classificação com SVM ou K-Means:

```http
POST /predict
Content-Type: application/json
```

```json
{"text":"Texto da notícia", "pipeline":"svm"}
```

Detecção com DBSCAN ou Isolation Forest:

```http
POST /anomaly
Content-Type: application/json
```

```json
{"text":"Texto da notícia", "pipeline":"isolation_forest"}
```

## CORS

Por padrão, o backend permite o frontend local. Para restringir origens:

```bash
DUAT_CORS_ORIGINS=http://localhost:5500 uvicorn backend.app.main:app --reload --port 8000
```

Sem artefatos treinados, a interface informa que está em modo de desenvolvimento. Não use o fallback como resultado científico.
