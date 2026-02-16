import geopandas as gpd
import matplotlib.pyplot as plt


# Carregar o shapefile do incremento anual
desmatamento = gpd.read_file("yearly_deforestation.shp")

# Ver as primeiras linhas
#print(desmatamento.head(10))

# Ver colunas disponiveis
print("Colunas disponiveis:", desmatamento.columns)

# Verificar sistema de coordenadas
print("Sistema de coordenadas:", desmatamento.crs)

# Filtrar apenas o Estado do Espirito Santo
desmatamento_es = desmatamento[desmatamento['state'] == 'ES']

print("\nDesmatamento no Espirito Santo:")
print(desmatamento_es.head())

# Calcular o total desmatado por ano (em km2)
desmatamento_por_ano = desmatamento_es.groupby('year')['area_km'].sum().reset_index()

print("\nArea desmatada no ES por ano (km2):\n", desmatamento_por_ano)


# Plotar grafico
plt.figure(figsize=(10,6))
plt.bar(desmatamento_por_ano['year'], desmatamento_por_ano['area_km'], color='darkred')
plt.title('Desmatamento Anual no Estado do ES (km2)')
plt.xlabel('Ano')
plt.ylabel('Area desmatada (km2)')
plt.grid(True)
plt.show()

# Exportar para CSV (se quiser)
desmatamento_por_ano.to_csv("desmatamento_ES_por_ano.csv", index=False)


