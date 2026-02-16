import geopandas as gpd
import xarray as xr
import matplotlib.pyplot as plt

# abrir dados
ds = xr.open_dataset("temp_era5_2020_es.nc")
shp_es = "/home/danilo/Projeto-Mestrado/Testes_Shape_File_INPE/ES_Municipios_2024/ES_Municipios_2024.shp"
mun = gpd.read_file(shp_es).to_crs("EPSG:4326")

# criar ponto representativo
mun["ponto"] = mun.geometry.representative_point()

# escolher municipios para validacao
municipios_teste = ["Anchieta", "Linhares", "Alegre"]
mun_test = mun[mun["NM_MUN"].isin(municipios_teste)]

# plot
fig, ax = plt.subplots(figsize=(6, 6))
mun_test.plot(ax=ax, edgecolor="black", facecolor="none")
mun_test["ponto"].plot(ax=ax, color="red", markersize=50)

ax.set_title("Validacao espacial - pontos representativos")
plt.show()

