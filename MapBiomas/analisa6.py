import geopandas as gpd
import rasterio
from rasterio.mask import mask
import numpy as np
import pandas as pd
import sys

if len(sys.argv) < 2:
    print("ERRO: incluir o nome do arquivo")
    sys.exit(1)

arquivo = sys.argv[1]
ano = arquivo.split("_")[0]
#print(f"O ano é {ano}")
#exit();

# Caminho do shapefile do ES
shp_es = "/home/danilo/Projeto-Mestrado/Testes_Shape_File_INPE/ES_Municipios_2024/ES_Municipios_2024.shp"

# Lendo o shapefile
es = gpd.read_file(shp_es)

print(es.crs)


#PASSO 4:

#tif_path = "2022_deforestation_annual_1-1-1_74215b40-a389-43b6-aa16-ebdcb7b9a252.tif"
tif_path = arquivo;

src = rasterio.open(tif_path)

print(src.crs)


# PASSO 5:
if es.crs != src.crs:
    es = es.to_crs(src.crs)


#print(es.crs)
#print(src.crs)


#print(es.crs == src.crs)


# PASSO 6

# Geometrias do ES
geoms = es.geometry.values

# Recorte (mask)
raster_es, transform = mask(
    src,
    geoms,
    crop=True,
    nodata=0
)

src.close()


raster_es = raster_es[0]


# PASSO 7:

print("Shape do raster ES:", raster_es.shape)
print("Valores únicos:", np.unique(raster_es))

#PASSO 8:
#print(raster_es[:10, :10])



# PASSO

# [4,6] são as classes de desmatamento propriamemte ditos, segundo site do MapBiomas
mask_desmat = np.isin(raster_es, [4, 6])

#print(mask_desmat[:10, :10])


#PASSO:

pixels_desmat = np.sum(mask_desmat)
print(f"Pixels com desmatamento em {ano} no ES:", pixels_desmat)


area_es_ha = pixels_desmat * 0.09


area_es_km2 = area_es_ha / 100


print(f"Área desmatada em {ano} no ES: {area_es_ha:.2f} ha ({area_es_km2:.2f} km²)")



# AGORA A PARTE DOS MUNICIPIOS


# Shapefile dos municípios do ES
shp_mun = "/home/danilo/Projeto-Mestrado/Testes_Shape_File_INPE/ES_Municipios_2024/ES_Municipios_2024.shp"
municipios = gpd.read_file(shp_mun)

# Garantir mesmo CRS do raster
municipios = municipios.to_crs(src.crs)

#print(municipios.columns);


#
#tif_path = "2022_deforestation_annual_1-1-1_74215b40-a389-43b6-aa16-ebdcb7b9a252.tif"
tif_path = arquivo;
src = rasterio.open(tif_path)


#PASSO: Loop por município (código principal):

resultados = []
col_nome = "NM_MUN"


for idx, row in municipios.iterrows():
    nome_mun = row[col_nome]
    geom = [row.geometry]

    try:
        raster_mun, _ = mask(
            src,
            geom,
            crop=True,
            nodata=0
        )

        raster_mun = raster_mun[0]

        # Mascara de desmatamento
        mask_desmat = np.isin(raster_mun, [4, 6])
        pixels_desmat = np.sum(mask_desmat)

        area_ha = pixels_desmat * 0.09
        area_km2 = area_ha / 100

        resultados.append({
            "municipio": nome_mun,
            f"pixels_desmat_{ano}": pixels_desmat,
            f"area_desmat_ha_{ano}": area_ha,
            f"area_desmat_km2_{ano}": area_km2
        })

    except Exception as e:
        print(f"Erro no municipio {nome_mun}: {e}")


src.close();



#PASSO: Criar o DataFrame final

#df_resultados = pd.DataFrame(resultados)
df_municipios = pd.DataFrame(resultados)


#print(df_resultados.head())
print(df_municipios.head())



# PASSO: Checagem de consistencia (importantissima):

print("Soma municipal (ha):", df_municipios[f"area_desmat_ha_{ano}"].sum())
print("Total estadual (ha):", area_es_ha);


# PASSO: Exportar para CSV:

df_municipios.to_csv(
    f"_{ano}_desmatamento_municipios_ES.csv",
    sep=';',
    decimal=',',
    index=False
);


