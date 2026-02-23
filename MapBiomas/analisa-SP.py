import geopandas as gpd
import rasterio
from rasterio.mask import mask
import numpy as np
import pandas as pd
import sys
import os
import csv
import glob



if len(sys.argv) < 2:
    print("ERRO: incluir o nome do arquivo")
    sys.exit(1)


# variaveis globais 

arquivo = sys.argv[1]
ano = arquivo.split("_")[0]
ano_anterior = int(ano) - 1;
resultados = []
base_dir = "RECORTA-SP"

coverage = {}

with open(f"/home/danilo/Projeto-Mestrado/Coverage/CSV-SP/_{ano_anterior}_cobertura_por_municipio_SP.csv", newline="", encoding="utf-8-sig") as f:
    leitor = csv.DictReader(f, delimiter=";")

    for linha in leitor:
        municipio = linha["Municipio"]
        sem_dados = linha["Sem dados"]
        formacao_flor = linha["Formação Florestal"]
        mangue = linha["Mangue"]

        coverage[municipio] = [sem_dados, formacao_flor, mangue]


#print(coverage['Altair']);
#exit();



def geraResult(resultados, shp_sp):

    # Lendo o shapefile
    sp = gpd.read_file(shp_sp)

    print(sp.crs)

    #PASSO 4:

    tif_path = arquivo;

    src = rasterio.open(tif_path)

    print(src.crs);


    # PASSO 5:
    if sp.crs != src.crs:
        sp = sp.to_crs(src.crs)


    #print(rj.crs)
    #print(src.crs)


    #print(rj.crs == src.crs)


    # PASSO 6

    # Geometrias de SP
    geoms = sp.geometry.values

    # Recorte (mask)
    raster_sp, transform = mask(
        src,
        geoms,
        crop=True,
        nodata=0
    )

    src.close()


    raster_sp = raster_sp[0]


    # PASSO 7:

    print("Shape do raster SP:", raster_sp.shape)
    print("Valores únicos:", np.unique(raster_sp))

    #PASSO 8:
    #print(raster_rj[:10, :10])


    # PASSO

    # [4,6] são as classes de desmatamento propriamemte ditos, segundo site do MapBiomas
    mask_desmat = np.isin(raster_sp, [4, 6])

    #print(mask_desmat[:10, :10])


    #PASSO:

    pixels_desmat = np.sum(mask_desmat)
    print(f"Pixels com desmatamento em {ano} no SP:", pixels_desmat)


    area_sp_ha = pixels_desmat * 0.09


    area_sp_km2 = area_sp_ha / 100


    print(f"Área desmatada em {ano} em {shp_sp} SP: {area_sp_ha:.2f} ha ({area_sp_km2:.2f} km²)")


    # AGORA A PARTE DOS MUNICIPIOS


    # Shapefile dos municípios de SP
    municipios = gpd.read_file(shp_sp)

    # Garantir mesmo CRS do raster
    municipios = municipios.to_crs(src.crs)

    #print(municipios.columns);


    #tif_path = "2022_deforestation_annual_1-1-1_74215b40-a389-43b6-aa16-ebdcb7b9a252.tif"
    tif_path = arquivo;
    src = rasterio.open(tif_path)


    #PASSO: Loop por município (código principal):

    #resultados = []
    col_nome = "NM_MUN"


    for idx, row in municipios.iterrows():
        nome_mun = row[col_nome]
        '''if nome_mun != 'Altair':
            continue;'''
        geom = [row.geometry]

        try:
            raster_mun, _ = mask(
                src,
                geom,
                crop=True,
                nodata=0
            )

            raster_mun = raster_mun[0]

            # Mascara de desmatamento
            mask_desmat = np.isin(raster_mun, [4, 6])
            pixels_desmat = np.sum(mask_desmat)

            area_ha = pixels_desmat * 0.09
            area_km2 = area_ha / 100

            cover_forest = coverage[nome_mun][1].replace(",",".");
            cover_mague  = coverage[nome_mun][2].replace(",",".");
            cover = float(cover_forest) + float(cover_mague);
            
            
            if float(cover) != 0:
                percent = (float(area_km2) / float(cover)) * 100;
                percent = round(percent, 2);
            else:
                percent = '-';
            
                #print("pixels_desmat: ", pixels_desmat);
                #print("Cobertura vegetal de ", nome_mun, ": ", coverage[nome_mun], " ------ ", cover);
                #print("porcentagem:", percent);
                #print(area_km2, " / ",  cover);
                #exit();

            resultados.append({
                "municipio": nome_mun,
                f"cobertura_vegetal_{ano_anterior}": cover,
                f"pixels_desmat_{ano}": pixels_desmat,
                f"area_desmat_ha_{ano}": area_ha,
                f"area_desmat_km2_{ano}": area_km2,
                f"percentual": percent
            })

        except Exception as e:
            print(f"Erro no municipio {nome_mun}: {e}")


    src.close();
    print("Tamanho: ", len(resultados));
    #return resultados;
    
    #################################################################
    #################### Fim da funcao geraResult ###################
    #################################################################


################### Codigo principal ###########################


#Lista as 11 regioes de SP
shapes_por_regiao = {}

for regiao in os.listdir(base_dir):
    caminho_regiao = os.path.join(base_dir, regiao)

    if os.path.isdir(caminho_regiao):
        shapes = glob.glob(os.path.join(caminho_regiao, "*.shp"))
        for shp in shapes:
            shapes_por_regiao[regiao] = os.path.basename(shp);


for shp in shapes_por_regiao:
    pasta = "RECORTA-SP/" + shp + "/" + shapes_por_regiao[shp];
    print(pasta);
    geraResult(resultados, pasta);
    print();



#PASSO: Criar o DataFrame final

#df_resultados = pd.DataFrame(resultados)
df_municipios = pd.DataFrame(resultados);

#df_altair = df_municipios[df_municipios['municipio'] == 'Altair']
#print(df_altair)

#Junta os municípios pelo nome (pois pode ter gerado mais de um):
#df_municipios = (df_municipios.groupby("municipio", as_index=False).sum());

df_municipios = (
    df_municipios
    .groupby("municipio", as_index=False)
    .agg({
        f"cobertura_vegetal_{ano_anterior}": "first",  # ou "mean"
        f"pixels_desmat_{ano}": "sum",
        f"area_desmat_ha_{ano}": "sum",
        f"area_desmat_km2_{ano}": "sum",
        "percentual": "sum"
    })
)


#df_altair = df_municipios[df_municipios['municipio'] == 'Altair']
#print(df_altair)


#print(df_resultados.head())
#print(df_municipios.head(20));
#exit();



# PASSO: Checagem de consistencia (importantissima):

#print("Soma municipal (ha):", df_municipios[f"area_desmat_ha_{ano}"].sum())
#print("Total estadual (ha):", area_sp_ha);


# PASSO: Exportar para CSV:

df_municipios.to_csv(
    f"CSV-SP/_{ano}_desmatamento_municipios_SP.csv",
    sep=';',
    decimal=',',
    index=False
);

print("Arquivo criado!");
