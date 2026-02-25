import pandas as pd
import re

df = pd.read_csv("../MapBiomas/desmatamento-final-ES-v4.csv", sep = ';', decimal = ',')

#print(df.head);
#exit();

# Garantir que numeros com virgula virem float
#for col in df.columns[1:]:
#    df[col] = df[col].str.replace(",", ".").astype(float)


# ETAPA 1 - Transformar o banco para formato temporal
for col in df.columns[1:]:
    if df[col].dtype == "object":
        df[col] = df[col].str.replace(",", ".", regex=False).astype(float)

# Criar lista para armazenar dados reorganizados
dados = []

for col in df.columns:
    match = re.search(r'_(\d{4})$', col)
    if match:
        ano = int(match.group(1))
        
        if "Area_florestal" in col:
            tipo = "florestal"
        elif "Area_desmat" in col:
            tipo = "desmat"
        else:
            continue
        
        temp = df[["Municipio", col]].copy()
        temp["Ano"] = ano
        temp["Tipo"] = tipo
        temp.rename(columns={col: "Valor"}, inplace=True)
        dados.append(temp)

df_long = pd.concat(dados)

df_final = df_long.pivot_table(
    index=["Municipio", "Ano"],
    columns="Tipo",
    values="Valor"
).reset_index()

#print(df_final.head());

#ETAPA 2 - Criar media estadual por ano
#estado = df_final.groupby("Ano")[["florestal", "desmat"]].mean().reset_index();
estado = df_final.groupby("Ano")[["florestal", "desmat"]].sum().reset_index()


# ETAPA 3 - Visualizacao inicial

import matplotlib.pyplot as plt

estado = estado.sort_values("Ano")

'''plt.figure()
plt.plot(estado["Ano"].to_numpy(), estado["florestal"].to_numpy())
plt.xlabel("Ano")
plt.ylabel("Area florestal media")
plt.show()

plt.figure()
plt.plot(estado["Ano"].to_numpy(),estado["desmat"].to_numpy())
plt.xlabel("Ano")
plt.ylabel("Desmatamento medio")
plt.show()'''


estado = estado.rename(columns={"Ano": "ano"})
estado["var_acum_florestal"] = estado["florestal"] - estado["florestal"].iloc[0]
estado["var_acum_desmat"] = estado["desmat"] - estado["desmat"].iloc[0]

'''print(estado['var_acum_florestal']);
print();
print(estado['var_acum_desmat']);
exit();'''

print(estado.head(5));
exit();


# ETAPA 4: Tendencia linear

import statsmodels.api as sm

X = sm.add_constant(estado["Ano"])

modelo_floresta = sm.OLS(estado["florestal"], X).fit()
modelo_desmat = sm.OLS(estado["desmat"], X).fit()

print(modelo_floresta.summary())
print();
print();
print();
print(modelo_desmat.summary())


