import xarray as xr

#ds = xr.open_dataset("temp_era5_2020_es.nc")
# avgua -> (temperatura, vento, pressão, etc.)
#print(ds);

ds_avg = xr.open_dataset("dados-climaticos/1987/data_stream-moda_stepType-avgua.nc")
print("Saída do primeiro:");
print();
print();
print(ds_avg);

print();
print();
print("Saída do segundo:");
print();
ds_acc = xr.open_dataset("dados-climaticos/1987/data_stream-moda_stepType-avgad.nc")
print(ds_acc)

#exit();


#temp_c = ds['t2m'] - 273.15
temp_c = ds_avg['t2m'] - 273.15
print(temp_c.mean().values);


temp_es_mensal = temp_c.mean(dim=['latitude', 'longitude'])
print(temp_es_mensal);



import pandas as pd
df = temp_es_mensal.to_dataframe(name='temp_c').reset_index()
print(df);


df.to_csv("dados-climaticos/1987/temperatura_media_mensal_es_1987.csv", index=False);
print("Arquivo salvo!");



