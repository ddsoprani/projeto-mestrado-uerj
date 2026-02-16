import geopandas as gpd
import rasterio
import rasterio.mask
import numpy as np
import pandas as pd

# ============================
# 1. Carrega shapefile do ES
# ============================
shp_path = "/home/danilo/Downloads/Testes_Shape_File_INPE/ES_Municipios_2024/ES_Municipios_2024.shp"
es = gpd.read_file(shp_path)
es = es.to_crs("EPSG:4326")  # mesmo CRS do raster MapBiomas

# ============================
# 2. Raster do MapBiomas 2024
# ============================
raster_path = "2024_deforestation_annual_1-1-1_18787e80-dd7a-4641-965d-0c410964f705.tif"

# Classes de desmatamento DEFINITIVAS
DESMAT_CLASSES = [4, 6]

# Lista para guardar resultados
resultados = []

# ============================
# 3. Processamento municipio a municipio (leve)
# ============================
for idx, muni in es.iterrows():

    geom = [muni.geometry]

    with rasterio.open(raster_path) as src:
        try:
            # recorte da area do municipio (nao carrega tudo)
            out_image, out_transform = rasterio.mask.mask(src, geom, crop=True)
            out_image = out_image[0]

            # pixels de interesse
            mask = np.isin(out_image, DESMAT_CLASSES)

            # contagem de pixels
            pixels_desmat = int(np.sum(mask))

            # conversao para hectares (30 m x 30 m = 900 m2 = 0.09 ha)
            area_ha = pixels_desmat * 0.09

        except ValueError:
            # municipio fora do raster
            pixels_desmat = 0
            area_ha = 0.0

    resultados.append({
        "municipio": muni["NM_MUN"],
        "pixels_desmat_2024": pixels_desmat,
        "area_desmat_ha_2024": area_ha
    })

# ============================
# 4. Salva em CSV
# ============================
df = pd.DataFrame(resultados)
df.to_csv("desmatamento_ES_2024.csv", index=False)

print(df)
print("\nArquivo salvo como: desmatamento_ES_2024.csv")

