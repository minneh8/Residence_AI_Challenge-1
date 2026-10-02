# DUAT Backend — validação e SVM

O backend agora rejeita textos que não parecem notícias completas: mínimo de 40 palavras e 250 caracteres.

O endpoint `/predict` usa `svm_bundle.joblib`, aplica o scaler e o embedding TF-IDF salvos, retorna `decision_score` e usa `label_mapping` salvo no bundle.

Gere o bundle atualizado executando o notebook `DUAT_SVM_Diagnostico_Recalibrado.ipynb`. Ele mantém o embedding TF-IDF, verifica o mapeamento dos rótulos, usa `SVC(probability=True)`, mede balanced accuracy e salva `Pipelines/svm_bundle.joblib`.

Após substituir o arquivo no backend, reinicie a API.