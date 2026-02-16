import geopandas as gpd

# Shapefile dos municipios do ES
#shp_mun = "municipios_ES.shp"  # ajuste o caminho
shp_mun = "/home/danilo/Downloads/Testes_Shape_File_INPE/ES_Municipios_2024/ES_Municipios_2024.shp"
municipios = gpd.read_file(shp_mun)

# Garantir mesmo CRS do raster
#municipios = municipios.to_crs(src.crs)

print(municipios.columns)

municipios = municipios[municipios["SIGLA_UF"] == "ES"].copy()

print(len(municipios))

#municipios = municipios.to_crs(src.crs)


