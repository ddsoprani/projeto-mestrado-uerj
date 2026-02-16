import rasterio
from rasterio.windows import from_bounds

# TIF original grande
input_tif = "2024_deforestation_annual_1-1-1_18787e80-dd7a-4641-965d-0c410964f705.tif"

# TIF recortado (saida)
es_tif = "desmatamento_2024_ES_recorte.tif"

# Coordenadas aproximadas do ES
minx, miny = -41.3, -21.3
maxx, maxy = -39.0, -17.9

with rasterio.open(input_tif) as src:
    window = from_bounds(minx, miny, maxx, maxy, src.transform)
    recorte = src.read(1, window=window)

    transform = src.window_transform(window)
    profile = src.profile.copy()
    profile.update({
        "height": recorte.shape[0],
        "width": recorte.shape[1],
        "transform": transform
    })

    with rasterio.open(es_tif, "w", **profile) as dst:
        dst.write(recorte, 1)

print("Recorte salvo como:", es_tif)

