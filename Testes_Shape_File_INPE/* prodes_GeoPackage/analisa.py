import fiona
import geopandas as gpd


# Ver as camadas disponiveis no GeoPackage
caminho_gpkg = "prodes_mata_atlantica_nb.gpkg"

camadas = fiona.listlayers(caminho_gpkg)
#print("Camadas disponiveis:", camadas)


gdf = gpd.read_file(caminho_gpkg, layer='yearly_deforestation')
# Ver colunas disponiveis
print("Colunas disponiveis:", gdf.columns)
exit();

# Ver as primeiras 5 linhas
#print(gdf.head())

# Filtrar somente os registros do Espirito Santo
gdf_es = gdf[gdf['state'] == 'ES']
#print("Numero de registros no Espirito Santo:", len(gdf_es))
#print(gdf_es.head())

gdf_es_desmatamento = gdf_es[gdf_es['main_class'] == 'desmatamento']
#print("Numero de registros de desmatamento no ES:", len(gdf_es_desmatamento))
#print(gdf_es_desmatamento.head())

# Agrupar por ano e somar a area desmatada (em km2)
area_por_ano = gdf_es_desmatamento.groupby('year')['area_km'].sum().reset_index()
print("\nArea desmatada no Espirito Santo por ano (km2):")
print(area_por_ano)

# Plotar o grafico
import matplotlib.pyplot as plt

plt.figure(figsize=(10,6))
plt.bar(area_por_ano['year'], area_por_ano['area_km'], color='forestgreen')
plt.xlabel('Ano')
plt.ylabel('Area desmatada (km2)')
plt.title('Desmatamento anual no Espirito Santo (2004-2023)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.show()




