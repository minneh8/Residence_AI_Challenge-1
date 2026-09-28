"""
concatenacao_dataset.py
------------------------
Junta DOIS datasets em um só: um dataset antigo (já com as features em
escala bruta) + um CSV de notícias novas (só com 'texto' e, opcionalmente,
'rotulo'). O resultado é um único dataset normalizado (0 a 1, float32).

Passo a passo:
  1. Extrai as features das notícias novas (extracao_features.montar_dataset),
     ainda em escala bruta.
  2. Lê o dataset antigo, que TAMBÉM precisa estar em escala bruta.
  3. Concatena os dois (antigo em cima, novas embaixo).
  4. Normaliza o conjunto combinado (extracao_features.padronizar_dataframe),
     usando o min/max de TODAS as linhas — assim antigo e novo ficam na
     mesma escala.

Aviso — o dataset antigo tem que ser a versão BRUTA (antes da
normalização). Se ele já estiver normalizado, os valores dele ficam
normalizados duas vezes e o resultado não faz sentido. Se o antigo foi
calculado com outra metodologia, o ideal é reduzi-lo a 'texto' + 'rotulo'
(reducao_dataset.py) e reprocessá-lo com extracao_features.py --bruto antes
de usar aqui.

Uso via linha de comando (os três caminhos são opcionais):
    python concatenacao_dataset.py [noticias_novas.csv] [dataset_bruto_antigo.csv] [saida.csv]

Padrões: noticias_novas.csv, dataset_bruto_antigo.csv e
dataset_combinado_normalizado.csv.

Uso em Python:
    import pandas as pd
    from concatenacao_dataset import concatenar_datasets

    df_final = concatenar_datasets(pd.read_csv('noticias_novas.csv'),
                                   pd.read_csv('dataset_bruto_antigo.csv'))
"""

import sys

import pandas as pd

from extracao_features import montar_dataset, padronizar_dataframe


def concatenar_datasets(df_novas: pd.DataFrame, df_bruto_antigo: pd.DataFrame) -> pd.DataFrame:
    """Extrai as features de df_novas (precisa ter 'texto'), junta com
    df_bruto_antigo (features em escala bruta) e normaliza o conjunto
    combinado. Devolve o dataset final (0 a 1, float32)."""
    df_bruto_novas = montar_dataset(df_novas)

    df_combinado_bruto = pd.concat([df_bruto_antigo, df_bruto_novas], ignore_index=True)
    return padronizar_dataframe(df_combinado_bruto)  # min/max do conjunto todo


if __name__ == '__main__':
    args = sys.argv[1:]
    caminho_novas = args[0] if len(args) > 0 else 'noticias_novas.csv'
    caminho_antigo = args[1] if len(args) > 1 else 'dataset_bruto_antigo.csv'
    caminho_saida = args[2] if len(args) > 2 else 'dataset_combinado_normalizado.csv'

    df_final_combinado = concatenar_datasets(pd.read_csv(caminho_novas),
                                             pd.read_csv(caminho_antigo))
    df_final_combinado.to_csv(caminho_saida, index=False)
    print(f"Salvo em: {caminho_saida}")
