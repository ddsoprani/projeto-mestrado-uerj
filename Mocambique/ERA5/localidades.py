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

provincias = ["Nampula", "Zambezia", "Sofala", "Inhambane"]

# 1. Abrir dados
ds_avg = xr.open_dataset(f"dados-climaticos/{ano}/data_stream-moda_stepType-avgua.nc")

ds_acc = xr.open_dataset(f"dados-climaticos/{ano}/data_stream-moda_stepType-avgad.nc")

#Temperatura:
temp = ds_avg['t2m'] - 273.15
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


shp_moc = "/home/danilo/Projeto-Mestrado/Mocambique/GEE/Mocambique_Localidade/Mocambique_Localidade.shp";
gdf = gpd.read_file(shp_moc).to_crs("EPSG:4326")

# 2. Criar ponto representativo
gdf["ponto"] = gdf.geometry.representative_point()

#localidades_teste = ["Funhalouro", "Govuro", "Homoine", "Inhassoro", "Dondo", "Chinde", "Meconta", "Pebane"]
#gdf_sel = gdf[gdf["NAME_2"].isin(localidades_teste)]
#print(gdf_sel.head());
#exit();

# 3. Lista para guardar resultados
resultados = []

# 4. Loop por municipio/localidade
for idx, row in gdf.iterrows():
    provincia = row["NAME_1"]
    distrito = row["NAME_2"]
    localidade = row["NAME_3"];

    # Filtrar somente as 4 provincias de interesse
    if provincia not in provincias:
        continue
    
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


    df["distrito"] = distrito
    df["provincia"] = provincia
    df["localidade"] = localidade;
    df["ano"] = ano
    df["mes"] = df["valid_time"].dt.month
    
    df["mes"] = df["mes"].astype(int)
    ano = int(ano)
    df["dias_mes"] = df["mes"].apply(lambda m: calendar.monthrange(ano, m)[1])
    df["precip_mm_mes"] = df["tp_mm"] * df["dias_mes"]



    #df = df.drop(columns=["number", "expver", "cd_mun", "tp_mm"])

    resultados.append(df)

# 5. Unir tudo
df_final = pd.concat(resultados, ignore_index=True);
#print(df_final.head())
#exit();

#acerta as posicoes das colunas
df_final = df_final[
    [
        "provincia",
        "distrito",
        "localidade", 
        "latitude", "longitude", 
        #"altitude",
        "ano", "mes",
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


df_final = df_final.sort_values(by=["provincia", "distrito", "localidade", "mes"])
#print(df_final.head(20));

# 6. Salvar
df_final.to_csv(f"dados-climaticos/{ano}/dados_climaticos_mensais_era5_localidades_Mocambique_{ano}.csv", sep=';', decimal=',', index=False)

print(f"Arquivo salvo com nome: dados-climaticos/{ano}/dados_climaticos_mensais_era5_localidades_Mocambique_{ano}.csv");


#print(df_final[["municipio", "ano", "mes", "tp_mm"]].head(12));
