# 1. Ler os dados

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

df = pd.read_csv("Desmatamento_Mozambique_GEE.csv")
gdf_distritos = gpd.read_file("Mocambique_Distritos/Mocambique_Distritos.shp");
print("distritos coluns: ", gdf_distritos.columns);
print(gdf_distritos.is_valid.value_counts());
print("distritos head: ", gdf_distritos.head());

# 2. Criar geometria (pontos)
geometry = [Point(xy) for xy in zip(df["lon"], df["lat"])]
gdf_points = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
'''print(gdf_points.crs)
print(gdf_distritos.crs);
print("Points:", gdf_points.total_bounds)
print("Distritos:", gdf_distritos.total_bounds)'''


# 3. Garantir mesmo CRS
gdf_distritos = gdf_distritos.to_crs(gdf_points.crs)
# calcular area
gdf_distritos["area_km2"] = gdf_distritos.to_crs("EPSG:3857").area / 1e6
areas = gdf_distritos[["NAME_1", "NAME_2","area_km2"]]


provincias = ["Nampula", "Zambezia", "Sofala", "Inhambane"]

gdf_distritos_filtrado = gdf_distritos[
    gdf_distritos["NAME_1"].isin(provincias)
]


print("Total Distritos: ", gdf_distritos.is_valid.value_counts());
print("Total Distritos Filtrados: ", gdf_distritos_filtrado.is_valid.value_counts());
exit();

gdf_join = gpd.sjoin(
    gdf_points,
    gdf_distritos_filtrado,
    how="inner",
    predicate="intersects"
)


#6. Agregar por distrito e ano
resultado = (
    gdf_join
    .groupby(["NAME_1", "NAME_2", "year"])["loss_km2"]
    .sum()
    .reset_index()
)



#Renomeia
resultado = resultado.rename(columns={
    "NAME_1": "provincia",
    "NAME_2": "distrito",
    "year" : "ano",
    "loss_km2": "desmatamento_km2"
})

resultado_final = resultado.merge(
    areas,
    left_on=["provincia", "distrito"],
    right_on=["NAME_1", "NAME_2"],
    how="left"
)

resultado_final = resultado_final.drop(columns=["NAME_1", "NAME_2"])

print(resultado_final.head());
exit();


# 7. Pivot (opcional, mas util)
tabela_final = resultado_final.pivot(
    index="distrito",
    columns="ano",
    values="desmatamento_km2"
).fillna(0)

#resultado_final.to_csv("desmatamento_por_distrito_ano.csv", index=False)
#print('Arquivo gerado!');



