import geopandas as gpd
from pathlib import Path

# 1. Carrega municipios de SP (IBGE)
mun_sp = gpd.read_file("/home/danilo/Projeto-Mestrado/Testes_Shape_File_INPE/SP_Municipios_2024/SP_Municipios_2024.shp")

# 2. Carrega limite do bioma Mata Atlantica (INPE)
mata = gpd.read_file("/home/danilo/Projeto-Mestrado/Testes_Shape_File_INPE/municipalities_mata_atlantica_biome/municipalities_mata_atlantica_biome.shp").to_crs(mun_sp.crs)

# 3. Recorta municipios de SP pela Mata Atlantica
mun_sp_mata = gpd.overlay(mun_sp, mata, how="intersection", keep_geom_type=True)
#print(mun_sp_mata.columns);
#print(mun_sp_mata);
#print(mun_sp_mata["SIGLA_UF"].unique());
#print(mun_sp_mata["NM_MUN"].nunique());
#print(mun_sp_mata["NM_RGINT"].nunique());
#exit();


# 4. Carrega regioes intermediarias de SP (IBGE)
reg_sp = gpd.read_file("/home/danilo/Projeto-Mestrado/Testes_Shape_File_INPE/SP_RG_Intermediarias_2024/SP_RG_Intermediarias_2024.shp").to_crs(mun_sp.crs)

# 5. Associa cada pedaco de municipio a sua regiao intermediaria
mun_sp_mata_reg = gpd.sjoin(mun_sp_mata, reg_sp, predicate="intersects")

mun_sp_mata_reg = mun_sp_mata_reg.rename(columns={
    "NM_RGINT_right": "NM_RGINT",
    "CD_RGINT_right": "CD_RGINT",
    "SIGLA_UF_right": "SIGLA_UF"
})

# remove as colunas duplicadas vindas do _left
cols_to_drop = [c for c in mun_sp_mata_reg.columns if c.endswith("_left")]
mun_sp_mata_reg = mun_sp_mata_reg.drop(columns=cols_to_drop)



# 6. (Opcional) Dissolve por regiao intermediaria
regioes_sp_mata = mun_sp_mata_reg.dissolve(by="NM_RGINT")



# Deve dar 11 ou menos (se alguma regiao for 100% Cerrado)
#print(regioes_sp_mata["NM_RGINT"].nunique());

# Deve dar <= 645
#print(mun_sp_mata_reg["CD_MUN"].nunique());

# Nunca deve aparecer PR
#print(mun_sp_mata_reg["SIGLA_UF"].unique());

#print(mun_sp_mata_reg["NM_RGINT"].nunique())
#print(mun_sp_mata_reg["SIGLA_UF"].unique())
#print(mun_sp_mata_reg["NM_MUN"].nunique())


for regiao in mun_sp_mata_reg['NM_RGINT'].unique():
    pasta = Path(regiao)
    pasta.mkdir(parents=True, exist_ok=True)
    
    bloco = mun_sp_mata_reg[mun_sp_mata_reg["NM_RGINT"] == regiao]
    bloco.to_file(f"{regiao}/SP_bloco_{regiao}_MataAtlantica.shp", )
    

print("Arquivos criados!");
