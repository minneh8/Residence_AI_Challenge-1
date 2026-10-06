# DUAT Backend

Backend FastAPI para a análise DUAT, seguindo o fluxo do notebook `DUAT-Analise-Noticia.ipynb`.

## Execução

Na raiz do repositório:

```bash
pip install -r backend/requirements.txt
python -m spacy download pt_core_news_sm
uvicorn backend.app.main:app --reload
```

## Cache da referência

Na primeira execução, se `backend/reference/referencia_bruta.csv` não existir, o backend lê o dataset configurado e cria o cache bruto. Nas execuções seguintes, o cache é carregado do disco uma vez e depois mantido em memória; o dataset pesado não é processado novamente para cada notícia.

Para forçar a recriação:

```bash
rm backend/reference/referencia_bruta.csv
```

No PowerShell:

```powershell
Remove-Item backend/reference/referencia_bruta.csv
```

Variáveis opcionais:

```bash
DUAT_DATASET_PATH=dataset_duat_final.csv
DUAT_REFERENCE_CACHE=backend/reference/referencia_bruta.csv
```

O cache não deve ser recriado automaticamente depois de existir. Se o dataset mudar, remova o cache manualmente.

## Endpoints

- `GET /health`
- `POST /api/v1/analyze`
- `POST /features`
- `POST /predict`

O DUAT é contexto para decisão e não um verificador de fatos.
