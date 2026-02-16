import geopandas as gpd
import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

shp_es = "/home/danilo/Projeto-Mestrado/Testes_Shape_File_INPE/ES_Municipios_2024/ES_Municipios_2024.shp"
municipios = gpd.read_file(shp_es)
municipios = municipios.to_crs("EPSG:4326")

municipios["centroide"] = municipios.geometry.centroid
municipios["lon"] = municipios.centroide.x
municipios["lat"] = municipios.centroide.y

ds = xr.open_dataset("temp_era5_2020_es.nc")

print(ds);

valores = []

for _, row in municipios.iterrows():
    temp = ds["t2m"].sel(
        longitude=row["lon"],
        latitude=row["lat"],
        method="nearest"
    ).mean().values

    temp_c = temp - 273.15


    valores.append({
        "municipio": row["NM_MUN"],
        "temp_media_2020": float(temp_c)
    })



df_clima = pd.DataFrame(valores)
df_clima.to_csv("clima_municipios_ES_2020.csv", index=False)




