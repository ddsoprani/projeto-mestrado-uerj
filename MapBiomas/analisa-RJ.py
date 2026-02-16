import geopandas as gpd
import rasterio
from rasterio.mask import mask
import numpy as np
import pandas as pd
import sys
import csv

if len(sys.argv) < 2:
    print("ERRO: incluir o nome do arquivo")
    sys.exit(1)

arquivo = sys.argv[1]
ano = arquivo.split("_")[0]
ano_anterior = int(ano) - 1;



# Caminho do shapefile do RJ
shp_rj = "/home/danilo/Projeto-Mestrado/Testes_Shape_File_INPE/RJ_Municipios_2024/RJ_Municipios_2024.shp"

# Lendo o shapefile
rj = gpd.read_file(shp_rj)

print(rj.crs)

#PASSO 4:

#tif_path = "2022_deforestation_annual_1-1-1_74215b40-a389-43b6-aa16-ebdcb7b9a252.tif"
tif_path = arquivo;

src = rasterio.open(tif_path)

print(src.crs)

# PASSO 5:
if rj.crs != src.crs:
    rj = rj.to_crs(src.crs)


#print(rj.crs)
#print(src.crs)


#print(rj.crs == src.crs)


# PASSO 6

# Geometrias do RJ
geoms = rj.geometry.values

# Recorte (mask)
raster_rj, transform = mask(
    src,
    geoms,
    crop=True,
    nodata=0
)

src.close()


raster_rj = raster_rj[0]


# PASSO 7:

print("Shape do raster RJ:", raster_rj.shape)
print("Valores únicos:", np.unique(raster_rj))

#PASSO 8:
#print(raster_rj[:10, :10])


# PASSO

# [4,6] são as classes de desmatamento propriamemte ditos, segundo site do MapBiomas
mask_desmat = np.isin(raster_rj, [4, 6])

#print(mask_desmat[:10, :10])


#PASSO:

pixels_desmat = np.sum(mask_desmat)
print(f"Pixels com desmatamento em {ano} no RJ:", pixels_desmat)


area_rj_ha = pixels_desmat * 0.09


area_rj_km2 = area_rj_ha / 100


print(f"Área desmatada em {ano} no RJ: {area_rj_ha:.2f} ha ({area_rj_km2:.2f} km²)")



# AGORA A PARTE DOS MUNICIPIOS


# Shapefile dos municípios do RJ
municipios = gpd.read_file(shp_rj)

# Garantir mesmo CRS do raster
municipios = municipios.to_crs(src.crs)
#print(municipios.columns);


#tif_path = "2022_deforestation_annual_1-1-1_74215b40-a389-43b6-aa16-ebdcb7b9a252.tif"
tif_path = arquivo;
src = rasterio.open(tif_path)



#abrir os arquivos de coverage

coverage = {}

with open(f"/home/danilo/Projeto-Mestrado/Coverage/CSV-RJ/_{ano_anterior}_cobertura_por_municipio_RJ.csv", newline="", encoding="utf-8-sig") as f:
    leitor = csv.DictReader(f, delimiter=";")

    for linha in leitor:
        municipio = linha["Municipio"]
        sem_dados = linha["Sem dados"]
        formacao_flor = linha["Formação Florestal"]
        mangue = linha["Mangue"]

        coverage[municipio] = [sem_dados, formacao_flor, mangue]



#print(coverage);
#exit();


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
        cover_forest = coverage[nome_mun][1].replace(",",".");
        cover_mague  = coverage[nome_mun][2].replace(",",".");

        cover = float(cover_forest) + float(cover_mague);
        percent = (float(area_km2) / float(cover)) * 100;
        percent = round(percent, 2);

        resultados.append({
            "municipio": nome_mun,
            f"cobertura_vegetal_{ano_anterior}": cover,
            f"pixels_desmat_{ano}": pixels_desmat,
            f"area_desmat_ha_{ano}": area_ha,
            f"area_desmat_km2_{ano}": area_km2,
            f"percentual": percent
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
print("Total estadual (ha):", area_rj_ha);


# PASSO: Exportar para CSV:

df_municipios.to_csv(
    f"CSV-RJ/_{ano}_desmatamento_municipios_RJ.csv",
    sep=';',
    decimal=',',
    index=False
);

print("Arquivo criado!");
