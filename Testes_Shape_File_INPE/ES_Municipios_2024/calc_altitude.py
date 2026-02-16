import geopandas as gpd

gdf = gpd.read_file("ES_Municipios_2024.shp")
print(gdf.crs)
print(gdf.columns)
print(gdf.head())

