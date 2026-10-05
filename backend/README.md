# DUAT Backend

Backend FastAPI para a análise DUAT, seguindo o fluxo do notebook `DUAT-Analise-Noticia.ipynb`.

## Execução

Na raiz do repositório:

```bash
pip install -r backend/requirements.txt
python -m spacy download pt_core_news_sm
uvicorn backend.app.main:app --reload
```

## Variáveis opcionais

```bash
export DUAT_DATASET_PATH=dataset_duat_final.csv
export DUAT_REFERENCE_CACHE=referencia_bruta.csv
```

O arquivo `extracao_features.py` precisa estar na raiz ou em `backend/`. Os modelos esperados ficam em `backend/app/models/`.

## Endpoints

- `GET /health`
- `POST /api/v1/analyze`

Exemplo:

```json
{
  "text": "Texto completo da notícia...",
  "user_evaluation": "n"
}
```

As opções de avaliação são `v`, `f` e `n`. A resposta contém features brutas/escaladas, perfil K-Means, percentis dos seis critérios prioritários, comparação por classe, predição SVM e segurança relativa.

O DUAT é contexto para decisão e não um verificador de fatos.
