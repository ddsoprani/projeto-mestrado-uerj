import geopandas as gpd
import pandas as pd
import glob
import os

# Caminho onde estao os arquivos
pasta = "JSON/"

# Lista todos os arquivos .geojson
arquivos = glob.glob(os.path.join(pasta, "*.geojson"))

lista_gdfs = []

for arquivo in arquivos:
    # Le o geojson
    gdf = gpd.read_file(arquivo)
    
    # Extrai o ano do nome do arquivo (ajuste conforme seu padrao)
    # Exemplo: grid_desmatamento_2005.geojson
    nome = os.path.basename(arquivo)
    #ano = nome.split("_")[-1].replace(".geojson", "")
    
    #gdf["ano"] = int(ano)
    
    lista_gdfs.append(gdf)

# Junta tudo
gdf_final = pd.concat(lista_gdfs, ignore_index=True)

# Se quiser remover geometria (pra CSV ficar leve)
df_final = pd.DataFrame(gdf_final.drop(columns="geometry"))

print(df_final.head(10));

# Salva CSV
df_final.to_csv("Desmatamento_Mozambique_GEE.csv", index=False)

print("CSV gerado com sucesso!")

print(df_final["year"].unique());

