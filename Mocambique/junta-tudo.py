# 1 - Ler o arquivo de desmatamento
import pandas as pd
df_desmat = pd.read_csv("GEE/resultado_localidades.csv", sep=";", decimal=",");


# 2 - Ler todos os arquivos climáticos da pasta
import glob
arquivos = glob.glob("dados_juntos_localidades_mozambique_V2/clima/*.csv")
lista_df = []
for arq in arquivos:
    df = pd.read_csv(arq, sep=';', decimal = ',' )
    lista_df.append(df)

df_clima = pd.concat(lista_df, ignore_index=True)


# 3 - Ajuste importante (vírgula decimal!)

df_clima = df_clima.replace(",", ".", regex=True)

df_desmat = df_desmat.replace(",", ".", regex=True)

cols_clima = [
    "latitude", "longitude", "ano", "mes",
    "temp_media_graus (C)", "precipitacao_total (mm)",
    "vel. vento (m/s)", "umidade_ar (%)", "pressao_atm (hPa)"
]

for col in cols_clima:
    df_clima[col] = pd.to_numeric(df_clima[col], errors="coerce")


cols_desmat = [
    "ano", "desmatamento_km2", "area_km2", "desmat_relativo_percentual"
]

for col in cols_desmat:
    df_desmat[col] = pd.to_numeric(df_desmat[col], errors="coerce")


# GARANTA que as chaves são strings
for col in ["provincia", "distrito", "localidade"]:
    df_clima[col] = df_clima[col].astype(str)
    df_desmat[col] = df_desmat[col].astype(str)



#4 - Fazer o merge
df_final = df_clima.merge(
    df_desmat,
    on=["provincia", "distrito", "localidade", "ano"],
    how="left"
)


df_final["match"] = df_final["desmatamento_km2"].notna();
print(df_final["match"].value_counts());
#exit();


print(df_final.groupby(
    ["provincia", "distrito", "localidade", "ano"]
).size().value_counts());
#exit();


sem_match = df_final[df_final["desmatamento_km2"].isna()]
print(sem_match);
sem_match.to_csv('investiga.csv');
sem_match[["provincia", "distrito", "localidade"]].drop_duplicates()
#exit();


# Ordena
df_final = df_final.sort_values(
    by=["provincia", "distrito", "localidade", "ano", "mes"]
)


print(df_final.head(10));

df_final.to_csv("dados_juntos_desmat_clima_por_localidade.csv", index=False, sep=";", decimal=",")
