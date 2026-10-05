# DUAT Backend alinhado ao notebook

O backend agora gera automaticamente `referencia_bruta.csv` na inicialização.

## Dataset aceito

O serviço procura, nesta ordem:

```text
backend/reference/dataset_duat_final.csv
backend/dataset_duat_final.csv
./dataset_duat_final.csv
backend/reference/DUAT_datasetv_2_1.csv
backend/DUAT_datasetv_2_1.csv
./DUAT_datasetv_2_1.csv
```

O dataset deve conter a coluna `texto` e pode conter `rotulo`. Se já possuir as 16 features em escala bruta, elas são usadas diretamente. Se estiver normalizado ou possuir somente `texto`/`rotulo`, o backend recalcula as features para cada notícia e salva:

```text
backend/reference/referencia_bruta.csv
```

Na primeira inicialização, o processamento pode levar alguns minutos, como no notebook. As inicializações seguintes usam o cache.

## Fluxo

1. Lê o dataset.
2. Recalcula ou reutiliza as 16 features brutas.
3. Salva `referencia_bruta.csv`.
4. Normaliza a notícia junto com a referência.
5. Executa K-Means e SVM.

Depois de atualizar o código, reinicie o backend:

```bash
uvicorn backend.app.main:app --reload --port 8000
```
