import geopandas as gpd
import matplotlib.pyplot as plt

# 1. Carregar o desmatamento da Mata Atlantica
desmatamento = gpd.read_file("prodes_mata_atlantica_nb.gpkg", layer='yearly_deforestation')

# 2. Filtrar somente o estado do ES
desmatamento_ES = desmatamento[desmatamento['state'] == 'ES']

# 3. Carregar o shapefile dos municipios do ES
municipios = gpd.read_file("/home/danilo/Downloads/Testes_Shape_File_INPE/ES_Municipios_2024/ES_Municipios_2024.shp")  # ajuste o nome se necessário

# 4. Garantir o mesmo CRS - reprojetar para UTM Zona 24S (EPSG:31984) para cálculo de area correto
desmatamento_ES = desmatamento_ES.to_crs(epsg=31984)
municipios = municipios.to_crs(epsg=31984)

# 5. Fazer a intersecao espacial
intersecao = gpd.overlay(desmatamento_ES, municipios, how='intersection')

# 6. Conferir as colunas apos a intersecao (verificar 'year' e 'NM_MUN')
print("Colunas disponiveis na intersecao:", intersecao.columns)

# 7. Calcular area desmatada em km2
intersecao['area_desmatada_km2'] = intersecao.geometry.area / 1e6  # metros quadrados para km2

# 8. Agrupar por municipio ('NM_MUN') e ano ('year')
area_por_municipio_ano = intersecao.groupby(['NM_MUN', 'year'])['area_desmatada_km2'].sum().reset_index()

# 9. Visualizar a tabela
print(area_por_municipio_ano)

# 10. (Opcional) Salvar resultado como CSV
area_por_municipio_ano.to_csv("desmatamento_por_municipio_ano.csv", index=False)


# Somar a area desmatada por municipio, acumulando todos os anos
area_acumulada = intersecao.groupby('NM_MUN')['area_desmatada_km2'].sum().reset_index()

# Junta a soma com o GeoDataFrame dos municipios
municipios = municipios.merge(area_acumulada, on='NM_MUN', how='left')

# Substitui NaN por zero (municipios sem desmatamento)
municipios['area_desmatada_km2'] = municipios['area_desmatada_km2'].fillna(0)


# 11. (Opcional) Gerar um mapa bonito do desmatamento no ES
'''fig, ax = plt.subplots(figsize=(12, 12))
municipios.plot(ax=ax, color='none', edgecolor='black', linewidth=0.5)
desmatamento_ES.plot(ax=ax, color='red', edgecolor='black', alpha=0.5)
ax.set_title("Desmatamento da Mata Atlâatica no Espirito Santo", fontsize=16)
plt.axis('off')
plt.show()'''

fig, ax = plt.subplots(figsize=(12, 12))

municipios.plot(column='area_desmatada_km2',
                cmap='Reds',        # gradiente do branco ao vermelho intenso
                linewidth=0.8,
                ax=ax,
                edgecolor='black',
                legend=True)

ax.set_title('Area Acumulada de Desmatamento por Municipio no ES (km2)', fontsize=16)
plt.axis('off')
plt.show()


