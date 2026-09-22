"""
padronizar_normalizar.py
--------------------------
Extensão do padronizacao.py original.

O padronizacao.py que já existia só convertia colunas numéricas para
float32/float64 (sem alterar a escala dos valores). O pedido agora é
"normalizar de 0 a 1 e deixar o dataset em float32" — ou seja, além do
cast de tipo, é preciso um min-max scaling por coluna:

    valor_normalizado = (valor - min_da_coluna) / (max_da_coluna - min_da_coluna)

A coluna 'rotulo' (binária, 0/1) é apenas convertida para float32, sem
normalização (min-max não faria diferença nela).

Duas formas de usar (ambas via padronizar_dataframe, que trabalha em
memória, sem precisar salvar nada em disco):

  1. Só as notícias novas: normaliza usando o min/max só delas.
  2. Notícias novas + dataset antigo concatenados: normaliza usando o
     min/max do conjunto combinado (mais consistente se depois for treinar/
     comparar tudo junto) — nesse caso o "antigo" tem que ser a versão
     BRUTA (antes da normalização), senão os valores ficam normalizados
     duas vezes e o resultado não faz sentido.

Uso via terminal (mantido por compatibilidade, só normaliza um arquivo):
    python padronizar_normalizar.py caminho/dataset_bruto.csv caminho/saida.csv
"""

import sys
import os
import pandas as pd
import numpy as np

# Coluna que já é 0/1 por natureza — não normalizar
COLUNAS_BINARIAS_EXATAS = {'rotulo'}


def _eh_binaria(col: str) -> bool:
    return col in COLUNAS_BINARIAS_EXATAS


def normalizar_min_max(df: pd.DataFrame, colunas=None) -> pd.DataFrame:
    """Aplica min-max scaling (0 a 1) nas colunas numéricas informadas
    (ou em todas as numéricas não-binárias, se colunas=None)."""
    df = df.copy()
    if colunas is None:
        colunas = [c for c in df.select_dtypes(include=[np.number]).columns
                   if not _eh_binaria(c)]

    for col in colunas:
        minimo = df[col].min()
        maximo = df[col].max()
        amplitude = maximo - minimo
        if amplitude == 0 or pd.isna(amplitude):
            df[col] = 0.0
        else:
            df[col] = (df[col] - minimo) / amplitude

    return df


def padronizar_dataframe(df: pd.DataFrame, normalizar: bool = True,
                          verbose: bool = True) -> pd.DataFrame:
    """Versão em memória (sem precisar salvar/ler arquivo): normaliza (0 a 1)
    e converte pra float32. Serve tanto pra um DataFrame só de notícias
    novas quanto pra um já concatenado (novas + antigo bruto) — o min/max
    usado é sempre o do DataFrame que for passado aqui."""
    colunas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    if not colunas_numericas:
        raise ValueError("Nenhuma coluna numérica encontrada no dataset.")

    if verbose:
        print(f"Colunas numéricas identificadas ({len(colunas_numericas)}):")
        for c in colunas_numericas:
            marcador = " (binária, sem normalização)" if _eh_binaria(c) else ""
            print(f"  - {c}{marcador}")

    df_proc = normalizar_min_max(df) if normalizar else df.copy()

    df_f32 = df_proc.copy()
    for col in colunas_numericas:
        df_f32[col] = df_f32[col].astype(np.float32)

    return df_f32


def padronizar_dataset(caminho_csv: str, pasta_saida: str = ".",
                        normalizar: bool = True) -> pd.DataFrame:
    """Versão em arquivo (lê um CSV, normaliza, salva outro CSV) — mantida
    por compatibilidade com quem já usava assim."""
    df = pd.read_csv(caminho_csv)
    df_f32 = padronizar_dataframe(df, normalizar=normalizar)

    base_nome = os.path.splitext(os.path.basename(caminho_csv))[0]
    sufixo = "_normalizado_float32" if normalizar else "_float32"
    caminho_f32 = os.path.join(pasta_saida, f"{base_nome}{sufixo}.csv")
    df_f32.to_csv(caminho_f32, index=False, float_format="%.6g")

    print(f"\nArquivo salvo em: {caminho_f32}")
    return df_f32


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python padronizar_normalizar.py caminho/dataset.csv [pasta_saida]")
        sys.exit(1)

    caminho_entrada = sys.argv[1]
    pasta_destino = sys.argv[2] if len(sys.argv) > 2 else "."

    padronizar_dataset(caminho_entrada, pasta_destino)
