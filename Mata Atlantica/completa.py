import pandas as pd
import glob
import os

# ler base principal
df = pd.read_csv("painel_final_clima_desmat.csv", sep=";", decimal=",")

# padronizar nome (importante!)
df["Municipio"] = df["Municipio"].str.strip()

# criar chave (ja esta pronta, mas vamos garantir padrao)
df["municipio_uf"] = df["Municipio"].str.upper()


# Funcao para ler arquivos auxiliares
# ALTITUDE
def carregar_altitude(pasta):
    arquivos = glob.glob(os.path.join(pasta, "*.csv"))

    lista = []

    for arq in arquivos:
        nome = os.path.basename(arq).replace(".csv", "").upper()
        uf = '';
        if nome == "ALTITUDE_MUNICIPIOS_SP": 
            uf = 'SP';
        elif nome == "ALTITUDE_MUNICIPIOS_RJ":
            uf = 'RJ';
        else:
            uf = 'ES';


        temp = pd.read_csv(arq, sep=";", decimal=",")

        temp["municipio_uf"] = (
            temp["municipio"].str.strip().str.upper() + "-" + uf
        )

        temp = temp[["municipio_uf", "altitude"]]

        lista.append(temp)

    return pd.concat(lista, ignore_index=True)

df_alt = carregar_altitude("/home/danilo/Projeto-Mestrado/Altimetria/");
print(df_alt.head());



# DISTANCIA DO MAR
def carregar_distancia(pasta):
    arquivos = glob.glob(os.path.join(pasta, "distancia_mar_municipios*"))
    #print(arquivos);
    #exit();

    lista = []

    for arq in arquivos:
        temp = pd.read_csv(arq, sep=";", decimal=",")

        temp["municipio_uf"] = (
            temp["municipio"].str.strip().str.upper() + "-" + temp["SIGLA_UF"]
        )

        temp = temp[["municipio_uf", "dist_mar_km"]]

        lista.append(temp)

    return pd.concat(lista, ignore_index=True)

df_dist = carregar_distancia("/home/danilo/Projeto-Mestrado/Distancia-Mar/")
print(df_dist.head());


# MERGE's

# merge altitude
df = df.merge(df_alt, on="municipio_uf", how="left")

# merge distancia
df = df.merge(df_dist, on="municipio_uf", how="left")

print(df.head(20));

df.to_csv("painel_mata_atlantica_completo.csv", sep=";", decimal=",");

