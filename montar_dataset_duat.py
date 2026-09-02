import pandas as pd
import re
from datetime import datetime

# ============================================
# CONFIGURAÇÃO DE CAMINHOS
# ============================================
caminho_entrada = '/Users/lucasmarassi/Library/Mobile Documents/com~apple~CloudDocs/Residencia_IA/fakebr_dataset_completo.csv'
caminho_saida = '/Users/lucasmarassi/Library/Mobile Documents/com~apple~CloudDocs/Residencia_IA/dataset_duat_final.csv'

df = pd.read_csv(caminho_entrada)
print(f"Dataset original carregado: {df.shape[0]} linhas, {df.shape[1]} colunas\n")


# ============================================
# BLOCO 1 — DADOS MANTIDOS DO DATASET ORIGINAL
# (apenas renomeados para o padrão final do grupo)
# ============================================
df_final = pd.DataFrame()

df_final['texto'] = df['texto']
df_final['link'] = df['link']
df_final['categoria'] = df['categoria']
df_final['diversidade_lexica'] = df['diversidade_lexica']
df_final['tamanho_medio_palavra'] = df['tam_medio_palavra']
df_final['data_publicacao'] = df['data_publicacao']
df_final['num_tokens'] = df['num_tokens']
df_final['num_palavras'] = df['num_palavras']
df_final['pct_erro_ortografico'] = df['pct_erro_ortografico']
df_final['emotividade'] = df['emotividade']
df_final['pausalidade'] = df['pausalidade']
df_final['tamanho_medio_frase'] = df['tam_medio_frase']

print("Bloco 1 concluído: 12 colunas mantidas do dataset original.")


# ============================================
# BLOCO 2 — RÓTULO (0 = Falso, 1 = Verdadeiro)
# ============================================
df_final['rotulo'] = df['label'].map({'fake': 0, 'real': 1})

print("Rótulo mapeado: fake -> 0, real -> 1.")


# ============================================
# BLOCO 3 — DADOS CALCULADOS VIA SCRIPT
# ============================================

# Função auxiliar: transforma contagem bruta em proporção (0 a 1)
def proporcao(coluna_contagem, coluna_palavras=df['num_palavras']):
    return coluna_contagem / coluna_palavras


# --- 3.1 Proporção de types ---
df_final['types_proporcao'] = proporcao(df['num_types'])


# --- 3.2 e 3.3 Número de fontes citadas (bruto e proporção) ---
# Proxy: conta expressões típicas de atribuição de fonte no texto.
padrao_fontes = re.compile(
    r'\bsegundo\b|\bde acordo com\b|\bconforme\b|\bdisse\b|\bafirmou\b|'
    r'\bdeclarou\b|\brevelou\b|\binformou\b|\baponta\b|\baponta que\b',
    flags=re.IGNORECASE
)
df_final['num_fontes_citadas_temp'] = df['texto'].apply(lambda t: len(padrao_fontes.findall(str(t))))
df_final['fontes_proporcao'] = proporcao(df_final['num_fontes_citadas_temp'])


# --- 3.4 e 3.5 Número de estudos prévios citados (bruto e proporção) ---
# Proxy: procura menções a estudo/pesquisa/universidade/instituto/revista científica.
padrao_estudos = re.compile(
    r'\bestudo[s]?\b|\bpesquisa[s]?\b|\bpesquisador(es)?\b|\bcientista[s]?\b|'
    r'\buniversidade\b|\binstituto\b|\brevista científica\b|\bpublicado(a)? n[ao]\b',
    flags=re.IGNORECASE
)
df_final['num_estudos_previos_temp'] = df['texto'].apply(lambda t: len(padrao_estudos.findall(str(t))))
df_final['estudos_previos_proporcao'] = proporcao(df_final['num_estudos_previos_temp'])


# --- 3.6 e 3.7 Palavras sensacionalistas (bruto e proporção) ---
# Lista de proxy: termos de apelo emocional/alarmista comuns em clickbait em português.
# Ajustem/completem esta lista conforme análise do corpus de vocês.
palavras_sensacionalistas = [
    'urgente', 'chocante', 'bomba', 'revelado', 'você não vai acreditar',
    'inacreditável', 'absurdo', 'escândalo', 'alerta', 'atenção',
    'exclusivo', 'impressionante', 'polêmica', 'espantoso', 'grave',
    'crime', 'ataque', 'perigo', 'alarmante', 'insano',
]
padrao_sensacionalista = re.compile(
    r'\b(' + '|'.join(palavras_sensacionalistas) + r')\b',
    flags=re.IGNORECASE
)
df_final['num_palavras_sensacionalistas_temp'] = df['texto'].apply(
    lambda t: len(padrao_sensacionalista.findall(str(t)))
)
df_final['sensacionalismo_proporcao'] = proporcao(df_final['num_palavras_sensacionalistas_temp'])


# --- 3.8 a 3.14 Atributos gramaticais, em proporção ---
df_final['verbos_proporcao'] = proporcao(df['num_verbos'])
df_final['verbos_subj_imp_proporcao'] = proporcao(df['verbos_subj_imp'])
df_final['substantivos_proporcao'] = proporcao(df['num_substantivos'])
df_final['adjetivos_proporcao'] = proporcao(df['num_adjetivos'])
df_final['adverbios_proporcao'] = proporcao(df['num_adverbios'])
df_final['modais_proporcao'] = proporcao(df['verbos_modais'])
df_final['pronomes_proporcao'] = proporcao(df['num_pronomes'])

print("Bloco 3 (proporções) concluído.")


# ============================================
# BLOCO 4 — ÍNDICE DE LEGIBILIDADE (ILF)
# Fórmula: Flesch adaptado ao português (Martins et al., 1996)
# ILF = 248.835 - 1.015*(palavras/frases) - 84.6*(sílabas/palavras)
# ============================================

VOGAIS = 'aeiouáéíóúâêîôûãõàèìòù'

def contar_silabas_palavra(palavra):
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

def contar_silabas_texto(texto):
    palavras = re.findall(r'[a-záéíóúâêîôûãõàèìòüçA-ZÁÉÍÓÚÂÊÎÔÛÃÕÀÈÌÒÜÇ]+', str(texto))
    if not palavras:
        return 0
    return sum(contar_silabas_palavra(p) for p in palavras)

def calcular_ilf(row):
    num_palavras = row['num_palavras']
    tamanho_medio_frase = row['tamanho_medio_frase']  # palavras por frase, já vem do corpus
    if num_palavras == 0 or tamanho_medio_frase == 0:
        return None

    total_silabas = contar_silabas_texto(row['texto'])
    silabas_por_palavra = total_silabas / num_palavras

    ilf = 248.835 - (1.015 * tamanho_medio_frase) - (84.6 * silabas_por_palavra)
    return ilf

print("Calculando índice de legibilidade (pode levar alguns segundos)...")
df_final['indice_legibilidade'] = df.assign(
    tamanho_medio_frase=df['tam_medio_frase']
).apply(calcular_ilf, axis=1)

print("Bloco 4 concluído: índice de legibilidade calculado.")


# ============================================
# BLOCO 5 — REDUZIR PRECISÃO DAS COLUNAS NUMÉRICAS
# Converte para float32 e arredonda para 4 casas decimais,
# eliminando ruído de ponto flutuante nas colunas calculadas.
# ============================================
colunas_float = df_final.select_dtypes(include=['float64']).columns
df_final[colunas_float] = df_final[colunas_float].astype('float32').round(4)

print(f"Bloco 5 concluído: {len(colunas_float)} colunas numéricas convertidas para float32, 4 casas decimais.")


# ============================================
# BLOCO 6 — REMOVER COLUNAS DE CONTAGEM BRUTA AUXILIARES
# Mantém apenas as proporções finais, descarta os contadores intermediários.
# ============================================
df_final = df_final.drop(columns=[
    'num_fontes_citadas_temp',
    'num_estudos_previos_temp',
    'num_palavras_sensacionalistas_temp',
])

print("Bloco 6 concluído: colunas de contagem bruta removidas — mantidas apenas as proporções.")


# ============================================
# BLOCO 7 — REORDENAR COLUNAS NA ORDEM DEFINIDA PELO GRUPO
# ============================================
ordem_final = [
    'texto',                        # Texto da Notícia
    'link',                         # Link
    'categoria',                    # Categoria
    'diversidade_lexica',           # Diversidade Léxica
    'tamanho_medio_palavra',        # Tamanho Médio
    'data_publicacao',              # Data de Publicação
    'num_tokens',                   # Número de Tokens
    'num_palavras',                 # Número de Palavras
    'pct_erro_ortografico',         # Porcentagem de erro ortográfico
    'types_proporcao',              # Média de Types
    'fontes_proporcao',             # Média de fontes
    'estudos_previos_proporcao',    # Média de estudos prévios
    'emotividade',                  # Emotividade
    'sensacionalismo_proporcao',    # Média de palavras sensacionalistas
    'verbos_proporcao',             # Média de verbos
    'verbos_subj_imp_proporcao',    # Média de Verbos subjuntivo Imperativo
    'substantivos_proporcao',       # Média de Substantivos
    'adjetivos_proporcao',          # Média de Adjetivos
    'adverbios_proporcao',          # Média de Advérbios
    'modais_proporcao',             # Média de Modais
    'pronomes_proporcao',           # Média de Pronomes
    'pausalidade',                  # Pausalidade
    'indice_legibilidade',          # Índice de Legibilidade
    'tamanho_medio_frase',          # Tamanho Médio Frase
    'rotulo',                       # Rótulo
]

df_final = df_final[ordem_final]

print("Bloco 7 concluído: colunas reordenadas conforme definição do grupo.")


# ============================================
# CHECAGEM FINAL
# ============================================
print(f"\nDataset final: {df_final.shape[0]} linhas, {df_final.shape[1]} colunas")
print(f"Colunas: {list(df_final.columns)}")

print("\n--- Verificação de dados faltantes ---")
print(df_final.isnull().sum()[df_final.isnull().sum() > 0])

print("\n--- Amostra das novas colunas calculadas ---")
colunas_novas = [
    'types_proporcao', 'fontes_proporcao',
    'estudos_previos_proporcao',
    'sensacionalismo_proporcao',
    'verbos_proporcao', 'verbos_subj_imp_proporcao',
    'substantivos_proporcao', 'adjetivos_proporcao',
    'adverbios_proporcao', 'modais_proporcao',
    'pronomes_proporcao', 'indice_legibilidade'
]
print(df_final[colunas_novas].describe())

# ============================================
# SALVAR
# ============================================
df_final.to_csv(caminho_saida, index=False)
print(f"\nDataset final salvo em:\n{caminho_saida}")
