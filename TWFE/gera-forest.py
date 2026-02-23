import pandas as pd
import csv


# Ler arquivo
df = pd.read_csv("desmatamento-final-SP-v5.csv", sep=";", decimal = ',')

# Remover colunas que começam com 'Area_florestal_'
df = df.loc[:, ~df.columns.str.startswith("Area_desmat_km2_")]

# Dicionário final
area = {}

with open('Areas_Municipais.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        # Filtrar apenas Espirito Santo (CD_UF = 32)
        if row['CD_UF'] == '35':

            nome_municipio = row['NM_MUN'].strip()

            # Converter vírgula decimal para ponto
            area_str = row['AR_MUN_2024'].replace(',', '.')
            area_float = float(area_str)

            area[nome_municipio] = area_float

# Teste: imprimir algumas entradas
#for municipio in list(area.keys())[:5]:
#    print(municipio, area[municipio])





# Renomear colunas 'Area_desmat_km2_1987' -> '1987'
novos_nomes = {}

for col in df.columns:
    if col.startswith("Area_florestal_"):
        ano = col.replace("Area_florestal_", "")
        novos_nomes[col] = ano

df = df.rename(columns=novos_nomes)

df = df.set_index('Municipio');

col_anos = [col for col in df.columns if str(col).isdigit()]

for municipio in df.index:
    if municipio in area:
        #df.loc[municipio] = df.loc[municipio] / area[municipio]
        df.loc[municipio, col_anos] = (df.loc[municipio, col_anos] / area[municipio])

    else:
        print(f"Municipio nao encontrado no vetor area: {municipio}")

# Salvar novo CSV
df.to_csv("percentual_SP3.csv")
