import pandas as pd
import glob
import re
import statsmodels.api as sm


# Carrega dados climaticos

# Caminho da pasta
caminho = "../dados_juntos_clima_desmat/dados_juntos_V5/Clima_V5/SP/*.csv"

lista_dfs = []

for arquivo in glob.glob(caminho):
    df = pd.read_csv(arquivo, sep=";")
    lista_dfs.append(df)

clima_es = pd.concat(lista_dfs, ignore_index=True)

# Ajustar virgula decimal
colunas_numericas = [
    "temp_media_graus (C)",
    "precipitacao_total (mm)",
    "vel. vento (m/s)",
    "umidade_ar (%)",
    "pressao_atm (hPa)"
]

for col in colunas_numericas:
    clima_es[col] = (
        clima_es[col]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

# 1 - Media anual por municipio
clima_municipal_anual = clima_es.groupby(
    ["municipio", "ano"]
).agg({
    "temp_media_graus (C)": "mean",
    "precipitacao_total (mm)": "mean",
    "vel. vento (m/s)": "mean",
    "umidade_ar (%)": "mean",
    "pressao_atm (hPa)": "mean"
}).reset_index()

# 2 - Media estadual anual
#clima_estadual_anual = clima_municipal_anual.groupby("ano").mean().reset_index()

clima_estadual_anual = clima_municipal_anual.groupby("ano").agg({
    "temp_media_graus (C)": "mean",
    "precipitacao_total (mm)": "mean",
    "vel. vento (m/s)": "mean",
    "umidade_ar (%)": "mean",
    "pressao_atm (hPa)": "mean"
}).reset_index()

'''print(clima_estadual_anual.head())
print();
print();
print();
print(clima_estadual_anual.dtypes)'''

#print(clima_estadual_anual.head(5));

#print();


# Carrega dados de uso de terra

df = pd.read_csv("../MapBiomas/desmatamento-final-SP-v5.csv", sep = ';', decimal = ',')

# ETAPA 1 - Transformar o banco para formato temporal
for col in df.columns[1:]:
    if df[col].dtype == "object":
        df[col] = df[col].str.replace(",", ".", regex=False).astype(float)

# Criar lista para armazenar dados reorganizados
dados = []

for col in df.columns:
    match = re.search(r'_(\d{4})$', col)
    if match:
        ano = int(match.group(1))
        
        if "Area_florestal" in col:
            tipo = "florestal"
        elif "Area_desmat" in col:
            tipo = "desmat"
        else:
            continue
        
        temp = df[["Municipio", col]].copy()
        temp["Ano"] = ano
        temp["Tipo"] = tipo
        temp.rename(columns={col: "Valor"}, inplace=True)
        dados.append(temp)

df_long = pd.concat(dados)

df_final = df_long.pivot_table(
    index=["Municipio", "Ano"],
    columns="Tipo",
    values="Valor"
).reset_index()


#ETAPA 2 - Criar media estadual por ano
estado = df_final.groupby("Ano")[["florestal", "desmat"]].sum().reset_index()


# ETAPA 3 - Visualizacao inicial

import matplotlib.pyplot as plt

estado = estado.sort_values("Ano")

estado = estado.rename(columns={"Ano": "ano"})
estado["var_acum_florestal"] = estado["florestal"] - estado["florestal"].iloc[0]
estado["var_acum_desmat"] = estado["desmat"] - estado["desmat"].iloc[0]

#print(estado.head(5));


# --------------------------------------------------------
# ----------------------- MERGE --------------------------
# --------------------------------------------------------


df = pd.merge(estado, clima_estadual_anual, on="ano")

# Passo 2 - Regressao: Temperatura ~ Floresta + Ano

X_temp = df[["florestal", "ano"]]
X_temp = sm.add_constant(X_temp)

y_temp = df["temp_media_graus (C)"]

modelo_temp = sm.OLS(y_temp, X_temp).fit()
#print(modelo_temp.summary())



# Passo 3 - Regressao: Precipitacao ~ Floresta + Ano

X_prec = df[["florestal", "ano"]]
X_prec = sm.add_constant(X_prec)

y_prec = df["precipitacao_total (mm)"]

modelo_prec = sm.OLS(y_prec, X_prec).fit()
#print(modelo_prec.summary())
#exit();



X = sm.add_constant(df["florestal"])
modelo = sm.OLS(y_temp, X).fit()
print(modelo.summary())


df["d_temp"] = df["temp_media_graus (C)"].diff()
df["d_floresta"] = df["florestal"].diff()
df_diff = df.dropna()
X = sm.add_constant(df_diff["d_floresta"])
y = df_diff["d_temp"]
modelo = sm.OLS(y, X).fit()
print(modelo.summary())
