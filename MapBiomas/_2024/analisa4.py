import rasterio
from rasterio.mask import mask
import geopandas as gpd

# Caminhos
raster_path = "2024_deforestation_annual_1-1-1_18787e80-dd7a-4641-965d-0c410964f705.tif"
shp_path = "/home/danilo/Downloads/Testes-Shape-File/ES_Municipios_2024/ES_Municipios_2024.shp"
out_tif = "ES_desmatamento_2024.tif"

# Carrega shapefile do ES
gdf = gpd.read_file(shp_path)
geoms = gdf.geometry.values

# Recorte
with rasterio.open(raster_path) as src:
    out_image, out_transform = mask(src, geoms, crop=True)
    out_meta = src.meta.copy()

# Atualizar metadados
out_meta.update({
    "height": out_image.shape[1],
    "width": out_image.shape[2],
    "transform": out_transform
})

# Salvar raster recortado
with rasterio.open(out_tif, "w", **out_meta) as dest:
    dest.write(out_image)

