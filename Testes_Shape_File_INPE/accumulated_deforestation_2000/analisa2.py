import geopandas as gpd
import matplotlib.pyplot as plt

# Carregar o shapefile
mask = gpd.read_file("accumulated_deforestation_2000.shp")

# Verificar as colunas
print("Colunas disponiveis:", mask.columns)

# Filtrar apenas para o estado do Esp. Santo
mask_es = mask[mask['state'] == 'ES']

print(f"Numero de registros no ES: {len(mask_es)}")

# Verificar se tem valores faltantes na coluna 'year'
print("Valores faltantes em 'year':", mask_es['year'].isnull().sum())

# Reprojetar para UTM Zona 24S para calculo de area
mask_es = mask_es.to_crs(epsg=31983)

# Calcular area de cada poligono (em km2)
mask_es['area_km2'] = mask_es['geometry'].area / 10**6

# Agrupar por ano e somar area
area_por_ano = mask_es.groupby('year')['area_km2'].sum().reset_index()

# Mostrar a tabela
print("\nArea desmatada no ES por ano (ate 2000):")
print(area_por_ano)

# Plotar grafico
plt.figure(figsize=(10,6))
plt.bar(area_por_ano['year'], area_por_ano['area_km2'], color='brown')
plt.xlabel('Ano')
plt.ylabel('Area desmatada (km2)')
plt.title('Desmatamento acumulado no Esp. Santo ate 2000 (ano a ano)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.show()

