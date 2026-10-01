# Modelos dos pipelines

Coloque nesta pasta os artefatos treinados com estes nomes exatos:

- `svm.joblib`
- `kmeans.joblib`
- `dbscan.joblib`
- `isolation_forest.joblib`

Cada arquivo deve ser um objeto scikit-learn já treinado e receber um DataFrame com as 18 colunas definidas em `app/services/feature_extractor.py`.

## Contratos esperados

### SVM

Deve implementar `predict`. Para probabilidades, treine o `SVC` com `probability=True`.

### K-Means

Deve implementar `predict`, retornando o cluster. O endpoint `/predict` converte o cluster em `classification` apenas como saída técnica; o significado semântico dos clusters deve ser definido pela equipe após analisar os centróides.

### DBSCAN

Deve implementar `predict` ou ser encapsulado em um pipeline que implemente esse método. O endpoint `/anomaly` considera o rótulo `-1` como anomalia.

### Isolation Forest

Deve implementar `predict`, em que `-1` representa anomalia e `1` representa observação normal. O endpoint `/anomaly` também utiliza `decision_function` quando disponível.

O backend não treina nem inventa os pipelines automaticamente. Enquanto os artefatos não existirem, os endpoints continuam disponíveis e retornam `model_loaded: false`, usando fallback apenas para desenvolvimento.
