import pandas as pd
import geopandas as gpd
import xarray as xr
import rioxarray

shp_es = "/home/danilo/Projeto-Mestrado/Testes_Shape_File_INPE/ES_Municipios_2024/ES_Municipios_2024.shp"
mun = gpd.read_file(shp_es) # Aqui temos um poligono vetorial.
#print(mun.head())
#print(mun.crs)


#Passo 2: Reprojetar municipios para WGS84
mun = mun.to_crs("EPSG:4326");


# Passo 3: Preparar o ERA5 corretamente

ds = xr.open_dataset("temp_era5_2020_es.nc") # Abre um raster em grade regular (lat x lon)

# Renomear coordenadas
ds = ds.rename({'latitude': 'y', 'longitude': 'x'})

# Definir CRS do ERA5
ds = ds.rio.write_crs("EPSG:4326");


#Passo 4: Selecionar UM municipio

mun_anchieta = mun[mun["NM_MUN"] == "Anchieta"]
print(mun_anchieta);



#Passo 5: Recortar o raster ERA5
temp_c = ds["t2m"] - 273.15

temp_clip = temp_c.rio.clip(
    mun_anchieta.geometry,
    mun_anchieta.crs,
    drop=True
);


#Passo 6: Media mensal do municipio

temp_mensal = temp_clip.mean(dim=["y", "x"])

print(temp_mensal);


#Passo 7: DataFrame final

import pandas as pd

df = temp_mensal.to_dataframe(name="temp_c").reset_index()

df["municipio"] = "Anchieta"

#print(df);


#Limpeza:

df_limpo = df[["valid_time", "temp_c", "municipio"]].copy()
df_limpo["ano"] = df_limpo["valid_time"].dt.year
df_limpo["mes"] = df_limpo["valid_time"].dt.month
df_limpo = df_limpo.drop(columns="valid_time")
print(df_limpo);
df_limpo.to_csv("Anchieta_temp_2020.csv");




