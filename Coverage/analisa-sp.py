import rasterio
import rasterio.transform
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np
import pandas as pd
import geopandas as gpd
import sys
import os
import glob

if len(sys.argv) < 2:
    print("ERRO: incluir o nome do arquivo")
    sys.exit(1)

tif = sys.argv[1]
ano = tif.split("_")[2].replace(".tif", "");
ano = int(ano);

# -------------------------
# ARQUIVOS
# -------------------------

#shp = "/home/danilo/Projeto-Mestrado/Testes_Shape_File_INPE/RJ_Municipios_2024/RJ_Municipios_2024.shp"

saida_csv = f"CSV-SP/_{ano}_cobertura_por_municipio_SP.csv"

resultados = []

# -------------------------
# CLASSES DE INTERESSE
# -------------------------

CLASSES = {
    0: "Sem dados",
    3: "Formação Florestal",
    4: "Formação Savânica",
    5: "Mangue",
    9: "Silvicultura",
    11: "Formação Campestre",
    12: "Formação Natural Não Florestal",
    15: "Pastagem",
    20: "Mosaico Agricultura-Pastagem",
    21: "Agrultura",
    23: "Praia/Duna/Areal",
    24: "Área Urbana",
    25: "Outras Áreas Não Vegetadas",
    29: "Afloramento Rochoso",
    31: "Aquicultura",
    32: "Mineração",
    33: "Corpos d'Água",
    41: "Arroz Irrigado",
    46: "Soja",
    48: "Cana-de-açúcar",
    49: "Outras Lavouras Temporárias",
    50: "Outras Lavouras Perenes"
}


def geraResult(resultados, shp):
    # -------------------------
    # LEITURA DO SHAPEFILE
    # -------------------------
    gdf = gpd.read_file(shp)
    # reprojetar municípios para o CRS do raster (EPSG:4326)
    gdf = gdf.to_crs("EPSG:4326")


    with rasterio.open(tif) as src:
        for idx, row in gdf.iterrows():
            municipio = row["NM_MUN"]  # ajuste se sua coluna tiver outro nome
            geom = [row.geometry]

            # recorte
            recorte, rec_transform = mask(src, geom, crop=True)

            # preparar reprojeção para UTM do RJ (SIRGAS 2000 / UTM 23S)
            dst_crs = "EPSG:31983"

            transform, width, height = calculate_default_transform(
                src.crs, dst_crs, 
                recorte.shape[2], recorte.shape[1], *rasterio.transform.array_bounds(
                    recorte.shape[1], recorte.shape[2], rec_transform
                )
            )


            recorte_utm = np.zeros((1, height, width), dtype=recorte.dtype)

            reproject(
                source=recorte,
                destination=recorte_utm,
                src_transform=rec_transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=dst_crs,
                resampling=Resampling.nearest
            )

            banda = recorte_utm[0]

            # área do pixel (m² -> km²)
            pixel_area_km2 = abs(transform.a * transform.e) / 1e6

            linha = {"Municipio": municipio}

            for codigo, nome in CLASSES.items():
                pixels = np.sum(banda == codigo)
                area_km2 = pixels * pixel_area_km2
                linha[nome] = round(area_km2, 3)

            resultados.append(linha)
            #print("Tamanho: ", len(resultados));
            ####### Fim da função ######



##########################################################
##################### Codigo principal ###################
##########################################################


#Lista as 11 regioes de SP
base_dir = "/home/danilo/Projeto-Mestrado/MapBiomas/RECORTA-SP"
shapes_por_regiao = {}

for regiao in os.listdir(base_dir):
    caminho_regiao = os.path.join(base_dir, regiao)

    if os.path.isdir(caminho_regiao):
        shapes = glob.glob(os.path.join(caminho_regiao, "*.shp"))
        for shp in shapes:
            shapes_por_regiao[regiao] = os.path.basename(shp);


for shp in shapes_por_regiao:
    pasta = "/home/danilo/Projeto-Mestrado/MapBiomas/RECORTA-SP/" + shp + "/" + shapes_por_regiao[shp];
    print(pasta);
    geraResult(resultados, pasta);
    print();




df = pd.DataFrame(resultados)

df = (df.groupby("Municipio", as_index=False).sum());
df.to_csv(saida_csv, sep=";", index=False, encoding="utf-8-sig", decimal=",")

print("CSV gerado com sucesso:", saida_csv)

