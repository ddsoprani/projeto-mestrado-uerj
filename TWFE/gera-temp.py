import pandas as pd
import os

caminho_base = "../ERA5/dados-climaticos/ES/"  # pasta principal

lista_dfs = []



for ano in os.listdir(caminho_base):

    caminho_ano = os.path.join(caminho_base, ano)

    if os.path.isdir(caminho_ano):

        arquivo = f"dados_climaticos_mensais_era5_municipios_ES_{ano}.csv"
        caminho_arquivo = os.path.join(caminho_ano, arquivo)

        if os.path.exists(caminho_arquivo):

            df = pd.read_csv(
                caminho_arquivo,
                sep=";",
                decimal=","
            )

            lista_dfs.append(df)


df_total = pd.concat(lista_dfs, ignore_index=True)

df_anual = (
    df_total
    .groupby(["municipio", "ano"], as_index=False)["temp_media_graus (C)"]
    .mean()
)


vetor = (
    df_anual
    .set_index(["municipio", "ano"])["temp_media_graus (C)"]
    .unstack()
    .to_dict(orient="index")
)

df_pivot = df_anual.pivot(
    index="municipio",
    columns="ano",
    values="temp_media_graus (C)"
)

df_pivot = df_pivot.sort_index(axis=1)
df_pivot = df_pivot.round(2)

df_pivot.to_csv("temperatura_media_anual_municipios-ES.csv")
