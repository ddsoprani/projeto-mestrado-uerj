# 1. Ler os dados

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

df = pd.read_csv("Desmatamento_Mozambique_GEE.csv")
gdf_localidades = gpd.read_file("Mocambique_Localidade/Mocambique_Localidade.shp");
print("localidades coluns: ", gdf_localidades.columns);
print(gdf_localidades.is_valid.value_counts());
print("localidades head: ", gdf_localidades.head());

# 2. Criar geometria (pontos)
geometry = [Point(xy) for xy in zip(df["lon"], df["lat"])]
gdf_points = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
'''print(gdf_points.crs)
print(gdf_distritos.crs);
print("Points:", gdf_points.total_bounds)
print("Distritos:", gdf_distritos.total_bounds)'''


# 3. Garantir mesmo CRS
gdf_localidades = gdf_localidades.to_crs(gdf_points.crs)
# calcular area
gdf_localidades["area_km2"] = gdf_localidades.to_crs("EPSG:3857").area / 1e6
areas = gdf_localidades[["NAME_1", "NAME_2", "NAME_3", "area_km2"]]



provincias = ["Nampula", "Zambezia", "Sofala", "Inhambane"]

gdf_localidades_filtrado = gdf_localidades[
    gdf_localidades["NAME_1"].isin(provincias)
]

print("Total Localidades: ", gdf_localidades.is_valid.value_counts());
print("Localidades filtradas: ", gdf_localidades_filtrado.is_valid.value_counts());

gdf_join = gpd.sjoin(
    gdf_points,
    gdf_localidades_filtrado,
    how="inner",
    predicate="intersects"
)

#print(gdf_join.head(20));
#exit();


#6. Agregar por distrito e ano
resultado = (
    gdf_join
    .groupby(["NAME_1", "NAME_2", "NAME_3", "year"])["loss_km2"]
    .sum()
    .reset_index()
)


#Renomeia
resultado = resultado.rename(columns={
    "NAME_1": "provincia",
    "NAME_2": "distrito",
    "NAME_3": "localidade", # ou postos administrativos ??? 
    "year" : "ano",
    "loss_km2": "desmatamento_km2"
})

resultado_final = resultado.merge(
    areas,
    left_on=["provincia", "distrito", "localidade"],
    right_on=["NAME_1", "NAME_2", "NAME_3"],
    how="left"
)

resultado_final = resultado_final.drop(columns=["NAME_1", "NAME_2"])

print(resultado_final.head(20));
exit();


# 7. Pivot (opcional, mas util)
tabela_final = resultado_final.pivot(
    index="distrito",
    columns="ano",
    values="desmatamento_km2"
).fillna(0)

#resultado_final.to_csv("desmatamento_por_distrito_ano.csv", index=False)
#print('Arquivo gerado!');



