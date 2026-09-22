"""
corrigir_rotulo_nan.py
------------------------
Corrige linhas de notícias verdadeiras que ficaram sem rótulo (rotulo = NaN
em vez de 1.0). Troca todo NaN em 'rotulo' por 1.0 e salva um dataset novo
(não mexe no arquivo original).

Uso:
    python corrigir_rotulo_nan.py entrada.csv saida.csv

Em Python:
    import pandas as pd
    from corrigir_rotulo_nan import corrigir_rotulo_nan

    df = pd.read_csv('meu_dataset.csv')
    df_corrigido = corrigir_rotulo_nan(df)
"""

import sys
import pandas as pd


def corrigir_rotulo_nan(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """Substitui rotulo == NaN por 1.0 (notícia verdadeira). Devolve uma
    cópia — não altera o df original."""
    df = df.copy()

    if 'rotulo' not in df.columns:
        raise ValueError(f"Não encontrei a coluna 'rotulo'. Colunas: {list(df.columns)[:10]}")

    n_nan = df['rotulo'].isna().sum()
    df.loc[df['rotulo'].isna(), 'rotulo'] = 1.0

    if verbose:
        print(f"Linhas com rotulo NaN corrigidas para 1.0: {n_nan}")
        print(df['rotulo'].value_counts(dropna=False))

    return df


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Uso: python corrigir_rotulo_nan.py entrada.csv saida.csv")
        sys.exit(1)

    caminho_entrada, caminho_saida = sys.argv[1], sys.argv[2]
    df_in = pd.read_csv(caminho_entrada)
    df_out = corrigir_rotulo_nan(df_in)
    df_out.to_csv(caminho_saida, index=False)
    print(f"Salvo em: {caminho_saida}")
