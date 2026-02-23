import os
import pandas as pd
import re
from collections import defaultdict


pasta = "CSV-SP"
dados = []

matriz = defaultdict(dict)
matrizCover = defaultdict(dict)


for arq in os.listdir(pasta):
    if not arq.endswith(".csv"):
        continue

    caminho = os.path.join(pasta, arq)
    df = pd.read_csv(caminho, sep=";")


    # Extrair o ano do nome do arquivo
    match = re.search(r"(\d{4})", arq)
    if not match:
        continue

    ano = int(match.group(1))
    ano_anterior = ano - 1;

    # Nome das colunas esperadas
    col_pixels = f"pixels_desmat_{ano}"
    col_ha = f"area_desmat_ha_{ano}"
    col_km2 = f"area_desmat_km2_{ano}"
    col_cover = f"cobertura_vegetal_{ano_anterior}"
    

    for _, row in df.iterrows():
        municipio = row["municipio"];
        area_km2 = row[col_km2];
        cobertura = row[col_cover]
        matriz[ano][municipio] = area_km2;
        matrizCover[ano][municipio] = cobertura;



for ano, municipios in matriz.items():
    for municipio, area in municipios.items():
        dados.append({
            "Municipio": municipio,
            "Ano": ano,
            "Area_florestal" : matrizCover[ano][municipio],
            "Area_desmat_km2": area
        })

df = pd.DataFrame(dados);

#print(df.dtypes)
df.duplicated(subset=["Municipio", "Ano"]).sum()

#print(df.head(30));
#exit();

df["Area_florestal"] = (
    df["Area_florestal"]
        .str.replace(",", ".", regex=False)
        .astype(float)
)

df["Area_desmat_km2"] = (
    df["Area_desmat_km2"]
        .str.replace(",", ".", regex=False)
        .astype(float)
)


df_pivot = df.pivot(
    index="Municipio",
    columns="Ano",
    #values="Area_desmat_km2"
    values=["Area_florestal", "Area_desmat_km2"]

);

#print(df_pivot.head(20));
#exit();

#df_pivot.columns = [f"{col[0]}_{col[1]}" for col in df_pivot.columns]
#df_pivot.columns = [
#    f"{var}_{ano}"
#    for var, ano in df_pivot.columns
#]

#df_pivot = df_pivot.reset_index()
df_pivot = df_pivot.swaplevel(axis=1)
#df_pivot = df_pivot.sort_index(axis=1, level=0)
ordem_variaveis = ["Area_florestal", "Area_desmat_km2"]

df_pivot = df_pivot.reindex(
    columns=sorted(
        df_pivot.columns,
        key=lambda x: (x[0], ordem_variaveis.index(x[1]))
    )
)


df_pivot.columns = [
    f"{var}_{ano}"
    for ano, var in df_pivot.columns
]

df_pivot = df_pivot.reset_index()





#df_pivot.columns = [f"Area_desmat_km2_{ano}" for ano in df_pivot.columns]

#df_pivot = df_pivot.sort_index(axis=1);
df_pivot = df_pivot.reset_index()



df_pivot.to_csv(
    "desmatamento-final-SP-v5.csv",
    sep=";",
    decimal=',',
    index=True
);



