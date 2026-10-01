# DUAT Backend

API FastAPI preparada para integração com o frontend HTML/CSS/JavaScript e para receber os pipelines SVM, K-Means, DBSCAN e Isolation Forest.

## Instalação

Na raiz do repositório:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\\Scripts\\activate
pip install -r backend/requirements.txt
```

## Executar

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Documentação: `http://localhost:8000/docs`.

## Endpoints para o frontend

### Status dos pipelines

```http
GET /pipelines
```

### Classificação

```http
POST /predict
Content-Type: application/json
```

```json
{
  "text": "Texto completo da notícia.",
  "pipeline": "svm"
}
```

Valores aceitos para `pipeline`: `svm` e `kmeans`. O K-Means retorna o cluster técnico; a equipe deve definir no frontend a interpretação dos clusters após avaliar seus centróides.

### Anomalias

```http
POST /anomaly
Content-Type: application/json
```

```json
{
  "text": "Texto completo da notícia.",
  "pipeline": "isolation_forest"
}
```

Valores aceitos: `dbscan` e `isolation_forest`.

## Instalação dos modelos

Coloque os arquivos `.joblib` em `backend/app/models/`:

```text
svm.joblib
kmeans.joblib
dbscan.joblib
isolation_forest.joblib
```

O carregamento ocorre quando a API inicia. Depois de adicionar ou substituir os arquivos, reinicie o Uvicorn.

## Exemplo JavaScript

```javascript
const response = await fetch('http://localhost:8000/predict', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({text: texto, pipeline: 'svm'})
});
const resultado = await response.json();
```

Para DBSCAN e Isolation Forest, use `/anomaly`.

Sem artefatos treinados, a API mantém o contrato ativo e informa `model_loaded: false`. Não use o fallback como resultado científico; ele existe somente para testar a integração.
