import rasterio
from rasterio.windows import Window

# Caminhos
raster_path = "2024_deforestation_annual_1-1-1_18787e80-dd7a-4641-965d-0c410964f705.tif"

# BOUNDING BOX DO ES (IBGE)
min_lon, max_lon = -41.52, -39.19
min_lat, max_lat = -21.30, -17.89

with rasterio.open(raster_path) as src:

    # Transformando coordenadas em indices de linha/coluna
    row_min, col_min = src.index(min_lon, max_lat)  # canto superior esquerdo
    row_max, col_max = src.index(max_lon, min_lat)  # canto inferior direito

    # Garantir que os valores sao validos
    row_min, row_max = sorted([row_min, row_max])
    col_min, col_max = sorted([col_min, col_max])

    bloco_altura = 2000
    bloco_largura = 2000

    encontrou = False

    for row in range(row_min, row_max, bloco_altura):
        for col in range(col_min, col_max, bloco_largura):

            altura = min(bloco_altura, row_max - row)
            largura = min(bloco_largura, col_max - col)

            window = Window(col_off=col, row_off=row, width=largura, height=altura)
            bloco = src.read(1, window=window)

            # filtrando NODATA
            if src.nodata is not None:
                bloco = bloco[bloco != src.nodata]

            if bloco.size > 0:
                unicos = set(bloco.ravel())
                if max(unicos) > 0:
                    print("Valores encontrados:", unicos)
                    encontrou = True
                    break

        if encontrou:
            break

if not encontrou:
    print("Nenhum valor > 0 encontrado na regiao do ES.")

