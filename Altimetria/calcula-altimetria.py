import geopandas as gpd
import rasterio, csv

# 1. Ler shapefile dos municipios
gdf = gpd.read_file("../Testes_Shape_File_INPE/SP_Municipios_2024/SP_Municipios_2024.shp");

# Renomear coluna
gdf = gdf.rename(columns={"NM_MUN": "municipio"})

# 2. Garantir que estah em WGS84 (caso nao esteja)
gdf = gdf.to_crs(4326)

# 3. Reprojetar para projecao metrica para calcular centroides corretamente
gdf_proj = gdf.to_crs(5880)   # SIRGAS 2000 / Brazil Polyconic

# 4. Calcular centroides
#gdf["centroid"] = gdf_proj.centroid.to_crs(4326)

# Novo calculo usando representative_point
gdf["point"] = gdf_proj.representative_point().to_crs(4326)


# 5. Extrair latitude e longitude
#gdf["lon"] = gdf["centroid"].x
#gdf["lat"] = gdf["centroid"].y


gdf["lon"] = gdf["point"].x
gdf["lat"] = gdf["point"].y

# 6. Ver resultado
#print(gdf[["lat", "lon"]].head())

# Criar coluna para altitude
gdf["altitude"] = None



# Calcula Altitude
def calculaAltitude(lat, long):

    # Converter latitude e longitude para o sistema de coordenadas do raster
    coordinates = [(long, lat)]  # Observe que rasterio usa (lon, lat)


    # Abrir o raster e extrair os valores
    with rasterio.open("/home/danilo/Downloads/Orquideas/altit/wc2.1_30s_elev.tif") as altit_raster:
        altit_values = list(altit_raster.sample(coordinates))
        altit = altit_values[0][0]

    if altit is None or altit <= 0 or altit <= -10000:
        altit = 1
    return altit;



# calcula
# Percorrer municipios
for i, row in gdf.iterrows():
    
    lat = row["lat"]
    lon = row["lon"]
    
    try:
        alt = calculaAltitude(lat, lon)
    except:
        alt = None

    gdf.at[i, "altitude"] = alt
    
    #print(i, lat, lon, gdf['municipio'], alt)


# Exportar:

gdf[["CD_MUN", "municipio","lat","lon","altitude"]].to_csv(
    "altitude_municipios_SP.csv",
    sep=";",
    decimal=",",
    index=False
);
