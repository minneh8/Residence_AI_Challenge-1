# DUAT Backend + Frontend

O backend reconhece os artefatos reais:

```text
backend/app/models/svm.joblib
backend/app/models/pipeline_kmeans_duat.joblib
backend/app/models/duat_dbscan_isolation_forest.joblib
```

O terceiro artefato é combinado: DBSCAN e Isolation Forest são executados juntos na mesma requisição. O objeto salvo deve expor os componentes como `dbscan` e `isolation_forest` — ou como chaves equivalentes reconhecidas pelo backend.

## Executar

```bash
python -m venv .venv
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
# Linux/macOS
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
python -m http.server 5500 --directory frontend
```

Abra `http://localhost:5500`.

## Status

`GET /pipelines` mostra os nomes reais carregados. Aliases aceitos:

- `kmeans` → `pipeline_kmeans_duat`.
- `dbscan` → `duat_dbscan_isolation_forest`.
- `isolation_forest` → `duat_dbscan_isolation_forest`.

Para executar os dois modelos juntos:

```json
{"text":"Texto da notícia", "pipeline":"duat_dbscan_isolation_forest"}
```

Use `POST /anomaly` ou `POST /predict`. A resposta contém `details.dbscan` e `details.isolation_forest`.