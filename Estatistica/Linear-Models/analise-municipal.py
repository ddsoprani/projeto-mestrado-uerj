import pandas as pd
import re


# MONTANDO O PAINEL DE USO DA TERRA

# carregar uso da terra
uso = pd.read_csv("../dados_juntos_clima_desmat/dados_juntos_V5/Uso_da_terra_V5/CSV-SP/desmatamento-final-SP-v5.csv", sep=";", decimal = ',');

# padronizar nome
uso = uso.rename(columns={"Municipio": "municipio"})

# derreter (melt) todas as colunas exceto municipio
uso_long = uso.melt(id_vars="municipio", var_name="variavel_ano", value_name="valor")


uso_long["ano"] = uso_long["variavel_ano"].str.extract(r"(\d{4})$").astype(int)
#print(uso_long[["variavel_ano","ano"]].head())

uso_long["tipo"] = uso_long["variavel_ano"].str.replace(r"_\d{4}$", "", regex=True)
#print(uso_long["tipo"].unique())

uso_painel = uso_long.pivot_table(
    index=["municipio", "ano"],
    columns="tipo",
    values="valor"
).reset_index()

uso_painel.columns.name = None


uso_painel = uso_painel.rename(columns={
    "Area_florestal": "area_florestal",
    "Area_desmat_km2": "area_desmat"
})


# MONTANDO O PAINEL CLIMATICO

import os
import pandas as pd

# Ler todos os arquivos de clima

pasta_clima = "../dados_juntos_clima_desmat/dados_juntos_V5/Clima_V5/SP/"

arquivos = [f for f in os.listdir(pasta_clima) if f.endswith(".csv")]

lista = []

for arq in arquivos:
    df = pd.read_csv(os.path.join(pasta_clima, arq), sep=";")
    lista.append(df)

clima = pd.concat(lista, ignore_index=True)

#print(clima.shape)
#print(clima.head())

# Padronizar nomes
clima.columns = clima.columns.str.strip()

clima = clima.rename(columns={
    "temp_media_graus (C)": "temp_media",
    "precipitacao_total (mm)": "precipitacao",
    "vel. vento (m/s)": "vento",
    "umidade_ar (%)": "umidade",
    "pressao_atm (hPa)": "pressao"
})


#Converter para numerico (caso necessario)
cols_numericas = ["temp_media", "precipitacao", "vento", "umidade", "pressao"]

for col in cols_numericas:
    clima[col] = (
        clima[col]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

#Garantir tipos corretos
clima["ano"] = clima["ano"].astype(int)
clima["mes"] = clima["mes"].astype(int)


#FAZER O MERGE (momento critico):

painel = pd.merge(
    clima,
    uso_painel,
    on=["municipio", "ano"],
    how="inner"
)

#print("Dimensao final:", painel.shape)
#print(painel.head())

#print(painel["municipio"].nunique())
#print(painel["ano"].min(), painel["ano"].max())


# ---------------------------------------------------------------------------------------

#PRIMEIRO MODELO: regressao simples (sem efeitos fixos)
import statsmodels.formula.api as smf

modelo_simples = smf.ols(
    "temp_media ~ area_florestal",
    data=painel
).fit()

print();
print();
print("Primeiro modelo: regressao simples:");
print();
print(modelo_simples.summary());

print();
print();
print();


# SEGUNDO MODELO: controlar por tendencia temporal
painel["tendencia"] = painel["ano"] - painel["ano"].min()

modelo_tend = smf.ols(
    "temp_media ~ area_florestal + tendencia",
    data=painel
).fit()

print();
print();
print("Segundo modelo: controlar por tendencia temporal:");
print();
print(modelo_tend.summary());


# O MODELO MAIS IMPORTANTE (efeitos fixos municipais):

modelo_fe = smf.ols(
    "temp_media ~ area_florestal + tendencia + C(mes) + C(municipio)",
    data=painel
).fit()

print();
print();
print("Terceiro modelo: efeitos fixos municipais:");
print();
print(modelo_fe.summary());


# Modelo completo:
modelo_fe_completo = smf.ols(
    "temp_media ~ area_florestal + C(municipio) + C(ano) + C(mes)",
    data=painel
).fit()

print();
print();
print("Modelo completo:");
print();
print();
print(modelo_fe_completo.summary())
print();
print();

