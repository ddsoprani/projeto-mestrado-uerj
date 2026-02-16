import geopandas as gpd
from pathlib import Path

#municipios = gpd.read_file("/home/danilo/Projeto-Mestrado/Testes_Shape_File_INPE/SP_Municipios_2024/SP_Municipios_2024.shp")
#intermed =   gpd.read_file("/home/danilo/Projeto-Mestrado/Testes_Shape_File_INPE/SP_RG_Intermediarias_2024/SP_RG_Intermediarias_2024.shp")

# Garante mesmo CRS
#municipios = municipios.to_crs(intermed.crs)

# Intersecao espacial
#join = gpd.sjoin(municipios, intermed, predicate="intersects")

# Processa por regiao intermediaria
'''for regiao in join["NM_RGI"].unique():
    bloco = join[join["NM_RGI"] == regiao]
    bloco.to_file(f"SP_bloco_{regiao}.shp")

    # aqui voce roda:
    # - recorte MapBiomas
    # - extracao ERA5
'''


# 1. Carrega seus 11 blocos
blocos =   gpd.read_file("/home/danilo/Projeto-Mestrado/Testes_Shape_File_INPE/SP_RG_Intermediarias_2024/SP_RG_Intermediarias_2024.shp")

# 2. Carrega shapefile municipal da Mata Atlantica (INPE)
mata_municipal = gpd.read_file("/home/danilo/Projeto-Mestrado/Testes_Shape_File_INPE/municipalities_mata_atlantica_biome/municipalities_mata_atlantica_biome.shp")

# 3. Mesmo CRS
mata_municipal = mata_municipal.to_crs(blocos.crs)

# 4. Intersecao: mantem so o que esta na Mata Atlantica
blocos_mata = gpd.overlay(blocos, mata_municipal, how="intersection")

#print(blocos_mata.columns);
'''print(blocos_mata['NM_RGINT'].nunique());
print(blocos_mata['NM_REGIA'].nunique());
print(blocos_mata['nome'].nunique());
print(blocos_mata['geocodigo'].nunique());
print(blocos_mata["anoderefer"].unique());
print(blocos_mata["SIGLA_UF"].unique());
'''


for nome in sorted(blocos_mata["nome"].unique()):
    print(nome)


exit();

# 5. Ver quantos blocos sobraram
print(blocos_mata["NM_RGINT"].nunique())

# quantos municipios por bloco?
blocos_mata.groupby("NM_RGINT")["NM_MUN"].nunique()

# area total por bloco (em km2)
blocos_mata["area_km2"] = blocos_mata.geometry.area / 1e6
blocos_mata.groupby("NM_RGINT")["area_km2"].sum()

exit();


# 6. Exporta por regiao
for regiao in blocos_mata["NM_RGINT"].unique():
    pasta = Path(regiao)
    pasta.mkdir(parents=True, exist_ok=True)
    
    bloco = blocos_mata[blocos_mata["NM_RGINT"] == regiao]
    bloco.to_file(f"{regiao}/SP_bloco_{regiao}_MataAtlantica.shp")

print("Arquivos criados!");


