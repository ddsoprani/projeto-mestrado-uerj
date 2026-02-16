import geopandas as gpd
import xarray as xr
import pandas as pd
import numpy as np
import sys
import calendar
import rasterio


if len(sys.argv) < 2:
    print("ERRO: incluir o ano")
    sys.exit(1)

ano = sys.argv[1]

# Calcula Altitude
def calcAltit(lat, long):
    # Converter latitude e longitude para o sistema de coordenadas do raster
    coordinates = [(long, lat)]  # Observe que rasterio usa (lon, lat)

    # Abrir o raster e extrair os valores
    with rasterio.open("/home/danilo/Projeto-Mestrado/Orquideas/altit/wc2.1_30s_elev.tif") as altit_raster:
        altit_values = list(altit_raster.sample(coordinates))  # Extração dos valores
        altit = altit_values[0][0]  # Valor da primeira camada (ex.: mes 1)

    return altit;



# 1. Abrir dados
#ds = xr.open_dataset(f"dados-climaticos/{ano}/temp_era5_{ano}_es.nc")

#ds_atmos = xr.open_dataset(f"dados-climaticos/1987/data_stream-moda_stepType-avgad.nc")
ds_avg = xr.open_dataset(f"dados-climaticos/RJ/{ano}/data_stream-moda_stepType-avgua.nc")

#ds_precip = xr.open_dataset(f"dados-climaticos/1987/data_stream-moda_stepType-avgua.nc")
ds_acc = xr.open_dataset(f"dados-climaticos/RJ/{ano}/data_stream-moda_stepType-avgad.nc")

#Temperatura:
temp = ds_avg['t2m'] - 273.15
#ds_avg['t2m'] =  ds_avg['t2m'] - 273.15
ds_avg["t2m_c"] = ds_avg["t2m"] - 273.15 # Temp. em Kelvin
ds_avg["d2m_c"] = ds_avg["d2m"] - 273.15 # Ponto de orvalho medio


#Precipitacao  (m -> mm):
ds_acc["tp_mm"] = ds_acc["tp"] * 1000

# Pressao atmosferica (Pa -> hPa)
ds_avg["sp_hpa"] = ds_avg["sp"] / 100


# Velocidade do vento (m/s)
ds_avg["wind_speed"] = np.sqrt(ds_avg["u10"]**2 + ds_avg["v10"]**2)


# Umidade relativa (derivada de t2m e d2m)
def umidade_relativa(t, td):
    return 100 * (np.exp((17.625 * td) / (243.04 + td)) / np.exp((17.625 * t) / (243.04 + t)))

ds_avg["rh"] = umidade_relativa(ds_avg["t2m_c"], ds_avg["d2m_c"])




#ds_atmos["t2m"] = ds_atmos["t2m"] - 273.15  # Kelvin -> Celsius

#exit();

shp_es = "/home/danilo/Projeto-Mestrado/Testes_Shape_File_INPE/RJ_Municipios_2024/RJ_Municipios_2024.shp"
mun = gpd.read_file(shp_es)
mun = mun.to_crs("EPSG:4326")

# 2. Criar ponto representativo
mun["ponto"] = mun.geometry.representative_point()

# 3. Lista para guardar resultados
resultados = []

# 4. Loop por municipio
for idx, row in mun.iterrows():
    nome = row["NM_MUN"]
    codigo = row["CD_MUN"]
    ponto = row["ponto"]

    '''temp = ds_avg["t2m"].sel(
        latitude=ponto.y,
        longitude=ponto.x,
        method="nearest"
    )
    df_temp = temp.to_dataframe().reset_index()
    df_temp["municipio"] = nome
    df_temp["cd_mun"] = codigo'''

    lat = ponto.y
    lon = ponto.x


    ds_avg_ponto = ds_avg.sel(latitude=lat, longitude=lon, method="nearest")

    ds_acc_ponto = ds_acc.sel(latitude=lat, longitude=lon, method="nearest")

    df_avg = ds_avg_ponto[["t2m_c", "sp_hpa", "wind_speed", "rh"]].to_dataframe().reset_index()

    df_acc = ds_acc_ponto[["tp_mm"]].to_dataframe().reset_index()

    df_avg["ano"] = df_avg["valid_time"].dt.year
    df_avg["mes"] = df_avg["valid_time"].dt.month


    df_acc["ano"] = df_acc["valid_time"].dt.year
    df_acc["mes"] = df_acc["valid_time"].dt.month


    df = df_avg.merge(df_acc[["ano", "mes", "tp_mm"]], on=["ano", "mes"], how="left")
    #df = df_avg.merge(df_acc[["valid_time", "tp_mm"]],on="valid_time", how="left")


    df["municipio"] = nome
    df["cd_mun"] = codigo
    df["ano"] = ano
    df["mes"] = df["valid_time"].dt.month
    
    #df["altitude"] = calcAltit(lat, lon);

    df["mes"] = df["mes"].astype(int)
    ano = int(ano)
    df["dias_mes"] = df["mes"].apply(lambda m: calendar.monthrange(ano, m)[1])
    df["precip_mm_mes"] = df["tp_mm"] * df["dias_mes"]



    df = df.drop(columns=["number", "expver", "cd_mun", "tp_mm"])

    resultados.append(df)

# 5. Unir tudo
df_final = pd.concat(resultados, ignore_index=True);
#print(df_final.columns)
#exit();

#acerta as posicoes das colunas
df_final = df_final[
    [
        "municipio",
        "latitude", "longitude", 
        #"altitude",
        "ano", "mes", "valid_time",
        "t2m_c",
        "precip_mm_mes",
        "wind_speed",
        "rh",
        "sp_hpa"
    ]
]

df_final = df_final.rename(columns={
    't2m_c': 'temp_media_graus (C)',
    'sp_hpa' : 'pressao_atm (hPa)',
    'rh' : 'umidade_ar (%)',
    'wind_speed' : 'vel. vento (m/s)',
    'precip_mm_mes' : 'precipitacao_total (mm)'

})


df_final = df_final.sort_values(by=["municipio", "mes"])

# 6. Salvar
df_final.to_csv(f"dados-climaticos/RJ/{ano}/dados_climaticos_mensais_era5_municipios_RJ_{ano}.csv", sep=';', decimal=',', index=False)

print(f"Arquivo salvo com nome: dados-climaticos/RJ/{ano}/dados_climaticos_mensais_era5_municipios_RJ_{ano}.csv");


#print(df_final[["municipio", "ano", "mes", "tp_mm"]].head(12));
