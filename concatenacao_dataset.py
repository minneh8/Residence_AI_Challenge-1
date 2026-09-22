import pandas as pd
from extracao_features import montar_dataset
from padronizar_normalizar import padronizar_dataframe

df_novas = pd.read_csv('noticias_novas.csv')
df_bruto_novas = montar_dataset(df_novas)

df_bruto_antigo = pd.read_csv('dataset_bruto_antigo.csv')   # ver aviso abaixo

df_combinado_bruto = pd.concat([df_bruto_antigo, df_bruto_novas], ignore_index=True)
df_final_combinado = padronizar_dataframe(df_combinado_bruto)  # min/max do conjunto todo

df_final_combinado.to_csv('dataset_combinado_normalizado.csv', index=False)