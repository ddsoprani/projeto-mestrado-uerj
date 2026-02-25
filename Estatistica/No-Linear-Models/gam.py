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

#print("Dimensao final:", painel.shape)
#print(painel.head(5))

# garantir que latitude/longitude sejam numéricas
painel['latitude'] = painel['latitude'].str.replace(',', '.').astype(float)
painel['longitude'] = painel['longitude'].str.replace(',', '.').astype(float)

# Agregação anual
painel_anual = (
    painel
    .groupby(['municipio', 'ano', 'latitude', 'longitude'])
    .agg({
        'temp_media': 'mean',
        'precipitacao': 'sum',
        'vento': 'mean',
        'umidade': 'mean',
        'pressao': 'mean',
        'area_desmat': 'first',
        'area_florestal': 'first'
    })
    .reset_index()
)

#print("Dimensao final:", painel_anual.shape);
print(painel_anual.head(5));
exit();

#print(painel_anual[['area_florestal','area_desmat']].corr());





########################  Modelo para Temperatura: #######################


from pygam import LinearGAM, s
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

X = painel_anual[['area_florestal', 'area_desmat']].values
y = painel_anual['temp_media'].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

gam_temp = LinearGAM(s(0) + s(1))

gam_temp.fit(X_train, y_train)

y_pred = gam_temp.predict(X_test)

print("R²:", r2_score(y_test, y_pred))

#print(painel_anual['area_florestal'].describe());

import matplotlib.pyplot as plt
#plt.hist(painel_anual['area_florestal'], bins=30)
#plt.show()


#plt.hist(painel_anual['area_desmat'], bins=30)
#plt.show()

#exit();


import matplotlib.pyplot as plt

'''for i, feature in enumerate(['area_florestal', 'area_desmat']):
    XX = gam_temp.generate_X_grid(term=i)
    plt.figure()
    plt.plot(XX[:, i], gam_temp.partial_dependence(term=i, X=XX))
    plt.title(f'Efeito de {feature} na Temperatura')
    plt.xlabel(feature)
    plt.ylabel('Efeito parcial')
    plt.show()'''



# Adiciona coordenadas ao modelo:
from pygam import LinearGAM, s, te

X = painel_anual[['area_florestal','area_desmat','latitude','longitude']].values
y = painel_anual['temp_media'].values

gam_temp_spatial = LinearGAM(
    s(0, n_splines=6) +
    s(1, n_splines=6) +
    te(2,3)
)

gam_temp_spatial.fit(X, y)
print("Pseudo-R²:", gam_temp_spatial.statistics_['pseudo_r2'])


import matplotlib.pyplot as plt
features = ['area_florestal', 'area_desmat']

for i, feature in enumerate(features):
    XX = gam_temp_spatial.generate_X_grid(term=i)
    plt.figure()
    plt.plot(XX[:, i], gam_temp_spatial.partial_dependence(term=i, X=XX))
    plt.title(f'Efeito de {feature} na Temperatura (controlando espaço)')
    plt.xlabel(feature)
    plt.ylabel('Efeito parcial')
    plt.show()


# Adiciona o ano (GAM espacial + temporal):

# Matriz de regressoras
X = painel_anual[['area_florestal', 'area_desmat', 'latitude', 'longitude', 'ano']].values
y = painel_anual['temp_media'].values

# Modelo com espaco + tempo
'''gam_temp_full = LinearGAM(
    s(0) +          # floresta
    s(1) +          # desmatamento
    te(2, 3) +      # latitude + longitude (efeito espacial)
    s(4)            # ano (tendencia temporal)
).fit(X, y)'''

'''gam_temp_full = LinearGAM(
    s(0) +          # floresta
    s(1) +          # desmatamento
    te(2,3) +       # latitude + longitude (efeito espacial)
    s(4)            # ano (efeito temporal)
).gridsearch(X, y)'''

gam_temp_full = LinearGAM(
    s(0, n_splines=8) +
    s(1, n_splines=8) +
    te(2,3, n_splines=6) +
    s(4, n_splines=6)
).fit(X, y)


print(gam_temp_full.statistics_['pseudo_r2'])

'''XX = gam_temp_full.generate_X_grid(term=0)
plt.figure()
plt.plot(XX[:, 0], gam_temp_full.partial_dependence(term=0, X=XX))
plt.title('Efeito de Area Florestal (controlando espaço e tempo)')
plt.show()'''

nomes = ['Área Florestal', 'Desmatamento', 'Ano']

for i, nome in zip([0, 1], nomes):
    XX = gam_temp_full.generate_X_grid(term=i)
    pdep = gam_temp_full.partial_dependence(term=i, X=XX)

    plt.figure()
    plt.plot(XX[:, i], pdep)
    plt.title(f'Efeito parcial de {nome}')
    plt.xlabel(nome)
    plt.ylabel('Efeito parcial')
    plt.show()



term = 3

XX = gam_temp_full.generate_X_grid(term=term)
pdep = gam_temp_full.partial_dependence(term=term, X=XX)

plt.figure()
plt.plot(XX[:, -1], pdep)  # última coluna é ano
plt.show()
