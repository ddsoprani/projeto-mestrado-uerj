from linearmodels.panel import PanelOLS
import pandas as pd
import re
import os


# MONTANDO O PAINEL DE USO DA TERRA

# carregar uso da terra
uso = pd.read_csv("../../dados_juntos_clima_desmat/dados_juntos_V5/Uso_da_terra_V5/CSV-ES/desmatamento-final-ES-v5.csv", sep=";", decimal = ',');

# padronizar nome
uso = uso.rename(columns={"Municipio": "municipio"})

# derreter (melt) todas as colunas exceto municipio
uso_long = uso.melt(id_vars="municipio", var_name="variavel_ano", value_name="valor")


uso_long["ano"] = uso_long["variavel_ano"].str.extract(r"(\d{4})$").astype(int)
uso_long["tipo"] = uso_long["variavel_ano"].str.replace(r"_\d{4}$", "", regex=True)

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

# Ler todos os arquivos de clima
pasta_clima = "../../dados_juntos_clima_desmat/dados_juntos_V5/Clima_V5/ES/"

arquivos = [f for f in os.listdir(pasta_clima) if f.endswith(".csv")]

lista = []

for arq in arquivos:
    df = pd.read_csv(os.path.join(pasta_clima, arq), sep=";")
    lista.append(df)

clima = pd.concat(lista, ignore_index=True)

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

# garantir que latitude/longitude sejam numéricas
painel['latitude'] = painel['latitude'].str.replace(',', '.').astype(float)
painel['longitude'] = painel['longitude'].str.replace(',', '.').astype(float)


painel['data'] = pd.to_datetime(painel['ano'].astype(str) + '-' + painel['mes'].astype(str).str.zfill(2) + '-01')
painel = painel.set_index(['municipio', 'data'])


############### Etapa 1 - Modelo Dinamico com Termo Quadratico ################

# Criar termo quadratico
painel['desmat2'] = painel['area_desmat']**2

# Garantir que temp_lag1 ja existe
painel['temp_lag1'] = painel.groupby(level=0)['temp_media'].shift(1)

painel_nl = painel.dropna(subset=['temp_lag1','desmat2'])

from linearmodels.panel import PanelOLS
import statsmodels.api as sm

y = painel_nl['temp_media']
X = sm.add_constant(painel_nl[['temp_lag1','area_desmat','desmat2']])

modelo_nl = PanelOLS(
    y,
    X,
    entity_effects=True,
    time_effects=True
).fit(cov_type='clustered', cluster_entity=True)

print(modelo_nl.summary);


print(painel['area_desmat'].describe(percentiles=[0.90, 0.95, 0.99]));


# Grafico

import numpy as np
import matplotlib.pyplot as plt

# Coeficientes do modelo
beta1 = 0.0043
beta2 = -4.921e-05

# Criar faixa de desmatamento (0 até máximo observado)
desmat_range = np.linspace(0, painel['area_desmat'].max(), 200)

# Efeito marginal
efeito_marginal = beta1 + 2*beta2*desmat_range

# Plot
plt.figure(figsize=(8,5))
plt.plot(desmat_range, efeito_marginal, color='blue', lw=2)
plt.axhline(0, color='black', linestyle='--')
plt.axvline(44, color='red', linestyle='--', label='Ponto de virada teórico')
plt.scatter(painel['area_desmat'], np.zeros_like(painel['area_desmat']),
            alpha=0.05, color='grey', label='Observações')
plt.xlabel('Área de desmatamento (km²)')
plt.ylabel('Efeito marginal sobre Temp (°C)')
plt.title('Efeito marginal do desmatamento sobre temperatura')
plt.legend()
plt.grid(True)
plt.show()
