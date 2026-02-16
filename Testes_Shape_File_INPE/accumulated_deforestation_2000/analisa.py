import geopandas as gpd
import matplotlib.pyplot as plt


# Carregar o shapefile da mascara acumulada
mascara_acumulada = gpd.read_file("accumulated_deforestation_2000.shp")

# Verificar as primeiras linhas
print(mascara_acumulada.head())

# Verificar as colunas disponiveis
print("\nColunas disponiveis:", mascara_acumulada.columns)

# Verificar o sistema de coordenadas
print("\nSistema de Coordenadas (CRS):", mascara_acumulada.crs)

# Plotar a mascara acumulada
mascara_acumulada.plot(figsize=(10, 10), color='orange', edgecolor='black')
plt.title('Mascara de Area Acumulada de Supressao ate 2000')
plt.show()

