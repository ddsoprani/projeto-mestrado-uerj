'''import pandas as pd

# carregar dados
df = pd.read_csv("csv/desmatamento-final-ES-v5.csv", sep=";", decimal = ',')

# converter virgula decimal (IMPORTANTE no seu caso)
df = df.replace(",", ".", regex=True)

# transformar colunas em formato longo
df_long = pd.wide_to_long(
    df,
    stubnames=["Area_florestal", "Area_desmat_km2"],
    i="Municipio",
    j="Ano",
    sep="_",
    suffix="\d+"
).reset_index()

print(df_long.head())'''


import pandas as pd
import glob

# lista todos os arquivos CSV dentro da pasta
arquivos = glob.glob("csv/*.csv")

# lista para armazenar os dfs transformados
lista_dfs = []

for arquivo in arquivos:
    uf = '';
    if arquivo == "csv/desmatamento-final-SP-v5.csv":
        uf = 'SP';
    elif arquivo == "csv/desmatamento-final-RJ-v5.csv":
        uf = 'RJ'
    else:
        uf = 'ES';

    df = pd.read_csv(arquivo, sep=";", decimal=",")
    df["Municipio"] = df["Municipio"] + "-" + uf

    # corrigir virgula decimal
    for col in df.columns:
        if col != "Municipio":
            df[col] = df[col].astype(str).str.replace(",", ".").astype(float)

    # transformar para formato longo
    df_long = pd.wide_to_long(
        df,
        stubnames=["Area_florestal", "Area_desmat_km2"],
        i="Municipio",
        j="Ano",
        sep="_",
        suffix="\d+"
    ).reset_index()

    lista_dfs.append(df_long)

# juntar tudo em um unico dataframe
df_long = pd.concat(lista_dfs, ignore_index=True)

# ordenar por Municipio e Ano
df_long = df_long.sort_values(by=["Municipio", "Ano"])

print(df_long.head());
print(df_long.tail());

#df_long.to_csv("desmatamento_unido.csv");




# ==================== DADOS CLIMATICOS ======================

#Ler TODOS os arquivos climaticos + adicionar UF

import pandas as pd
import glob
import os

caminho_base = "/home/danilo/Projeto-Mestrado/dados_juntos_clima_desmat/dados_juntos_V5/Clima_V5/"

lista_clima = []

# percorre as pastas (ES, RJ, SP)
for uf in os.listdir(caminho_base):
    caminho_uf = os.path.join(caminho_base, uf)

    if os.path.isdir(caminho_uf):
        arquivos = glob.glob(os.path.join(caminho_uf, "*.csv"))

        for arquivo in arquivos:
            df = pd.read_csv(arquivo, sep=";", decimal=",")

            # padronizar nome das colunas
            df = df.rename(columns={
                "municipio": "Municipio",
                "ano": "Ano"
            })

            # corrigir virgula decimal
            for col in df.columns:
                if col not in ["Municipio", "valid_time"]:
                    df[col] = df[col].astype(str).str.replace(",", ".").astype(float)

            # adicionar UF ao municipio
            df["Municipio"] = df["Municipio"].str.strip() + "-" + uf

            lista_clima.append(df)

# juntar tudo
df_clima = pd.concat(lista_clima, ignore_index=True)

print(df_clima.head());

#df_clima.to_csv("dados_climaticos.csv");


# ============================== MERGE ===============================

df_final = pd.merge(
    df_long,   # desmat anual
    df_clima,  # dados mensais
    on=["Municipio", "Ano"],
    how="left"
)

print("Duplicados: ", df_clima.duplicated(subset=["Municipio", "Ano", "mes"]).sum());

df_final = df_final.sort_values(
    by=["Municipio", "Ano", "mes"]
).reset_index(drop=True)

#df_final = df_final[df_final["Municipio"] != "São João de Meriti-RJ"]


print(df_final.head(20));
print(df_final.tail());

df_final.to_csv("painel_final_clima_desmat.csv", sep=";", decimal=",");
