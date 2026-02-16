import geopandas as gpd
from rasterstats import zonal_stats
import pandas as pd
import rasterio
import math

# Arquivos de entrada
raster_path = "desmatamento_2024_ES_recorte.tif"
shp_path = "/home/danilo/Downloads/Testes-Shape-File/ES_Municipios_2024/ES_Municipios_2024.shp"

# Saida
saida_csv = "desmatamento_municipios_ES_2024.csv"

# Carregar shapefile
gdf = gpd.read_file(shp_path)

# Abrir raster recortado
src = rasterio.open(raster_path)

# Reprojetar shapefile (se necessario)
if gdf.crs != src.crs:
    gdf = gdf.to_crs(src.crs)

# Zonal statistics
stats = zonal_stats(
    gdf,
    raster_path,
    categorical=True,
    nodata=0
)

# Funcao para calcular area real do pixel
def area_pixel_ha(lat, res):
    R = 6371000
    dlat = math.radians(res)
    dlon = math.radians(res)
    lat_rad = math.radians(lat)
    a = R**2 * abs(dlat * dlon) * abs(math.cos(lat_rad))
    return a / 10000  # m2 -> ha

ha_por_pixel = area_pixel_ha(-19, src.res[0])

# Extrair valores por municipio
pixels_list = []
area_list = []

for s in stats:
    px = sum(v for k, v in s.items() if k > 0)
    pixels_list.append(px)
    area_list.append(px * ha_por_pixel)

# Criar tabela
gdf["pixels_desmat"] = pixels_list
gdf["area_ha"] = area_list

gdf[["NM_MUN", "pixels_desmat", "area_ha"]].to_csv(saida_csv, index=False)

print("CSV gerado:", saida_csv)

