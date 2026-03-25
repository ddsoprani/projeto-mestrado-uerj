'''import os
import geopandas as gpd

# Forcar o GDAL a recriar o .shx
os.environ["SHAPE_RESTORE_SHX"] = "YES"

shapefile_path = "Mocambique_Provincias/Mocambique_Provincias.shp"

gdf = gpd.read_file(shapefile_path)

print(gdf.head())
gdf.plot()

#exit();'''



import geopandas as gpd
import matplotlib.pyplot as plt

# Caminho do shapefile (.shp)
#shapefile_path = "Mocambique_Provincias/Mocambique_Provincias.shp"
#shapefile_path = "Mocambique_Distritos/Mocambique_Distritos.shp"
shapefile_path = "Mocambique_Localidade/Mocambique_Localidade.shp"

# 1. Carregar o shapefile
gdf = gpd.read_file(shapefile_path)

# 2. Mostrar informacoes basicas
print("=== INFORMACOES GERAIS ===")
print(gdf.info())

# Remover colunas inuteis
#gdf = gdf.drop(columns=["GID_0", "GID_1", "CC_2", "HASC_2", "NL_NAME_1", "NL_NAME_1", "TYPE_2", "ENGTYPE_2", "VARNAME_2", "NL_NAME_2", "GID_2"])

# Renomear colunas (opcional, mas ajuda muito)
gdf = gdf.rename(columns={
    "NAME_0": "pais",
    "NAME_1": "provincia", # Estado 
    "NAME_2": "distrito",   # Municipio
    "NAME_3": "localidade"   # Municipio
})


print("\n=== PRIMEIRAS LINHAS ===")
print(gdf.head())

print("\n=== SISTEMA DE COORDENADAS (CRS) ===")
print(gdf.crs)


print("\n=== COLUNAS ===")
print(gdf.columns)

# 3. Plotar o mapa
gdf.plot()
plt.title("Visualizacao do Shapefile")
plt.show();


# Faz o recorte

print(gdf.columns)
print(gdf.head())

exit();

provincias_interesse = ["Nampula", "Zambezia", "Sofala", "Inhambane"];

#gdf_filtrado = gdf[gdf["provincia"].isin(provincias_interesse)]
gdf_filtrado = gdf[gdf["provincia"].isin(provincias_interesse)].copy()
print(gdf_filtrado["provincia"].value_counts())

gdf_filtrado["geometry"] = gdf_filtrado.buffer(0)
gdf_filtrado = gdf_filtrado.reset_index(drop=True)

print(gdf_filtrado["provincia"].value_counts())
exit();

# salvar novo shapefile
gdf_filtrado.to_file("Mocambique_Distritos_Filtrados/distritos_filtrados.shp")


