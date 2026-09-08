"""
Script de padronização numérica do dataset_duat_final.csv
-----------------------------------------------------------
Converte as colunas numéricas do dataset para dois formatos de precisão:

  - float32 -> precisão de ~6 dígitos significativos (padrão IEEE 754 single)
  - float64 -> precisão de ~16 dígitos significativos (padrão IEEE 754 double)

Colunas não-numéricas (texto, link, fonte, categoria, data_publicacao) são
mantidas inalteradas em ambos os arquivos de saída.

Uso:
    python padronizar_float.py caminho/para/dataset_duat_final.csv

Saídas geradas na mesma pasta do script:
    dataset_duat_final_float32.csv
    dataset_duat_final_float64.csv
"""

import sys
import os
import pandas as pd
import numpy as np


def padronizar_dataset(caminho_csv: str, pasta_saida: str = ".") -> None:
    # 1. Carrega o dataset original
    df = pd.read_csv(caminho_csv)

    # 2. Identifica automaticamente as colunas numéricas (int e float)
    colunas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()

    if not colunas_numericas:
        raise ValueError("Nenhuma coluna numérica encontrada no dataset.")

    print(f"Colunas numéricas identificadas ({len(colunas_numericas)}):")
    for c in colunas_numericas:
        print(f"  - {c}")

    # ------------------------------------------------------------------
    # Versão FLOAT32 (~6 dígitos significativos)
    # ------------------------------------------------------------------
    df_f32 = df.copy()
    for col in colunas_numericas:
        # Converte para float32 (arredonda naturalmente para a precisão do tipo)
        valores_f32 = df_f32[col].astype(np.float32)
        df_f32[col] = valores_f32

    # ------------------------------------------------------------------
    # Versão FLOAT64 (~16 dígitos significativos)
    # ------------------------------------------------------------------
    df_f64 = df.copy()
    for col in colunas_numericas:
        df_f64[col] = df_f64[col].astype(np.float64)

    # 3. Salva os arquivos de saída
    base_nome = os.path.splitext(os.path.basename(caminho_csv))[0]

    caminho_f32 = os.path.join(pasta_saida, f"{base_nome}_float32.csv")
    caminho_f64 = os.path.join(pasta_saida, f"{base_nome}_float64.csv")

    # Ao salvar em CSV, especificamos o número de dígitos para preservar
    # a precisão pretendida de cada tipo (float32 ~ 6 dígitos, float64 ~ 16 dígitos)
    df_f32.to_csv(caminho_f32, index=False, float_format="%.6g")
    df_f64.to_csv(caminho_f64, index=False, float_format="%.16g")

    print(f"\nArquivo float32 salvo em: {caminho_f32}")
    print(f"Arquivo float64 salvo em: {caminho_f64}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python padronizar_float.py caminho/para/dataset_duat_final.csv [pasta_saida]")
        sys.exit(1)

    caminho_entrada = sys.argv[1]
    pasta_destino = sys.argv[2] if len(sys.argv) > 2 else "."

    padronizar_dataset(caminho_entrada, pasta_destino)