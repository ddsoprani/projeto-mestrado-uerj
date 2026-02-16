import rasterio
import geopandas as gpd
import numpy as np
from rasterio.mask import mask

#tif = "1987_coverage_lclu_1-1-1_72905aab-f4fa-41e2-8d1f-1c2a4949dac0.tif"
tif = "brazil_coverage_1987.tif";
shp = "/home/danilo/Projeto-Mestrado/Testes_Shape_File_INPE/ES_Municipios_2024/ES_Municipios_2024.shp"

gdf = gpd.read_file(shp)

with rasterio.open(tif) as src:
    for idx, row in gdf.iterrows():
        municipio = row["NM_MUN"]
        geom = [row.geometry]

        recorte, _ = mask(src, geom, crop=True)
        classes = np.unique(recorte)

        print(municipio, classes)

