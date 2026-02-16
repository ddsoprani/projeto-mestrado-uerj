import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import numpy as np
from rasterio.windows import Window


# Caminho para seu arquivo
caminho = "2024_deforestation_annual_1-1-1_18787e80-dd7a-4641-965d-0c410964f705.tif"

# Abre o raster
with rasterio.open(caminho) as src:
    h, w = src.height, src.width

    # ler pequena janela (500x500 pixels)
    #janela = Window(0, 0, 500, 500)
    janela = Window(w//2, h//2, 500, 500)

    pedaco = src.read(1, window=janela)

    '''print("Shape do pedaco:", pedaco.shape)
    print("Minimo:", np.nanmin(pedaco))
    print("Maximo:", np.nanmax(pedaco))
    print("Valores unicos (amostra):", np.unique(pedaco)[:20], "...")'''

    print("Valores unicos (amostra central):", np.unique(pedaco)[:20])
    print("Min:", pedaco.min(), "Max:", pedaco.max())


    # Visualizando esse pedaco
    plt.imshow(pedaco, cmap="viridis")
    plt.colorbar()
    plt.title("Amostra do raster (500x500)")
    plt.show()


    '''print("=== METADADOS DO RASTER ===")
    print("Driver:", src.driver)
    print("Dimensoes (linhas, colunas):", src.height, src.width)
    print("Numero de bandas:", src.count)
    print("Sistema de Coordenadas (CRS):", src.crs)
    print("Bounding Box:", src.bounds)
    print("Resolucao (pixel):", src.res)

    # Le a primeira banda
    banda1 = src.read(1)'''

# Mostra estatisticas basicas
'''print("\n=== ESTATISTICAS DA BANDA 1 ===")
print("Valor minimo:", np.nanmin(banda1))
print("Valor maximo:", np.nanmax(banda1))
print("Media:", np.nanmean(banda1))

# Plot simples
plt.figure(figsize=(8,6))
plt.title("Visualizacao da primeira banda do raster")
plt.imshow(banda1, cmap="viridis")
plt.colorbar(label="Valor dos pixels")
plt.show()'''

