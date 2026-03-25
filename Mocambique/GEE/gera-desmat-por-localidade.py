import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# =========================
# 1. Ler CSV (grid de desmatamento)
# =========================
df = pd.read_csv("Desmatamento_Mozambique_GEE.csv")

# Criar geometria (lon, lat)
geometry = [Point(xy) for xy in zip(df["lon"], df["lat"])]
gdf_points = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

# =========================
# 2. Ler shapefile das localidades
# =========================
shp = "Mocambique_Localidade/Mocambique_Localidade.shp";
gdf_localidades = gpd.read_file(shp);



# Garantir mesmo CRS
gdf_localidades = gdf_localidades.to_crs("EPSG:4326")

#print(gdf_localidades.head(10));
#exit();

# =========================
# 3. FILTRO DAS PROVINCIAS
# =========================

provincias_interesse = ["Nampula", "Zambezia", "Sofala", "Inhambane"]
col_provincia = "NAME_1"
gdf_localidades = gdf_localidades[
    gdf_localidades[col_provincia].isin(provincias_interesse)
]


# calcula a area considerando a localizacao da provincia
result= []

for provincia in provincias_interesse:
    gdf_prov = gdf_localidades[gdf_localidades["NAME_1"] == provincia].copy()
    # escolher projecao
    if provincia in ["Inhambane", "Sofala"]:
        epsg = 32736
    else:
        epsg = 32737

    # calcular area
    gdf_proj = gdf_prov.to_crs(epsg=epsg)
    gdf_prov["area_km2"] = gdf_proj.geometry.area / 1e6

    result.append(gdf_prov)

gdf_localidades_final = pd.concat(result)
#print(gdf_localidades_final.head(10));
#exit();



#print(gdf_localidades.head(10));
#exit();

gdf_localidades_final["geometry"] = gdf_localidades_final.buffer(0);






#print(gdf_points.head());
#print(gdf_localidades_final.head());
#exit();

# =========================
# 4. Spatial Join (ponto dentro do poligono)
# =========================

gdf_points_proj = gdf_points.to_crs(epsg=32736)
gdf_localidades_proj = gdf_localidades_final.to_crs(epsg=32736)

gdf_join = gpd.sjoin_nearest(
    gdf_localidades_proj,   # <- LOCALIDADES primeiro
    gdf_points_proj,        # <- PONTOS depois
    how="left",
    distance_col="distancia"
)

gdf_join = gdf_join.to_crs(epsg=4326)


'''for idx, row in gdf_join.iterrows():
    valor = row["NAME_3"]
    print(valor);
exit();'''


# =========================
# 5. Agregar desmatamento por localidade
# =========================




col_localidade = "NAME_3"  # ou outro nome

resultado = (
    gdf_join
    .groupby(["NAME_1", "NAME_2", "NAME_3", "year"])
    .agg({
        "loss_km2": "sum"
    })
    .reset_index()
)

# Criar todas combinações localidade × ano
localidades = gdf_localidades_final[["NAME_1", "NAME_2", "NAME_3"]].drop_duplicates()
anos = resultado["year"].unique()
painel = localidades.merge(
    pd.DataFrame({"year": anos}),
    how="cross"
)


# Fazer merge com seu resultado
resultado_aux = painel.merge(
    resultado,
    on=["NAME_1", "NAME_2", "NAME_3", "year"],
    how="left"
)

# Preencher zeros
resultado_aux["loss_km2"] = resultado_aux["loss_km2"].fillna(0)


# Agora sim: adicionar area
resultado_final = resultado_aux.merge(
    gdf_localidades_final[["NAME_1", "NAME_2", "NAME_3", "area_km2"]],
    on=["NAME_1", "NAME_2", "NAME_3"],
    how="left"
)

resultado_final["desmat_relativo_percentual"] = (
    resultado_final["loss_km2"] / resultado_final["area_km2"]
)

#Renomeia
resultado_final = resultado_final.rename(columns={
    "NAME_1": "provincia",
    "NAME_2": "distrito",
    "NAME_3": "localidade", # ou postos administrativos ??? 
    "year" : "ano",
    "loss_km2": "desmatamento_km2"
})

# =========================
# 6. Visualizar
# =========================

print(resultado_final.head(10))


# Salvar
resultado_final.to_csv("resultado_localidades2.csv", index=False, sep=";", decimal = ",")
