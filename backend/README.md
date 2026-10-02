# DUAT Backend + Frontend

A API está integrada ao frontend visual existente sem alteração de design. O HTML, CSS e a imagem da identidade visual são preservados; apenas o JavaScript realiza as chamadas à API.

## Rodar localmente

Na raiz do repositório:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\\Scripts\\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r backend/requirements.txt
```

Terminal 1 — backend:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 — frontend:

```bash
python -m http.server 5500 --directory frontend
```

Abra `http://localhost:5500`.

## Pipelines

Coloque os artefatos treinados em `backend/app/models/`:

```text
svm.joblib
kmeans.joblib
dbscan.joblib
isolation_forest.joblib
```

Reinicie a API e verifique `http://localhost:8000/pipelines`.

## Contratos

SVM e K-Means usam `POST /predict`:

```json
{"text":"Texto da notícia", "pipeline":"svm"}
```

DBSCAN e Isolation Forest usam `POST /anomaly`:

```json
{"text":"Texto da notícia", "pipeline":"isolation_forest"}
```

O frontend mantém o design original e consome esses endpoints pelo JavaScript.