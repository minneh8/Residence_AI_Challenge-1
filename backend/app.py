"""DUAT — backend da interface web.

Reaproveita as funções do notebook (duat_core.py) e expõe duas rotas:

  POST /api/analisar  → perfil de escrita, tabela de critérios, régua e radar
                        (sem o julgamento do modelo)
  POST /api/avaliar   → recebe a avaliação do usuário e só então devolve o
                        julgamento do SVM, a comparação e a régua por classe

O frontend (pasta ../frontend) é servido na raiz: http://localhost:8000
"""
import json
import os
import sys
import threading
import uuid
from collections import OrderedDict
from contextlib import asynccontextmanager
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # o duat_core importa o matplotlib; aqui não há gráficos

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

import duat_core as dc  # noqa: E402  (precisa do sys.path acima)
from extracao_features import padronizar_dataframe  # noqa: E402

# ---------------------------------------------------------------- configuração
PASTA_MODELOS = Path(os.getenv("DUAT_MODELOS", BASE / "modelos"))
CAMINHO_KMEANS = Path(os.getenv("DUAT_KMEANS", PASTA_MODELOS / "pipeline_kmeans_duat.joblib"))
CAMINHO_SVM = Path(os.getenv("DUAT_SVM", PASTA_MODELOS / "svm_bundle.joblib"))
CAMINHO_DATASET = Path(os.getenv("DUAT_DATASET", PASTA_MODELOS / "DUAT_dataset.csv"))
CAMINHO_CACHE = Path(os.getenv("DUAT_CACHE", PASTA_MODELOS / "referencia_bruta.csv"))
CAMINHO_LIMIARES = PASTA_MODELOS / "limiares_svm.json"
PASTA_FRONTEND = Path(os.getenv("DUAT_FRONTEND", BASE.parent / "frontend"))

MIN_PALAVRAS_AVISO = 50
MAX_CARACTERES = 20_000
MAX_ANALISES = 100  # análises guardadas em memória à espera da resposta do usuário

ESTADO = {}
ANALISES: "OrderedDict[str, dict]" = OrderedDict()
TRAVA = threading.Lock()  # spaCy e scikit-learn: uma análise por vez


# ---------------------------------------------------------------- carga inicial
def _limiares_seguranca(svm, ref_bruta):
    """Terços de |decision_function| nas notícias do dataset (baixa / moderada / alta).
    Calculado uma vez e salvo em disco, porque o SVM é lento em 14 mil notícias."""
    if CAMINHO_LIMIARES.exists():
        dados = json.loads(CAMINHO_LIMIARES.read_text())
        if dados.get("n") == len(ref_bruta):
            return dados["t1"], dados["t2"]
    print("Calculando os limiares de segurança do SVM (apenas na primeira vez)...")
    ref_norm = padronizar_dataframe(ref_bruta, verbose=False)
    X = dc.matriz_svm(svm, ref_norm, ref_bruta["texto"].astype(str))
    dist = np.abs(svm["model"].decision_function(X))
    t1, t2 = (float(v) for v in np.percentile(dist, [33.3, 66.7]))
    CAMINHO_LIMIARES.write_text(json.dumps({"n": len(ref_bruta), "t1": t1, "t2": t2}))
    return t1, t2


def carregar():
    for p in (CAMINHO_KMEANS, CAMINHO_SVM):
        if not p.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {p}")
    if not CAMINHO_CACHE.exists() and not CAMINHO_DATASET.exists():
        raise FileNotFoundError(
            f"Coloque o dataset v2.1 em {CAMINHO_DATASET} (ou o cache {CAMINHO_CACHE}).")
    print("Carregando modelos...")
    kmeans, svm, mapa = dc.carregar_modelos(CAMINHO_KMEANS, CAMINHO_SVM)
    print("Carregando o dataset de referência (a primeira vez recalcula as features brutas e demora alguns minutos)...")
    ref = dc.carregar_referencia_bruta(CAMINHO_DATASET, CAMINHO_CACHE)
    if "rotulo" not in ref.columns or "texto" not in ref.columns:
        raise ValueError("O dataset de referência precisa das colunas 'texto' e 'rotulo'.")
    t1, t2 = _limiares_seguranca(svm, ref)
    ESTADO.update(kmeans=kmeans, svm=svm, mapa=mapa, ref=ref, limiares=(t1, t2))
    print(f"DUAT pronto: {len(ref)} notícias de referência.")


@asynccontextmanager
async def ciclo_de_vida(app):
    carregar()
    yield


app = FastAPI(title="DUAT", lifespan=ciclo_de_vida)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ---------------------------------------------------------------- utilidades
def _pct(serie, v):
    return round(float(dc.percentil(serie, v)), 1)


def _radar(perfil, noticia, ref_perfil):
    """Mesma escala do gráfico de radar do notebook: percentis 5 a 95 do perfil viram 0 a 1."""
    eixos, tipica, nova = [], [], []
    for f, _, _ in dc.PERFIS[perfil]["criterios"]:
        lo, hi = np.percentile(ref_perfil[f], [5, 95])
        hi = hi if hi - lo > 1e-12 else lo + 1e-12
        esc = lambda v: float(np.clip((v - lo) / (hi - lo), 0, 1.15))  # noqa: E731
        eixos.append(dc.NOMES[f])
        tipica.append(round(esc(float(ref_perfil[f].median())), 4))
        nova.append(round(esc(float(noticia[f].iloc[0])), 4))
    return {"eixos": eixos, "tipica": tipica, "noticia": nova}


def _faixa(ref_perfil, f, vals):
    q1, q3 = np.percentile(vals, [25, 75])
    return {"q1": _pct(ref_perfil[f], q1), "q3": _pct(ref_perfil[f], q3),
            "mediana": _pct(ref_perfil[f], float(vals.median()))}


def _guardar(dados):
    i = uuid.uuid4().hex
    ANALISES[i] = dados
    while len(ANALISES) > MAX_ANALISES:
        ANALISES.popitem(last=False)
    return i


# ---------------------------------------------------------------- rotas
class PedidoAnalise(BaseModel):
    texto: str = Field(..., min_length=1, max_length=MAX_CARACTERES)


class PedidoAvaliacao(BaseModel):
    id: str
    resposta: str  # "verdadeira", "falsa" ou "nao_sei"


@app.get("/api/saude")
def saude():
    return {"pronto": bool(ESTADO), "noticias_referencia": len(ESTADO.get("ref", []))}


@app.post("/api/analisar")
def analisar(pedido: PedidoAnalise):
    texto = pedido.texto.strip()
    n_palavras = len(texto.split())
    if n_palavras < 3:
        raise HTTPException(400, "Digite o texto completo da notícia.")

    with TRAVA:
        ref = ESTADO["ref"]
        bruta, noticia, ref_norm, fora = dc.extrair_e_escalar(texto, ref)
        perfil, _, ref_clusters = dc.perfil_da_noticia(ESTADO["kmeans"], ESTADO["mapa"], noticia, ref_norm)

    mascara = np.array([ESTADO["mapa"][c] == perfil for c in ref_clusters])
    crit = [f for f, _, _ in dc.PERFIS[perfil]["criterios"]]
    ref_perfil = ref_norm.loc[mascara, crit].reset_index(drop=True)
    rotulo_perfil = ref["rotulo"].values[mascara]

    tabela = dc.tabela_criterios(perfil, noticia, ref_perfil)
    criterios = [{
        "feature": f,
        "nome": r["Critério"],
        "importancia": float(r["Importância"]),
        "score": float(r["Score (0 a 1)"]),
        "percentil": _pct(ref_perfil[f], float(noticia[f].iloc[0])),
        "situacao": r["Situação"],
        "explicacao": r["O que significa"],
    } for f, (_, r) in zip(crit, tabela.iterrows())]

    id_analise = _guardar({
        "texto": texto,
        "perfil": perfil,
        "noticia": noticia[dc.FEATURES].copy(),
        "ref_perfil": ref_perfil,
        "rotulo_perfil": rotulo_perfil,
    })

    p = dc.PERFIS[perfil]
    return {
        "id": id_analise,
        "n_palavras": n_palavras,
        "aviso_texto_curto": n_palavras < MIN_PALAVRAS_AVISO,
        "fora_da_faixa": [dc.NOMES[f] for f in fora],
        "perfil": {
            "chave": perfil,
            "nome": p["nome"],
            "descricao": p["descricao"],
            "noticias_no_perfil": int(mascara.sum()),
        },
        "criterios": criterios,
        "radar": _radar(perfil, noticia, ref_perfil),
    }


@app.post("/api/avaliar")
def avaliar(pedido: PedidoAvaliacao):
    dados = ANALISES.get(pedido.id)
    if dados is None:
        raise HTTPException(404, "Análise não encontrada. Envie a notícia novamente.")
    resposta = {"verdadeira": 1, "falsa": 0, "nao_sei": None}
    if pedido.resposta not in resposta:
        raise HTTPException(400, "Resposta inválida.")
    resp = resposta[pedido.resposta]

    perfil, noticia, ref_perfil, rotulo = (dados[k] for k in ("perfil", "noticia", "ref_perfil", "rotulo_perfil"))
    with TRAVA:
        X = dc.matriz_svm(ESTADO["svm"], noticia, [dados["texto"]])
        pred = int(ESTADO["svm"]["model"].predict(X)[0])
        dist = abs(float(ESTADO["svm"]["model"].decision_function(X)[0]))
    t1, t2 = ESTADO["limiares"]
    seguranca = "baixa" if dist < t1 else ("moderada" if dist < t2 else "alta")

    lados = dict(dc.lado_por_criterio(perfil, noticia, ref_perfil, rotulo))
    por_classe = []
    for f, _, _ in dc.PERFIS[perfil]["criterios"]:
        lado = lados[f]
        por_classe.append({
            "nome": dc.NOMES[f],
            "percentil": _pct(ref_perfil[f], float(noticia[f].iloc[0])),
            "falsas": _faixa(ref_perfil, f, ref_perfil.loc[rotulo == 0, f]),
            "verdadeiras": _faixa(ref_perfil, f, ref_perfil.loc[rotulo == 1, f]),
            "lado": {0: "falsas", 1: "verdadeiras", None: None}[lado],
        })

    rot = dc.ROTULOS
    if resp is None:
        comparacao = "Você preferiu não opinar. Compare a avaliação do modelo com os critérios abaixo."
    elif resp == pred:
        contra = any(l is not None and l != pred for l in lados.values())
        comparacao = f"Você também avaliou a notícia como {rot[pred]}." + (
            " Mesmo assim, confira os critérios que apontam na direção contrária antes de compartilhar." if contra else "")
    else:
        comparacao = (f"Você avaliou a notícia como {rot[resp]}, e o modelo, como {rot[pred]}. "
                      "Revise os critérios em que vocês divergiram: o modelo pode errar, e a decisão final é sua.")

    return {
        "modelo": {"rotulo": rot[pred], "seguranca": seguranca},
        "sua_resposta": None if resp is None else rot[resp],
        "comparacao": comparacao,
        "criterios_como_falsas": [dc.NOMES[f] for f, l in lados.items() if l == 0],
        "criterios_como_verdadeiras": [dc.NOMES[f] for f, l in lados.items() if l == 1],
        "por_classe": por_classe,
    }


# o frontend é montado por último, para não esconder as rotas /api
if PASTA_FRONTEND.exists():
    app.mount("/", StaticFiles(directory=PASTA_FRONTEND, html=True), name="frontend")
