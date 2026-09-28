"""
montagem_dataset_novo.py
-------------------------
Monta um dataset do zero a partir de um CSV de notícias novas, SEM juntar
com nenhum dataset antigo.

Passo a passo:
  1. Lê o CSV de notícias novas (precisa ter a coluna 'texto'; 'rotulo' ou
     'label' são opcionais e são mantidos se existirem).
  2. Extrai as features de cada texto (extracao_features.montar_dataset).
  3. Normaliza (0 a 1) e converte para float32
     (extracao_features.padronizar_dataframe).

A normalização usa o min/max só dessas notícias, então o resultado NÃO fica
na mesma escala de outro dataset normalizado separadamente. Para juntar as
notícias novas com um dataset antigo, use concatenacao_dataset.py.

Uso via linha de comando (os dois caminhos são opcionais):
    python montagem_dataset_novo.py [noticias_novas.csv] [saida.csv]

Padrões: noticias_novas.csv e dataset_novas_normalizado.csv.
"""

import sys

import pandas as pd

from extracao_features import montar_dataset, padronizar_dataframe


if __name__ == '__main__':
    args = sys.argv[1:]
    caminho_novas = args[0] if len(args) > 0 else 'noticias_novas.csv'
    caminho_saida = args[1] if len(args) > 1 else 'dataset_novas_normalizado.csv'

    df_novas = pd.read_csv(caminho_novas)                  # precisa ter 'texto'
    df_bruto_novas = montar_dataset(df_novas)
    df_final_novas = padronizar_dataframe(df_bruto_novas)  # normaliza só entre elas

    df_final_novas.to_csv(caminho_saida, index=False)
    print(f"Salvo em: {caminho_saida}")
