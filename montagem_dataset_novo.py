import pandas as pd
from extracao_features import montar_dataset
from padronizar_normalizar import padronizar_dataframe

df_novas = pd.read_csv('noticias_novas.csv')       # precisa ter 'texto'
df_bruto_novas = montar_dataset(df_novas)
df_final_novas = padronizar_dataframe(df_bruto_novas)   # normaliza só entre elas

df_final_novas.to_csv('dataset_novas_normalizado.csv', index=False)