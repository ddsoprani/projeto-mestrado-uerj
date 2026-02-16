import rasterio
import rasterio.transform
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np
import pandas as pd
import geopandas as gpd
import sys

if len(sys.argv) < 2:
    print("ERRO: incluir o nome do arquivo")
    sys.exit(1)

tif = sys.argv[1]
ano = tif.split("_")[2].replace(".tif", "");
ano = int(ano);

# -------------------------
# ARQUIVOS
# -------------------------

#tif = "1987_coverage_lclu_1-1-1_72905aab-f4fa-41e2-8d1f-1c2a4949dac0.tif"
#tif = "brazil_coverage_1987.tif";
shp = "/home/danilo/Projeto-Mestrado/Testes_Shape_File_INPE/RJ_Municipios_2024/RJ_Municipios_2024.shp"
saida_csv = f"CSV-RJ/_{ano}_cobertura_por_municipio_RJ.csv"


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


# -------------------------
# LEITURA DO SHAPEFILE
# -------------------------
gdf = gpd.read_file(shp)
# reprojetar municípios para o CRS do raster (EPSG:4326)
gdf = gdf.to_crs("EPSG:4326")

resultados = []

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

df = pd.DataFrame(resultados)
df.to_csv(saida_csv, sep=";", index=False, encoding="utf-8-sig", decimal=",")

print("CSV gerado com sucesso:", saida_csv)

