import geopandas as gpd
import matplotlib.pyplot as plt

# Caminho para o seu shapefile
shapefile_path = 'hydrography.shp'

# Lendo o shapefile
hidrografia_pampa = gpd.read_file(shapefile_path)

# Ver as primeiras linhas
print(hidrografia_pampa.head())

# Ver as colunas disponiveis
print(hidrografia_pampa.columns)

# Plotar o shapefile
hidrografia_pampa.plot(figsize=(10, 8), color='blue', edgecolor='black')
plt.title('Hidrografia do Bioma Pampa')
plt.show()

