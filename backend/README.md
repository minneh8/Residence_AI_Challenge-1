# DUAT Backend + Frontend

A API identifica automaticamente se cada artefato recebe texto bruto ou DataFrame.

## Pipelines TF-IDF

Se o modelo tiver um `TfidfVectorizer`, `TfidfTransformer` ou etapa com nome relacionado a `tfidf`, `vector` ou `text`, o backend chama:

```python
model.predict([texto])
```

Assim, o vocabulário original do treinamento — por exemplo `tfidf_10`, `tfidf_12` e `tfidf_2014` — é usado pelo próprio pipeline. O backend não tenta substituir essas colunas por `num_palavras` ou outras features manuais.

## Execução

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Depois de alterar qualquer `.joblib`, reinicie o processo para o registro recarregar os modelos.

Os endpoints continuam:

- `GET /health`
- `GET /pipelines`
- `POST /features`
- `POST /predict`
- `POST /anomaly`
