import rasterio
from rasterio.windows import from_bounds
import numpy as np
import matplotlib.pyplot as plt

caminho = "2024_deforestation_annual_1-1-1_18787e80-dd7a-4641-965d-0c410964f705.tif"

# Bounding box aproximado para ES, RJ e SP
lon_min = -42.5
lon_max = -39.0
lat_min = -20.5
lat_max = -17.5

# saida
tif_output = "recorte_ES.tif"
png_output = "recorte_ES.png"


with rasterio.open(caminho) as src:

    # Criar uma janela (window) correspondente ao bounding box
    janela = from_bounds(lon_min, lat_min, lon_max, lat_max, src.transform)

    # Ler SOMENTE essa regiao
    recorte = src.read(1, window=janela)

    # Obter o transform especifico da regiao recortada
    transform = src.window_transform(janela)

    profile = src.profile
    profile.update({
        "height": recorte.shape[0],
        "width": recorte.shape[1],
        "transform": transform
    })

    

    '''print("Shape da regiao recortada:", sudeste.shape)
    print("Valores unicos (amostra):", np.unique(sudeste)[:20])
    print("Min:", sudeste.min(), "Max:", sudeste.max())'''


    # ---------------------------------------
    # 4. Salvar novo TIFF
    # ---------------------------------------
    with rasterio.open(tif_output, "w", **profile) as dst:
        dst.write(recorte, 1)

# ---------------------------------------
# 5. Salvar PNG da imagem recortada
# ---------------------------------------
plt.imsave(png_output, recorte, cmap="viridis")

print("Novo raster salvo em:", tif_output)
print("Imagem PNG salva em:", png_output)

# Visualizacao simples
'''plt.imshow(sudeste, cmap="viridis")
plt.colorbar()
plt.title("Regiao Sudeste (SP, RJ, ES)")
plt.show()
'''
