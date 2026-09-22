"""
reduzir_para_texto_rotulo.py
-------------------------------
Recebe um dataset "bruto" que já tem várias colunas de feature prontas
(por exemplo o formato do dataset_antigo_bruto.csv, ou qualquer CSV com
'texto', 'rotulo' e outras colunas) e devolve só 'texto' + 'rotulo'.

Serve pra preparar um dataset antigo (já processado com outra metodologia)
pra ser RE-processado do zero pelo nosso pipeline (extracao_features.py) —
assim os dois lados (antigo + notícias novas) ficam calculados com a mesma
metodologia antes de concatenar e normalizar.

Uso:
    python reduzir_para_texto_rotulo.py entrada.csv saida.csv

Em Python:
    import pandas as pd
    from reduzir_para_texto_rotulo import reduzir_para_texto_rotulo

    df = pd.read_csv('dataset_bruto_antigo.csv')
    df_reduzido = reduzir_para_texto_rotulo(df)
    # df_reduzido já pode ir direto pro extracao_features.montar_dataset()
"""

import sys
import pandas as pd


def reduzir_para_texto_rotulo(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """Mantém só as colunas 'texto' e 'rotulo' (se existir), descartando
    todas as outras (features já calculadas, link, categoria, etc.)."""
    df = df.copy()
    df.columns = df.columns.str.strip()
    df = df.rename(columns={
        c: 'texto' for c in df.columns if c.lower() == 'texto' and c != 'texto'
    })
    df = df.rename(columns={
        c: 'rotulo' for c in df.columns if c.lower() == 'rotulo' and c != 'rotulo'
    })

    if 'texto' not in df.columns:
        raise ValueError(f"Não encontrei a coluna 'texto'. Colunas: {list(df.columns)[:10]}")

    colunas = ['texto'] + (['rotulo'] if 'rotulo' in df.columns else [])
    df_reduzido = df[colunas].copy()

    if verbose:
        print(f"Dataset reduzido: {df_reduzido.shape[0]} linhas, colunas {list(df_reduzido.columns)}")

    return df_reduzido


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Uso: python reduzir_para_texto_rotulo.py entrada.csv saida.csv")
        sys.exit(1)

    caminho_entrada, caminho_saida = sys.argv[1], sys.argv[2]
    df_in = pd.read_csv(caminho_entrada)
    df_out = reduzir_para_texto_rotulo(df_in)
    df_out.to_csv(caminho_saida, index=False)
    print(f"Salvo em: {caminho_saida}")
