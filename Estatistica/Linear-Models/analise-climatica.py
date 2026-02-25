import pandas as pd
import glob

# Caminho da pasta
caminho = "../dados_juntos_clima_desmat/dados_juntos_V5/Clima_V5/ES/*.csv"

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

print(clima_estadual_anual.head(5));
exit();

# Tendencia de temperatura:


import statsmodels.api as sm

X = sm.add_constant(clima_estadual_anual["ano"])
y = clima_estadual_anual["temp_media_graus (C)"]

modelo_temp = sm.OLS(y, X).fit()
print(modelo_temp.summary());


#Tendencia de precipitacao:
y_prec = clima_estadual_anual["precipitacao_total (mm)"]

modelo_prec = sm.OLS(y_prec, X).fit()
print(modelo_prec.summary())
