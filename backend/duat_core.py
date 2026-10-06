# ===== Funções do DUAT (análise de uma notícia) =====
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import joblib
from scipy.sparse import hstack, csr_matrix

from extracao_features import montar_dataset, padronizar_dataframe

warnings.filterwarnings("ignore", category=UserWarning)

FEATURES = ['tamanho_medio_palavra', 'pct_erro_ortografico', 'fontes_proporcao',
            'estudos_previos_proporcao', 'emotividade', 'sensacionalismo_proporcao',
            'verbos_proporcao', 'verbos_subj_imp_proporcao', 'substantivos_proporcao',
            'adjetivos_proporcao', 'adverbios_proporcao', 'modais_proporcao',
            'pronomes_proporcao', 'pausalidade', 'indice_legibilidade', 'tamanho_medio_frase']

NOMES = {
    'tamanho_medio_palavra': 'Tamanho médio da palavra',
    'pct_erro_ortografico': 'Erros ortográficos',
    'fontes_proporcao': 'Fontes citadas',
    'estudos_previos_proporcao': 'Estudos prévios citados',
    'emotividade': 'Emotividade',
    'sensacionalismo_proporcao': 'Palavras sensacionalistas',
    'verbos_proporcao': 'Verbos',
    'verbos_subj_imp_proporcao': 'Verbos de dúvida ou de ordem',
    'substantivos_proporcao': 'Substantivos',
    'adjetivos_proporcao': 'Adjetivos',
    'adverbios_proporcao': 'Advérbios',
    'modais_proporcao': 'Verbos modais',
    'pronomes_proporcao': 'Pronomes',
    'pausalidade': 'Pausalidade',
    'indice_legibilidade': 'Índice de legibilidade',
    'tamanho_medio_frase': 'Tamanho médio da frase',
}

# Critérios prioritários por perfil (Random Forest treinado dentro de cada perfil, seção 6.3)
PERFIS = {
    'nominal': {
        'nome': 'Descritivo / nominal',
        'descricao': 'muitos substantivos, palavras e frases longas, poucos verbos e pronomes — estilo denso e factual',
        'criterios': [
            ('estudos_previos_proporcao', 0.121, 'Textos descritivos citam pesquisas e fontes acadêmicas para embasar os fatos — é onde essa feature aparece.'),
            ('tamanho_medio_frase', 0.102, 'O estilo denso é feito de frases longas; o comprimento é característico deste perfil.'),
            ('pct_erro_ortografico', 0.095, 'Por se apresentarem como formais, esses textos têm padrão ortográfico mais controlado, o que torna a feature discriminativa aqui.'),
            ('verbos_subj_imp_proporcao', 0.087, 'Mede o uso de verbos de dúvida (“teria”, “seria”) ou de ordem (“veja”, “compartilhe”). O estilo descritivo narra fatos confirmados e quase não os usa, então eles se destacam quando aparecem.'),
            ('sensacionalismo_proporcao', 0.078, 'O tom é sóbrio e informativo, então termos sensacionalistas são incomuns e ganham peso quando aparecem.'),
            ('substantivos_proporcao', 0.073, 'É a marca central do estilo — a alta densidade de substantivos define o texto nominal.'),
        ],
    },
    'verbal': {
        'nome': 'Narrativo / verbal',
        'descricao': 'muitos verbos, pronomes e advérbios, frases curtas e mais legíveis — estilo de relato',
        'criterios': [
            ('verbos_subj_imp_proporcao', 0.145, 'A narrativa usa muito o subjuntivo e o imperativo para especular e convocar (“teria feito”, “veja”) — é o traço mais marcante deste estilo.'),
            ('tamanho_medio_frase', 0.120, 'O estilo é feito de frases curtas; o comprimento caracteriza o ritmo narrativo.'),
            ('pct_erro_ortografico', 0.113, 'O tom coloquial e espontâneo convive com mais variação ortográfica, tornando a feature relevante aqui.'),
            ('verbos_proporcao', 0.078, 'É a marca central do estilo — a alta densidade de verbos define o texto de ação.'),
            ('fontes_proporcao', 0.071, 'O relato dinâmico se apoia em citações e falas (“segundo ele”, “disse que”), onde essa feature se manifesta.'),
            ('pausalidade', 0.060, 'O ritmo acelerado da narrativa se reflete no padrão de pausas e pontuação.'),
        ],
    },
}

# cores neutras (antes da resposta) e por classe (depois da resposta)
COR_FAIXA, COR_NOTICIA, COR_DESTAQUE = '#c9c9c9', '#3b6ea8', '#1f1f1f'
COR_FALSA, COR_VERDADEIRA = '#c0504d', '#2e8b57'


# ---------------------------------------------------------------- modelos
def carregar_modelos(caminho_kmeans, caminho_svm):
    kmeans = joblib.load(caminho_kmeans)
    svm = joblib.load(caminho_svm)
    assert list(kmeans.named_steps['scaler'].feature_names_in_) == FEATURES, 'Features do K-Means diferentes do esperado.'
    assert list(svm['numeric_features']) == FEATURES, 'Features numéricas do SVM diferentes do esperado.'
    # qual cluster é o perfil verbal: maior centroide em verbos_proporcao
    c = kmeans.named_steps['kmeans'].cluster_centers_
    i_verbos = FEATURES.index('verbos_proporcao')
    verbal = int(np.argmax(c[:, i_verbos]))
    mapa_cluster = {verbal: 'verbal', 1 - verbal: 'nominal'}
    return kmeans, svm, mapa_cluster


# ---------------------------------------------------------------- dataset de referência
def _esta_normalizado(df):
    cols = [c for c in FEATURES if c in df.columns]
    if len(cols) < len(FEATURES):
        return None
    return bool(df['indice_legibilidade'].max() <= 1.0001 and df['indice_legibilidade'].min() >= -0.0001)


def carregar_referencia_bruta(caminho_dataset, caminho_cache='referencia_bruta.csv'):
    """Devolve o dataset de referência (v2.1) em ESCALA BRUTA, com 'texto' e 'rotulo'.
    A normalização min-max usa o mínimo e o máximo deste dataset (seção 2.4.2);
    a notícia nova é escalada com esses mesmos valores."""
    if Path(caminho_cache).exists():
        ref = pd.read_csv(caminho_cache)
        print(f'Referência bruta carregada do cache: {ref.shape[0]} notícias')
        return ref
    df = pd.read_csv(caminho_dataset)
    df.columns = df.columns.str.strip()
    normalizado = _esta_normalizado(df)
    if normalizado is False:
        print('O dataset já está em escala bruta: usando os valores do arquivo.')
        ref = df
    else:
        if 'texto' not in df.columns:
            raise ValueError('O dataset está normalizado e não tem a coluna "texto": '
                             'não é possível recuperar o mínimo e o máximo da escala bruta.')
        print('O dataset está normalizado (0 a 1). Recalculando as features em escala bruta '
              'a partir do texto (é feito uma única vez e salvo em cache)...')
        ref = montar_dataset(df[['texto'] + (['rotulo'] if 'rotulo' in df.columns else [])], verbose=True)
    ref.to_csv(caminho_cache, index=False)
    return ref


# ---------------------------------------------------------------- extração e escala
def normalizar_referencia(ref_bruta):
    """Normaliza o dataset de referência (min-max 0 a 1, como na documentação).
    É a régua fixa: não muda com a notícia analisada."""
    ref_norm = padronizar_dataframe(ref_bruta, verbose=False)
    ref_norm[FEATURES] = ref_norm[FEATURES].astype(np.float64)  # float64, como no treinamento
    return ref_norm


def extrair_e_escalar(texto, ref_bruta, ref_norm=None):
    """1) extrai as features da notícia em escala bruta;
    2) escala a notícia com o mínimo e o máximo do dataset de referência
       (a referência não é recalculada); valores fora da faixa viram 0 ou 1;
    3) devolve a notícia e a referência já normalizadas."""
    nova_bruta = montar_dataset(pd.DataFrame({'texto': [texto]}), verbose=False)
    if ref_norm is None:
        ref_norm = normalizar_referencia(ref_bruta)
    noticia = nova_bruta.copy()
    cols = [c for c in nova_bruta.select_dtypes(include=[np.number]).columns
            if c in ref_bruta.columns and c != 'rotulo']
    for c in cols:
        minimo, maximo = ref_bruta[c].min(), ref_bruta[c].max()
        amplitude = maximo - minimo
        if amplitude == 0 or pd.isna(amplitude):
            noticia[c] = 0.0
        else:
            noticia[c] = ((nova_bruta[c] - minimo) / amplitude).clip(0, 1)
        noticia[c] = noticia[c].astype(np.float32)
    noticia[FEATURES] = noticia[FEATURES].astype(np.float64)
    fora = [c for c in FEATURES
            if nova_bruta[c].iloc[0] < ref_bruta[c].min() or nova_bruta[c].iloc[0] > ref_bruta[c].max()]
    return nova_bruta, noticia.reset_index(drop=True), ref_norm, fora


# ---------------------------------------------------------------- perfil (K-Means)
def perfil_da_noticia(kmeans, mapa_cluster, noticia, ref_norm):
    cl = int(kmeans.predict(noticia[FEATURES])[0])
    ref_cl = kmeans.predict(ref_norm[FEATURES])
    return mapa_cluster[cl], cl, ref_cl


def percentil(valores, v):
    valores = np.asarray(valores, dtype=float)
    return 100 * (np.mean(valores < v) + 0.5 * np.mean(valores == v))


def situacao(p):
    return 'abaixo do comum' if p < 25 else ('acima do comum' if p > 75 else 'dentro do comum')


def situacao_valor(valores, v, tol=1e-12):
    """Situação pelo VALOR: compara com o Q1 e o Q3 do perfil (metade central).
    Sem empates dá o mesmo resultado que situacao(percentil); com muitos empates
    (ex.: muitas notícias com zero), o valor empatado não é chamado de incomum
    quando faz parte da metade central."""
    q1, q3 = np.percentile(np.asarray(valores, dtype=float), [25, 75])
    if v < q1 - tol:
        return 'abaixo do comum'
    if v > q3 + tol:
        return 'acima do comum'
    return 'dentro do comum'


def faixa_tipica(valores):
    """Metade central do perfil (Q1 a Q3) na escala de percentil da régua."""
    valores = np.asarray(valores, dtype=float)
    q1, q3 = np.percentile(valores, [25, 75])
    return percentil(valores, q1), percentil(valores, q3)


def tabela_criterios(perfil, noticia, ref_perfil):
    linhas = []
    for f, imp, explic in PERFIS[perfil]['criterios']:
        v = float(noticia[f].iloc[0]); p = percentil(ref_perfil[f], v)
        linhas.append({'Critério': NOMES[f], 'Importância': round(imp, 3), 'Score (0 a 1)': round(v, 4),
                       'Percentil no perfil': int(round(p)), 'Situação': situacao_valor(ref_perfil[f], v), 'O que significa': explic})
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------- gráficos
def regua(perfil, noticia, ref_perfil, por_classe=False, rotulo_ref=None):
    crit = PERFIS[perfil]['criterios']
    fig, ax = plt.subplots(figsize=(10, 0.75 * len(crit) + 1.4))
    for i, (f, _, _) in enumerate(crit):
        y = len(crit) - 1 - i
        p = percentil(ref_perfil[f], float(noticia[f].iloc[0]))
        ax.plot([0, 100], [y, y], color='#ededed', lw=8, solid_capstyle='butt', zorder=1)
        sit = situacao_valor(ref_perfil[f], float(noticia[f].iloc[0]))
        if not por_classe:
            a0, b0 = faixa_tipica(ref_perfil[f])
            ax.plot([a0, max(b0, a0 + 1)], [y, y], color=COR_FAIXA, lw=8, solid_capstyle='butt', zorder=2)
        else:
            for cls, cor, dy in [(0, COR_FALSA, 0.13), (1, COR_VERDADEIRA, -0.13)]:
                vals = ref_perfil.loc[rotulo_ref == cls, f]
                q1, q3 = np.percentile(vals, [25, 75])
                a, b = percentil(ref_perfil[f], q1), percentil(ref_perfil[f], q3)
                m = percentil(ref_perfil[f], vals.median())
                ax.plot([a, max(b, a + 1)], [y + dy, y + dy], color=cor, lw=5, alpha=0.75, solid_capstyle='butt', zorder=2)
                ax.plot([m, m], [y + dy - 0.09, y + dy + 0.09], color='white', lw=2.6, zorder=3, solid_capstyle='butt')
                ax.plot([m, m], [y + dy - 0.09, y + dy + 0.09], color=cor, lw=1.2, zorder=4, solid_capstyle='butt')
        destaque = sit != 'dentro do comum'
        ax.scatter([p], [y], s=90, color=COR_NOTICIA, zorder=5, edgecolor='white', linewidth=1)
        ax.text(p, y + 0.28, f'{p:.0f}', ha='center', fontsize=9, color='#333')
        if por_classe:
            lado = dict(lado_por_criterio(perfil, noticia, ref_perfil, rotulo_ref))[f]
            txt = {0: 'mais perto das falsas', 1: 'mais perto das verdadeiras', None: 'não distingue as classes'}[lado]
            ax.text(102, y, txt, va='center', fontsize=9, fontweight='normal' if lado is None else 'bold',
                    color='#777' if lado is None else '#1a1a1a')
        else:
            ax.text(102, y, sit.replace(' do comum', '') + ' da faixa típica',
                    va='center', fontsize=9, fontweight='bold' if destaque else 'normal',
                    color=COR_DESTAQUE if destaque else '#777')
    ax.set_yticks(range(len(crit)))
    ax.set_yticklabels([NOMES[f] for f, _, _ in reversed(crit)])
    ax.set_xlim(0, 100); ax.set_ylim(-0.7, len(crit) - 0.3)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel('Posição da notícia entre as notícias do mesmo perfil (percentil)')
    for s in ['top', 'right', 'left']: ax.spines[s].set_visible(False)
    ax.tick_params(axis='y', length=0)
    titulo = f'Perfil {PERFIS[perfil]["nome"].lower()} — os 6 critérios que mais importam neste perfil'
    if por_classe:
        titulo += '\n(barras: metade central das falsas e das verdadeiras; traço: mediana)'
        from matplotlib.lines import Line2D
        ax.legend(handles=[Line2D([], [], color=COR_NOTICIA, marker='o', ls='', label='Notícia analisada'),
                           Line2D([], [], color=COR_FALSA, lw=5, label='Notícias falsas do perfil'),
                           Line2D([], [], color=COR_VERDADEIRA, lw=5, label='Notícias verdadeiras do perfil'),
                           Line2D([], [], color='#555', marker='|', ms=12, mew=1.5, ls='', label='Mediana da classe')],
                  loc='upper center', bbox_to_anchor=(0.5, -0.22), ncol=4, frameon=False, fontsize=9)
    else:
        from matplotlib.lines import Line2D
        ax.legend(handles=[Line2D([], [], color=COR_NOTICIA, marker='o', ls='', label='Notícia analisada'),
                           Line2D([], [], color=COR_FAIXA, lw=6, label='Faixa típica do perfil (metade central das notícias)')],
                  loc='upper center', bbox_to_anchor=(0.5, -0.22), ncol=2, frameon=False, fontsize=9)
    ax.set_title(titulo, fontsize=11, fontweight='bold', loc='left')
    plt.tight_layout(); plt.show()


def radar(perfil, noticia, ref_perfil):
    crit = [f for f, _, _ in PERFIS[perfil]['criterios']]
    def esc(f, v):
        lo, hi = np.percentile(ref_perfil[f], [5, 95])
        if hi - lo < 1e-12: hi = lo + 1e-12
        return float(np.clip((v - lo) / (hi - lo), 0, 1.15))
    tip = [esc(f, ref_perfil[f].median()) for f in crit]
    nov = [esc(f, float(noticia[f].iloc[0])) for f in crit]
    ang = np.linspace(0, 2 * np.pi, len(crit), endpoint=False).tolist()
    ang_c = ang + ang[:1]
    fig, ax = plt.subplots(figsize=(6.4, 6.4), subplot_kw={'polar': True})
    ax.plot(ang_c, tip + tip[:1], color='#777', ls='--', lw=1.5, label='Notícia típica do perfil (mediana)')
    ax.fill(ang_c, tip + tip[:1], color=COR_FAIXA, alpha=0.35)
    ax.plot(ang_c, nov + nov[:1], color=COR_NOTICIA, lw=2, label='Notícia analisada')
    ax.fill(ang_c, nov + nov[:1], color=COR_NOTICIA, alpha=0.15)
    ax.set_xticks(ang); ax.set_xticklabels([NOMES[f].replace(' ', '\n', 1) for f in crit], fontsize=9)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0]); ax.set_yticklabels([]); ax.set_ylim(0, 1.15)
    ax.set_title(f'Perfil {PERFIS[perfil]["nome"].lower()} — comparação com a notícia típica',
                 fontsize=11, fontweight='bold', pad=22)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.06), ncol=2, frameon=False, fontsize=9)
    plt.tight_layout(); plt.show()


# ---------------------------------------------------------------- SVM
def matriz_svm(svm, df_norm, textos):
    num = svm['scaler'].transform(df_norm[FEATURES].astype(float).values)
    tf = svm['tfidf'].transform(pd.Series(textos).astype(str))
    return np.hstack([num, tf.toarray()])  # o SVM foi treinado com matriz densa


def avaliar_svm(svm, noticia, texto, ref_norm=None, ref_textos=None):
    X = matriz_svm(svm, noticia, [texto])
    pred = int(svm['model'].predict(X)[0])
    d = float(svm['model'].decision_function(X)[0])
    nivel = None
    if ref_norm is not None and ref_textos is not None:
        dref = np.abs(svm['model'].decision_function(matriz_svm(svm, ref_norm, ref_textos)))
        t1, t2 = np.percentile(dref, [33.3, 66.7])
        nivel = 'baixa' if abs(d) < t1 else ('moderada' if abs(d) < t2 else 'alta')
    return pred, d, nivel


# ---------------------------------------------------------------- mensagens (esquema predefinido)
ROTULOS = {0: 'falsa', 1: 'verdadeira'}

def msg_perfil(perfil):
    p = PERFIS[perfil]
    return (f'A notícia se encaixa no perfil de escrita {p["nome"].upper()}: {p["descricao"]}.\n'
            'O perfil descreve o estilo do texto, e não a veracidade: os dois perfis têm notícias falsas e verdadeiras. '
            'Ele serve para mostrar quais critérios mais importam para avaliar a notícia.')


def msg_criterios(tab):
    fora = tab[tab['Situação'] != 'dentro do comum']
    if fora.empty:
        return ('Todos os critérios prioritários estão dentro da faixa comum para notícias deste perfil. '
                'Observe os valores e as explicações da tabela para formar a sua opinião.')
    linhas = ['Critérios que fogem do comum para notícias deste perfil:']
    for _, r in fora.iterrows():
        linhas.append(f'  • {r["Critério"]}: {r["Situação"]} (percentil {r["Percentil no perfil"]}). {r["O que significa"]}')
    return '\n'.join(linhas)


def lado_por_criterio(perfil, noticia, ref_perfil, rotulo_ref):
    """Para cada critério, indica se a notícia está mais próxima da mediana das falsas ou das verdadeiras do perfil."""
    out = []
    for f, _, _ in PERFIS[perfil]['criterios']:
        v = float(noticia[f].iloc[0]); p = percentil(ref_perfil[f], v)
        pf = percentil(ref_perfil[f], ref_perfil.loc[rotulo_ref == 0, f].median())
        pv = percentil(ref_perfil[f], ref_perfil.loc[rotulo_ref == 1, f].median())
        if abs(pf - pv) < 5:
            lado = None
        else:
            lado = 0 if abs(p - pf) < abs(p - pv) else 1
        out.append((f, lado))
    return out


def msg_comparacao(resp_usuario, pred, nivel, lados):
    linhas = []
    conf = f' A segurança da avaliação é {nivel}, em comparação com as notícias do dataset.' if nivel else ''
    linhas.append(f'Avaliação do modelo (SVM): a notícia tem características de notícia {ROTULOS[pred].upper()}.{conf}')
    if resp_usuario is None:
        linhas.append('Você preferiu não opinar. Compare a avaliação do modelo com os critérios abaixo.')
    elif resp_usuario == pred:
        contra_ = [f for f, l in lados if l is not None and l != pred]
        linhas.append(f'Você também avaliou a notícia como {ROTULOS[pred]}.' +
                      (' Mesmo assim, confira os critérios que apontam na direção contrária antes de compartilhar.' if contra_ else ''))
    else:
        linhas.append(f'Você avaliou a notícia como {ROTULOS[resp_usuario]}, e o modelo, como {ROTULOS[pred]}. '
                      'Revise os critérios em que vocês divergiram: o modelo pode errar, e a decisão final é sua.')
    a_favor = [NOMES[f] for f, l in lados if l == pred]
    contra = [NOMES[f] for f, l in lados if l is not None and l != pred]
    if a_favor:
        linhas.append(f'  • Critérios em que a notícia se parece com as notícias {ROTULOS[pred]}s deste perfil: ' + ', '.join(a_favor) + '.')
    if contra:
        linhas.append(f'  • Critérios em que a notícia se parece com as notícias {ROTULOS[1 - pred]}s deste perfil: ' + ', '.join(contra) + '.')
    linhas.append('Lembre-se: o DUAT não é um verificador de fatos. Na dúvida, procure a notícia em veículos '
                  'confiáveis ou em agências de checagem antes de compartilhar.')
    return '\n'.join(linhas)
