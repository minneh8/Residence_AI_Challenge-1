# DUAT Backend

API FastAPI para extração de características e classificação de notícias.

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

## Treinar o modelo

O dataset `dataset_duat_final.csv` deve estar na raiz do repositório:

```bash
cd backend
python train_model.py
```

O modelo é gerado em `backend/app/models/duat_model.joblib`. Esse artefato é ignorado pelo Git; o treinamento deve ser executado no ambiente de implantação.

## Executar a API

Na raiz do projeto:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Documentação interativa: `http://localhost:8000/docs`.

## Endpoints

### `GET /health`

Verifica se a API está funcionando e se um modelo treinado foi carregado.

### `POST /features`

```json
{"text": "Texto da notícia com pelo menos vinte caracteres."}
```

### `POST /predict`

```json
{"text": "Texto da notícia com pelo menos vinte caracteres."}
```

Também é possível enviar `features` calculadas pelo cliente, desde que todas as 18 features do modelo estejam presentes. O endpoint retorna rótulo, probabilidades, confiança, features e explicações básicas.

## Observação

Sem o artefato treinado, a API utiliza um fallback heurístico apenas para manter o fluxo de desenvolvimento funcionando. Para resultados reais, execute `python backend/train_model.py` antes de publicar a aplicação.
