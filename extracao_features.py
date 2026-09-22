"""
extracao_features.py
---------------------
Arquivo único com toda a extração de features do dataset DUAT a partir do
texto puro de uma notícia. Junta o que antes estava em três arquivos
separados (features_prontas.py + features_gramaticais.py +
montar_dataset_completo.py), pensado para ser reaproveitado depois na
extração de features de notícias que o usuário for colocando (uma a uma ou
em lote).

Contém três blocos:

  1. FEATURES PRONTAS — funções que já existiam em montar_dataset_duat.py
     (palavras sensacionalistas, fontes citadas, estudos prévios citados,
     índice de legibilidade), refatoradas em funções reutilizáveis.

  2. FEATURES GRAMATICAIS — calculadas a partir do texto puro via spaCy
     (pt_core_news_sm): num_palavras, num_types, tamanho_medio_palavra,
     tamanho_medio_frase, verbos, verbos_subj_imp, substantivos, adjetivos,
     advérbios, modais, pronomes, pct_erro_ortografico, pausalidade,
     emotividade.

  3. MONTAGEM DO DATASET — junta os dois blocos acima, calcula as
     proporções (contagem / num_palavras) e devolve o DataFrame final, na
     mesma ordem de colunas usada no projeto (ainda em escala bruta — a
     normalização 0-1 e o float32 continuam em padronizar_normalizar.py).

A coluna 'categoria' NÃO é usada (removida por decisão do time).

Premissas assumidas e validadas empiricamente contra dataset_sem_balancear.csv
(o artigo original do Fake.br não detalha o etiquetador NLPNet nem o
corretor ortográfico usado — ver seção 5 da documentação):
  - Etiquetador morfossintático: spaCy (pt_core_news_sm) no lugar do NLPNet.
  - "substantivos" = NOUN + PROPN (nome comum + próprio).
  - Nº de frases: contado por regex simples (sequências de . ! ?), não pela
    segmentação de sentenças do parser do spaCy — deu correlação bem mais
    alta contra a referência.
  - "pausalidade": todos os sinais de pontuação (regex) / nº de frases.
  - "verbos" = tag VERB; "verbos_modais" = tag AUX (mutuamente exclusivos).
  - "pronomes" = tag PRON.
  - Erro ortográfico: pyspellchecker (dicionário pt), ignorando nomes
    próprios.
Detalhes da validação (correlação/MAE contra o dataset já pronto) estão no
relatorio_validacao.md.

Uso via linha de comando:
    python extracao_features.py entrada.csv saida_bruto.csv

Uso em Python (é o jeito recomendado para aplicar em notícias novas):
    import pandas as pd
    from extracao_features import montar_dataset

    df = pd.read_csv('minhas_noticias.csv')   # precisa ter a coluna 'texto'
    df_bruto = montar_dataset(df)
"""

import re
import sys

import pandas as pd
import spacy
from spellchecker import SpellChecker


# ============================================================
# BLOCO 1 — FEATURES PRONTAS
# (refatorado de montar_dataset_duat.py)
# ============================================================

PALAVRAS_SENSACIONALISTAS = [
    'urgente', 'chocante', 'bomba', 'revelado', 'você não vai acreditar',
    'inacreditável', 'absurdo', 'escândalo', 'alerta', 'atenção',
    'exclusivo', 'impressionante', 'polêmica', 'espantoso', 'grave',
    'crime', 'ataque', 'perigo', 'alarmante', 'insano',
]
_PADRAO_SENSACIONALISTA = re.compile(
    r'\b(' + '|'.join(PALAVRAS_SENSACIONALISTAS) + r')\b',
    flags=re.IGNORECASE
)

_PADRAO_FONTES = re.compile(
    r'\bsegundo\b|\bde acordo com\b|\bconforme\b|\bdisse\b|\bafirmou\b|'
    r'\bdeclarou\b|\brevelou\b|\binformou\b|\baponta\b|\baponta que\b',
    flags=re.IGNORECASE
)

_PADRAO_ESTUDOS = re.compile(
    r'\bestudo[s]?\b|\bpesquisa[s]?\b|\bpesquisador(es)?\b|\bcientista[s]?\b|'
    r'\buniversidade\b|\binstituto\b|\brevista científica\b|\bpublicado(a)? n[ao]\b',
    flags=re.IGNORECASE
)


def contar_palavras_sensacionalistas(texto: str) -> int:
    """Conta ocorrências de termos de apelo emocional/alarmista no texto."""
    return len(_PADRAO_SENSACIONALISTA.findall(str(texto)))


def contar_fontes_citadas(texto: str) -> int:
    """Conta expressões típicas de atribuição de fonte no texto (proxy)."""
    return len(_PADRAO_FONTES.findall(str(texto)))


def contar_estudos_previos(texto: str) -> int:
    """Conta menções a estudo/pesquisa/universidade/instituto no texto (proxy)."""
    return len(_PADRAO_ESTUDOS.findall(str(texto)))


# --- Índice de Legibilidade (ILF) — Flesch adaptado ao português ---
# Fórmula: Martins et al. (1996)
# ILF = 248.835 - 1.015*(palavras/frases) - 84.6*(sílabas/palavras)
VOGAIS = 'aeiouáéíóúâêîôûãõàèìòù'


def contar_silabas_palavra(palavra: str) -> int:
    """Estima sílabas contando grupos de vogais consecutivas (heurística padrão)."""
    palavra = palavra.lower()
    silabas = 0
    vogal_anterior = False
    for letra in palavra:
        eh_vogal = letra in VOGAIS
        if eh_vogal and not vogal_anterior:
            silabas += 1
        vogal_anterior = eh_vogal
    return max(silabas, 1)  # toda palavra tem ao menos 1 sílaba


def contar_silabas_texto(texto: str) -> int:
    palavras = re.findall(
        r'[a-záéíóúâêîôûãõàèìòüçA-ZÁÉÍÓÚÂÊÎÔÛÃÕÀÈÌÒÜÇ]+', str(texto)
    )
    if not palavras:
        return 0
    return sum(contar_silabas_palavra(p) for p in palavras)


def calcular_indice_legibilidade(texto: str, num_palavras: float,
                                  tamanho_medio_frase: float):
    """Índice de legibilidade (ILF), réplica da fórmula de montar_dataset_duat.py."""
    if num_palavras == 0 or tamanho_medio_frase == 0:
        return None

    total_silabas = contar_silabas_texto(texto)
    silabas_por_palavra = total_silabas / num_palavras

    ilf = 248.835 - (1.015 * tamanho_medio_frase) - (84.6 * silabas_por_palavra)
    return ilf


# ============================================================
# BLOCO 2 — FEATURES GRAMATICAIS (via spaCy)
# ============================================================

_PADRAO_FIM_FRASE = re.compile(r'[.!?]+')
_PADRAO_PONTUACAO = re.compile(r'[.,;:!?\-\"\'\(\)]')

_nlp = None
_spell = None


def _carregar_modelos():
    global _nlp, _spell
    if _nlp is None:
        _nlp = spacy.load('pt_core_news_sm', disable=['ner', 'lemmatizer', 'parser'])
    if _spell is None:
        _spell = SpellChecker(language='pt')
    return _nlp, _spell


def _eh_palavra(token) -> bool:
    """Token considerado 'palavra' (exclui pontuação, espaço e símbolo)."""
    return not (token.is_punct or token.is_space or token.pos_ == 'SYM')


def _extrair_features_doc(doc, texto_original: str, spell: SpellChecker) -> dict:
    tokens_palavra = [t for t in doc if _eh_palavra(t)]
    num_palavras = len(tokens_palavra)

    # nº de frases via regex (mais fiel ao NLPNet do que o parser do spaCy)
    num_frases = max(len(_PADRAO_FIM_FRASE.findall(texto_original)), 1)

    # --- types (palavras únicas, minúsculas) ---
    types = {t.text.lower() for t in tokens_palavra}
    num_types = len(types)

    # --- tamanho médio da palavra (caracteres) ---
    total_caracteres = sum(len(t.text) for t in tokens_palavra)
    tamanho_medio_palavra = total_caracteres / num_palavras if num_palavras else 0.0

    # --- tamanho médio da frase (palavras por frase) ---
    tamanho_medio_frase = num_palavras / num_frases

    # --- contagens gramaticais via POS/morph ---
    num_verbos = 0
    verbos_subj_imp = 0
    num_substantivos = 0
    num_adjetivos = 0
    num_adverbios = 0
    verbos_modais = 0
    num_pronomes = 0

    for t in doc:
        pos = t.pos_
        if pos == 'VERB':
            num_verbos += 1
            mood = t.morph.get('Mood')
            if mood and (mood[0] in ('Sub', 'Imp')):
                verbos_subj_imp += 1
        elif pos == 'AUX':
            verbos_modais += 1
            mood = t.morph.get('Mood')
            if mood and (mood[0] in ('Sub', 'Imp')):
                verbos_subj_imp += 1
        elif pos in ('NOUN', 'PROPN'):
            num_substantivos += 1
        elif pos == 'ADJ':
            num_adjetivos += 1
        elif pos == 'ADV':
            num_adverbios += 1
        elif pos == 'PRON':
            num_pronomes += 1

    # --- pontuação / pausalidade ---
    num_pontuacao = len(_PADRAO_PONTUACAO.findall(texto_original))
    pausalidade = num_pontuacao / num_frases

    # --- emotividade ---
    denom_emot = (num_substantivos + num_verbos)
    emotividade = (num_adjetivos + num_adverbios) / denom_emot if denom_emot else 0.0

    # --- erro ortográfico (proporção) ---
    # ignora nomes próprios (PROPN) para não penalizar nomes de pessoas/lugares
    palavras_alpha_sem_propn = [t.text for t in tokens_palavra
                                 if t.is_alpha and t.pos_ != 'PROPN']
    if palavras_alpha_sem_propn:
        desconhecidas = spell.unknown([w.lower() for w in palavras_alpha_sem_propn])
        pct_erro_ortografico = len(desconhecidas) / len(palavras_alpha_sem_propn)
    else:
        pct_erro_ortografico = 0.0

    return {
        'num_palavras': num_palavras,
        'num_types': num_types,
        'tamanho_medio_palavra': tamanho_medio_palavra,
        'tamanho_medio_frase': tamanho_medio_frase,
        'num_verbos': num_verbos,
        'verbos_subj_imp': verbos_subj_imp,
        'num_substantivos': num_substantivos,
        'num_adjetivos': num_adjetivos,
        'num_adverbios': num_adverbios,
        'verbos_modais': verbos_modais,
        'num_pronomes': num_pronomes,
        'pct_erro_ortografico': pct_erro_ortografico,
        'pausalidade': pausalidade,
        'emotividade': emotividade,
    }


def processar_textos(textos, batch_size: int = 50, n_process: int = 1, verbose: bool = True):
    """Recebe uma lista/Series de textos e devolve um DataFrame com as
    features gramaticais calculadas para cada um (na mesma ordem).
    Use n_process > 1 para acelerar em datasets grandes (usa mais núcleos)."""
    nlp, spell = _carregar_modelos()
    textos = [str(t) for t in textos]
    registros = []
    total = len(textos)
    for i, doc in enumerate(nlp.pipe(textos, batch_size=batch_size, n_process=n_process)):
        registros.append(_extrair_features_doc(doc, textos[i], spell))
        if verbose and (i + 1) % 500 == 0:
            print(f'  processados {i + 1}/{total} textos...')
    return pd.DataFrame(registros)


def processar_dataframe(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """Recebe um DataFrame com a coluna 'texto' (obrigatória) e devolve um
    novo DataFrame só com as features gramaticais/estruturais calculadas
    aqui."""
    if 'texto' not in df.columns:
        raise ValueError("DataFrame precisa ter a coluna 'texto'.")

    feats = processar_textos(df['texto'].tolist(), verbose=verbose)
    feats.index = df.index
    return feats


# ============================================================
# BLOCO 3 — MONTAGEM DO DATASET FINAL
# ============================================================

ORDEM_FINAL = [
    'tamanho_medio_palavra',
    'num_palavras',
    'pct_erro_ortografico',
    'types_proporcao',
    'fontes_proporcao',
    'estudos_previos_proporcao',
    'emotividade',
    'sensacionalismo_proporcao',
    'verbos_proporcao',
    'verbos_subj_imp_proporcao',
    'substantivos_proporcao',
    'adjetivos_proporcao',
    'adverbios_proporcao',
    'modais_proporcao',
    'pronomes_proporcao',
    'pausalidade',
    'indice_legibilidade',
    'tamanho_medio_frase',
]


def montar_dataset(df_entrada: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """Recebe um DataFrame com a coluna 'texto' (e opcionalmente
    'rotulo'/'label') e devolve o dataset final com todas as features,
    ainda em escala bruta (não normalizada — isso é feito depois por
    padronizar_normalizar.py)."""
    df_entrada = df_entrada.copy()
    df_entrada.columns = df_entrada.columns.str.strip()  # ex.: 'texto  ' -> 'texto'

    if 'texto' not in df_entrada.columns:
        raise ValueError(
            f"O CSV de entrada precisa ter a coluna 'texto'. Colunas encontradas: "
            f"{list(df_entrada.columns)[:10]}."
        )

    if verbose:
        print(f"Dataset de entrada: {df_entrada.shape[0]} linhas")
        print("Calculando features gramaticais/estruturais (spaCy)...")
    gram = processar_dataframe(df_entrada, verbose=verbose)

    if verbose:
        print("Calculando features prontas (regex + índice de legibilidade)...")
    textos = df_entrada['texto'].astype(str)

    num_sensacionalistas = textos.apply(contar_palavras_sensacionalistas)
    num_fontes = textos.apply(contar_fontes_citadas)
    num_estudos = textos.apply(contar_estudos_previos)

    indice_legibilidade = [
        calcular_indice_legibilidade(t, gram['num_palavras'].iloc[i], gram['tamanho_medio_frase'].iloc[i])
        for i, t in enumerate(textos)
    ]

    df_final = pd.DataFrame(index=df_entrada.index)

    df_final['texto'] = df_entrada['texto'].values

    df_final['tamanho_medio_palavra'] = gram['tamanho_medio_palavra']
    df_final['num_palavras'] = gram['num_palavras']
    df_final['pct_erro_ortografico'] = gram['pct_erro_ortografico']

    num_palavras_safe = gram['num_palavras'].replace(0, pd.NA)

    df_final['types_proporcao'] = gram['num_types'] / num_palavras_safe
    df_final['fontes_proporcao'] = num_fontes / num_palavras_safe
    df_final['estudos_previos_proporcao'] = num_estudos / num_palavras_safe
    df_final['emotividade'] = gram['emotividade']
    df_final['sensacionalismo_proporcao'] = num_sensacionalistas / num_palavras_safe
    df_final['verbos_proporcao'] = gram['num_verbos'] / num_palavras_safe
    df_final['verbos_subj_imp_proporcao'] = gram['verbos_subj_imp'] / num_palavras_safe
    df_final['substantivos_proporcao'] = gram['num_substantivos'] / num_palavras_safe
    df_final['adjetivos_proporcao'] = gram['num_adjetivos'] / num_palavras_safe
    df_final['adverbios_proporcao'] = gram['num_adverbios'] / num_palavras_safe
    df_final['modais_proporcao'] = gram['verbos_modais'] / num_palavras_safe
    df_final['pronomes_proporcao'] = gram['num_pronomes'] / num_palavras_safe
    df_final['pausalidade'] = gram['pausalidade']
    df_final['indice_legibilidade'] = indice_legibilidade
    df_final['tamanho_medio_frase'] = gram['tamanho_medio_frase']

    df_final = df_final.fillna(0.0)

    # rótulo, se existir na entrada (como 'rotulo' ou 'label')
    if 'rotulo' in df_entrada.columns:
        df_final['rotulo'] = df_entrada['rotulo'].values
    elif 'label' in df_entrada.columns:
        df_final['rotulo'] = df_entrada['label'].map({'fake': 0, 'real': 1}).values

    colunas_presentes = ['texto'] + ORDEM_FINAL + (['rotulo'] if 'rotulo' in df_final.columns else [])
    df_final = df_final[colunas_presentes]

    if verbose:
        print(f"Dataset final montado: {df_final.shape[0]} linhas, {df_final.shape[1]} colunas")

    return df_final


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Uso: python extracao_features.py entrada.csv saida.csv")
        sys.exit(1)

    caminho_entrada, caminho_saida = sys.argv[1], sys.argv[2]
    df_in = pd.read_csv(caminho_entrada)
    df_out = montar_dataset(df_in)
    df_out.to_csv(caminho_saida, index=False)
    print(f"Salvo em: {caminho_saida}")
