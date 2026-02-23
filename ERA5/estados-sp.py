import geopandas as gpd
import xarray as xr
import pandas as pd
import numpy as np
import sys
import calendar
import rasterio
import os
import csv
import glob


if len(sys.argv) < 2:
    print("ERRO: incluir o ano")
    sys.exit(1)

ano = sys.argv[1]
resultados = []


# 1. Abrir dados
#ds = xr.open_dataset(f"dados-climaticos/{ano}/temp_era5_{ano}_es.nc")

#ds_atmos = xr.open_dataset(f"dados-climaticos/1987/data_stream-moda_stepType-avgad.nc")
ds_avg = xr.open_dataset(f"dados-climaticos/SP/{ano}/data_stream-moda_stepType-avgua.nc")

#ds_precip = xr.open_dataset(f"dados-climaticos/1987/data_stream-moda_stepType-avgua.nc")
ds_acc = xr.open_dataset(f"dados-climaticos/SP/{ano}/data_stream-moda_stepType-avgad.nc")

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

#shp_es = "/home/danilo/Projeto-Mestrado/Testes_Shape_File_INPE/RJ_Municipios_2024/RJ_Municipios_2024.shp"


def geraResult(resultados, shp_sp, ano):
    mun = gpd.read_file(shp_sp)
    mun = mun.to_crs("EPSG:4326")

    # 2. Criar ponto representativo
    mun["ponto"] = mun.geometry.representative_point()

    # 3. Lista para guardar resultados

    # 4. Loop por municipio
    for idx, row in mun.iterrows():
        nome = row["NM_MUN"]
        codigo = row["CD_MUN"]
        ponto = row["ponto"]

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




################### Codigo principal ###########################

#Lista as 11 regioes de SP
base_dir = "/home/danilo/Projeto-Mestrado/MapBiomas/RECORTA-SP/"
shapes_por_regiao = {}

for regiao in os.listdir(base_dir):
    caminho_regiao = os.path.join(base_dir, regiao)

    if os.path.isdir(caminho_regiao):
        shapes = glob.glob(os.path.join(caminho_regiao, "*.shp"))
        for shp in shapes:
            shapes_por_regiao[regiao] = os.path.basename(shp);


for shp in shapes_por_regiao:
    pasta = base_dir + shp + "/" + shapes_por_regiao[shp];
    print(pasta);
    geraResult(resultados, pasta, ano);
    print();




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

'''df_agrupado = (
    df_final.groupby(["municipio", "ano", "mes", "valid_time"], as_index=False).agg({
        "latitude": "first",   # pega o primeiro valor
        "longitude": "first",  # pega o primeiro valor
        "temp_media_graus (C)": "mean",
        "precipitacao_total (mm)": "mean",
        "vel. vento (m/s)": "mean",
        "umidade_ar (%)": "mean",
        "pressao_atm (hPa)": "mean"
    })
)'''

#print(df_final.dtypes)
#exit();

df_final["municipio"] = df_final["municipio"].str.strip()
df_final["ano"] = df_final["ano"].astype(str).str.strip().astype(int)
df_final["mes"] = df_final["mes"].astype(int)

#print(df_final.dtypes)


df_agrupado = (
    df_final
    .groupby(["municipio", "ano", "mes"], as_index=False)
    .mean(numeric_only=True)
)

df_agrupado.duplicated(subset=["municipio","ano","mes"]).sum()

df_agrupado["latitude"] = df_agrupado["latitude"].round(2)
df_agrupado["longitude"] = df_agrupado["longitude"].round(2)



#print(df_agrupado)

#Junta os municípios pelo nome (pois pode ter gerado mais de um):
#df_final = (df_final.groupby("municipio", as_index=False).sum());

# 6. Salvar
df_agrupado.to_csv(f"dados-climaticos/SP/{ano}/dados_climaticos_mensais_era5_municipios_SP_{ano}-v5.csv", sep=';', decimal=',', index=False)

print(f"Arquivo salvo com nome: dados-climaticos/SP/{ano}/dados_climaticos_mensais_era5_municipios_SP_{ano}-v5.csv");


#print(df_final[["municipio", "ano", "mes", "tp_mm"]].head(12));
