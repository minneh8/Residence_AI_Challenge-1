from __future__ import annotations

FEATURES = [
    "tamanho_medio_palavra", "pct_erro_ortografico", "fontes_proporcao",
    "estudos_previos_proporcao", "emotividade", "sensacionalismo_proporcao",
    "verbos_proporcao", "verbos_subj_imp_proporcao", "substantivos_proporcao",
    "adjetivos_proporcao", "adverbios_proporcao", "modais_proporcao",
    "pronomes_proporcao", "pausalidade", "indice_legibilidade",
    "tamanho_medio_frase",
]

NAMES = {
    "tamanho_medio_palavra": "Tamanho médio da palavra",
    "pct_erro_ortografico": "Erros ortográficos",
    "fontes_proporcao": "Fontes citadas",
    "estudos_previos_proporcao": "Estudos prévios citados",
    "emotividade": "Emotividade",
    "sensacionalismo_proporcao": "Palavras sensacionalistas",
    "verbos_proporcao": "Verbos",
    "verbos_subj_imp_proporcao": "Verbos de dúvida ou de ordem",
    "substantivos_proporcao": "Substantivos",
    "adjetivos_proporcao": "Adjetivos",
    "adverbios_proporcao": "Advérbios",
    "modais_proporcao": "Verbos modais",
    "pronomes_proporcao": "Pronomes",
    "pausalidade": "Pausalidade",
    "indice_legibilidade": "Índice de legibilidade",
    "tamanho_medio_frase": "Tamanho médio da frase",
}

PRIORITY_CRITERIA = {
    "nominal": [
        ("estudos_previos_proporcao", 0.121),
        ("tamanho_medio_frase", 0.102),
        ("pct_erro_ortografico", 0.095),
        ("verbos_subj_imp_proporcao", 0.087),
        ("sensacionalismo_proporcao", 0.078),
        ("substantivos_proporcao", 0.073),
    ],
    "verbal": [
        ("verbos_subj_imp_proporcao", 0.145),
        ("tamanho_medio_frase", 0.120),
        ("pct_erro_ortografico", 0.113),
        ("verbos_proporcao", 0.078),
        ("fontes_proporcao", 0.071),
        ("pausalidade", 0.060),
    ],
}

PROFILE_NAMES = {"verbal": "Narrativo / verbal", "nominal": "Descritivo / nominal"}
LABEL_NAMES = {0: "falsa", 1: "verdadeira"}
