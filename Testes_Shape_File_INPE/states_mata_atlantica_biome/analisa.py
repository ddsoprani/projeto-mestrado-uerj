import geopandas as gpd
import matplotlib.pyplot as plt

# Caminho para seu shapefile (ajuste aqui)
caminho = "states_mata_atlantica_biome.shp"

# Ler o shapefile
mata_atlantica = gpd.read_file(caminho)

# Ver as primeiras linhas (atributos)
print(mata_atlantica.head(20))

# Ver as colunas disponiveis
print("Colunas disponiveis:", mata_atlantica.columns)

# Verificar o sistema de coordenadas
print("Sistema de coordenadas:", mata_atlantica.crs)

# Plotar o mapa da Mata Atlantica
mata_atlantica.plot(figsize=(10, 10), edgecolor='black', facecolor='green')
plt.title("Mapa da Mata Atlantica")
plt.show()

