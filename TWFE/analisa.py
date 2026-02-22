import pandas as pd
import numpy as np

def twfe_from_csv(temp_path, forest_path):

    # ----------------------------
    # 1 Ler arquivos
    # ----------------------------
    df_temp = pd.read_csv(temp_path, sep = ',', decimal = '.');
    df_forest = pd.read_csv(forest_path, sep=',', decimal = '.');
    
    #print(df_temp.head(5));
    #print(df_forest.head(5));

    #print("df_temp:", df_temp.shape)
    #print("df_forest:", df_forest.shape)

    #exit();

    # ----------------------------
    # 2 Garantir que municipios estao alinhados
    # ----------------------------
    df_temp = df_temp.sort_values("municipio").reset_index(drop=True)
    df_forest = df_forest.sort_values("municipio").reset_index(drop=True)

    if not all(df_temp["municipio"] == df_forest["municipio"]):
        raise ValueError("Municipios nao coincidem entre os arquivos.")

    municipios = df_temp["municipio"].values

    # ----------------------------
    # 3 Remover coluna de nome e converter para numpy
    # ----------------------------
    Y = df_temp.drop(columns=["municipio"]).to_numpy(dtype=float)
    X = df_forest.drop(columns=["municipio"]).to_numpy(dtype=float)

    N, T = Y.shape

    # ----------------------------
    # 4 Calcular medias
    # ----------------------------
    mean_Y_global = np.mean(Y)
    mean_X_global = np.mean(X)

    mean_Y_i = np.mean(Y, axis=1, keepdims=True)
    mean_X_i = np.mean(X, axis=1, keepdims=True)

    mean_Y_t = np.mean(Y, axis=0, keepdims=True)
    mean_X_t = np.mean(X, axis=0, keepdims=True)

    # ----------------------------
    # 5 Dupla centralizacao
    # ----------------------------
    Y_tilde = Y - mean_Y_i - mean_Y_t + mean_Y_global
    X_tilde = X - mean_X_i - mean_X_t + mean_X_global

    # ----------------------------
    # 6 Estimar beta (OLS simples)
    # ----------------------------
    numerator = np.sum(X_tilde * Y_tilde)
    denominator = np.sum(X_tilde * X_tilde)

    beta_hat = numerator / denominator

    return beta_hat




#beta = twfe_from_csv("ex1-temp.csv", "ex1-floresta.csv")
#beta = twfe_from_csv("temperatura_media_anual_municipios-ES.csv", "desmatamento_apenas_ES.csv")
#beta = twfe_from_csv("temperatura_media_anual_municipios-ES.csv", "area_verde_apenas_ES.csv")
beta = twfe_from_csv("temperatura_media_anual_municipios-ES.csv", "percentual_ES.csv")
print("Beta estimado:", beta)

