import xarray as xr
import geopandas as gpd
import pandas as pd
import rioxarray
import sys

import xarray as xr

if len(sys.argv) < 2:
    print("ERRO: incluir o ano")
    sys.exit(1)

ano = sys.argv[1]

# Temperatura media ou outra variavel continua
ds_avg = xr.open_dataset(f"dados-climaticos/{ano}/data_stream-moda_stepType-avgua.nc")

# Precipitacao ou variavel acumulada
ds_acc = xr.open_dataset(f"dados-climaticos/{ano}/data_stream-moda_stepType-avgad.nc")


# Shapefile e distritos de teste
shp_moc = "/home/danilo/Projeto-Mestrado/Mocambique/GEE/Mocambique_Distritos/Mocambique_Distritos.shp";
gdf = gpd.read_file(shp_moc).to_crs("EPSG:4326")

#distritos_teste = ["Funhalouro", "Govuro", "Homoine", "Inhassoro", "Dondo", "Chinde", "Meconta", "Pebane"]
#gdf_sel = gdf[gdf["NAME_2"].isin(distritos_teste)]


resultados = []

lat_norte = -12
lat_sul   = -26
lon_oeste = 32
lon_leste = 41


#for idx, row in gdf_sel.iterrows():
for idx, row in gdf.iterrows():
    provincia = row["NAME_1"]
    distrito = row["NAME_2"]
    geom = [row.geometry]

    # Clip ERA5 media (t2m)
    ds_clip_t2m = ds_avg["t2m"].rio.write_crs("EPSG:4326").rio.clip(geom, gdf_sel.crs, drop=True)
    temp_c = ds_clip_t2m - 273.15  # Kelvin -> Celsius
    media_temp = float(temp_c.mean().values)


    # Clip ERA5 precipitacao acumulada (tp)
    ds_clip_tp = ds_acc["tp"].rio.write_crs("EPSG:4326").rio.clip(geom, gdf_sel.crs, drop=True)
    sum_tp = float(ds_clip_tp.sum().values) * 1000;

    #Velocidade do vento:
    # Subset da bounding box do distrito
    u = ds_avg["u10"].sel(latitude=slice(lat_norte, lat_sul), longitude=slice(lon_oeste, lon_leste))
    v = ds_avg["v10"].sel(latitude=slice(lat_norte, lat_sul), longitude=slice(lon_oeste, lon_leste))
    # Velocidade do vento
    vento = np.sqrt(u**2 + v**2)
    # Media anual e espacial
    vento_media_ms = vento.mean(dim=["valid_time","latitude","longitude"]).values

    
    #Pressao Atmosferica
    sp = ds_avg["sp"].sel(latitude=slice(lat_norte, lat_sul), longitude=slice(lon_oeste, lon_leste))
    pressao_media_hpa = (sp.mean(dim=["valid_time","latitude","longitude"]).values) / 100

    
    #Umidade Relativa do Ar
    t = ds_avg["t2m"].sel(latitude=slice(lat_norte, lat_sul), longitude=slice(lon_oeste, lon_leste)) - 273.15  # K -> C
    td = ds_avg["d2m"].sel(latitude=slice(lat_norte, lat_sul), longitude=slice(lon_oeste, lon_leste)) - 273.15 # K -> C
    # Formula aproximada da umidade relativa (%)
    ur = 100 * (np.exp((17.625*td)/(243.04+td)) / np.exp((17.625*t)/(243.04+t)))
    # Media anual e espacial
    ur_media = ur.mean(dim=["valid_time","latitude","longitude"]).values



    resultados.append({
        "distrito"      : distrito,
        "provincia"     : provincia,
        "temp_media_C"  : media_temp,
        "prec_total_mm" : sum_tp,
        "vento"         : vento_media_ms,
        "pressao_atm"   : pressao_media_hpa,
        "umidade_rel_ar": ur_media
    })

df_result = pd.DataFrame(resultados)
print(df_result)



