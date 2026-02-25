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

#print("Dimensao final:", painel.shape)
#print(painel.head(5))

#print(painel.groupby('municipio')['area_desmat'].std().describe());

#print();

#print(painel.groupby('municipio')['area_florestal'].std().describe());

#exit();

from linearmodels.panel import PanelOLS
import statsmodels.api as sm

# Criar identificador ano-mês
#painel['ano_mes'] = painel['ano'].astype(str) + '-' + painel['mes'].astype(str).str.zfill(2)
painel['data'] = pd.to_datetime(painel['ano'].astype(str) + '-' + painel['mes'].astype(str).str.zfill(2) + '-01')

# Definir indice de painel
painel = painel.set_index(['municipio', 'data'])
#print(painel.head(5));
#exit();


# MODELO 1 - So desmatamento:
def model_1(painel):
    y = painel['temp_media']

    X1 = painel[['area_desmat']]
    X1 = sm.add_constant(X1)

    modelo1 = PanelOLS(
        y,
        X1,
        entity_effects=True,
        time_effects=True
    )

    resultado1 = modelo1.fit(cov_type='clustered', cluster_entity=True)
    print(resultado1.summary)


# MODELO 2 - So floresta:
def model_2(painel):
    y = painel['temp_media']
    X2 = painel[['area_florestal']]
    X2 = sm.add_constant(X2)

    modelo2 = PanelOLS(
        y,
        X2,
        entity_effects=True,
        time_effects=True
    )

    resultado2 = modelo2.fit(cov_type='clustered', cluster_entity=True)
    print(resultado2.summary)


# MODELO 3 - Ambos juntos:
def model_3(painel):
    y = painel['temp_media']
    X3 = painel[['area_desmat', 'area_florestal']]
    X3 = sm.add_constant(X3)

    modelo3 = PanelOLS(
        y,
        X3,
        entity_effects=True,
        time_effects=True
    )

    resultado3 = modelo3.fit(cov_type='clustered', cluster_entity=True)

    print(resultado3.summary)



#painel = painel.set_index(['municipio','time'])


# MODELO COM DEFASAGEM (Lag):
def modeloDefasagem(painel):
    # Ordenar corretamente
    painel = painel.sort_index()

    # Criar defasagem dentro de cada município
    painel['desmat_lag1'] = painel.groupby(level=0)['area_desmat'].shift(1)

    # Remover primeiros meses (ficam NaN)
    painel_lag = painel.dropna(subset=['desmat_lag1'])

    from linearmodels.panel import PanelOLS
    import statsmodels.api as sm

    y = painel_lag['temp_media']
    X = sm.add_constant(painel_lag[['desmat_lag1']])

    modelo_lag = PanelOLS(
        y,
        X,
        entity_effects=True,
        time_effects=True
    ).fit(cov_type='clustered', cluster_entity=True)

    print(modelo_lag.summary)

    
    
# Modelo com PRIMEIRA DIFERENÇA:
def modeloPrimeiraDiferenca(painel):
    painel['d_temp'] = painel.groupby(level=0)['temp_media'].diff()
    painel['d_desmat'] = painel.groupby(level=0)['area_desmat'].diff()

    painel_diff = painel.dropna(subset=['d_temp','d_desmat'])

    y = painel_diff['d_temp']
    X = sm.add_constant(painel_diff[['d_desmat']])

    modelo_diff = PanelOLS(
        y,
        X,
        entity_effects=False,   # já estamos diferenciando
        time_effects=True       # pode manter efeito temporal
    ).fit(cov_type='clustered', cluster_entity=True)

    print(modelo_diff.summary)



# MODELO DINAMICO:
def modeloDinamico(paniel):
    painel['temp_lag1'] = painel.groupby(level=0)['temp_media'].shift(1)

    painel_dyn = painel.dropna(subset=['temp_lag1'])

    y = painel_dyn['temp_media']
    X = sm.add_constant(painel_dyn[['temp_lag1','area_desmat']])

    modelo_dyn = PanelOLS(
        y,
        X,
        entity_effects=True,
        time_effects=True
    ).fit(cov_type='clustered', cluster_entity=True)

    print(modelo_dyn.summary)
    
    
#model_1(painel);
#model_2(painel);
#model_3(painel);

#modeloDefasagem(painel);
#modeloPrimeiraDiferenca(painel);
modeloDinamico(painel);

