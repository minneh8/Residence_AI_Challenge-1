# DUAT Backend alinhado ao notebook

O fluxo principal reproduz o notebook `DUAT-Analise-Noticia.ipynb`: extrai 16 features, normaliza junto com `referencia_bruta.csv`, identifica o perfil com K-Means e executa o SVM com os 16 critérios escalados + TF-IDF.

Arquivos obrigatórios:

```text
backend/app/models/pipeline_kmeans_duat.joblib
backend/app/models/svm_bundle.joblib
backend/reference/referencia_bruta.csv
```

Use `POST /analyze` com `{"text":"notícia completa"}`. O frontend visual não é alterado; apenas o JavaScript pode consumir o endpoint se necessário.
