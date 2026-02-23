import pandas as pd
import numpy as np

def twfe_from_csv(temp_path, forest_path):

    # ----------------------------
    # 1 Ler arquivos
    # ----------------------------
    df_temp = pd.read_csv(temp_path, sep = ',', decimal = '.');
    df_forest = pd.read_csv(forest_path, sep=',', decimal = '.');


    # Resetar índice para virar coluna
    df_temp_long = df_temp.melt(id_vars='municipio', var_name='Ano', value_name='Temperatura')
    df_cob_long = df_forest.melt(id_vars='municipio', var_name='Ano', value_name='Cobertura')

    
    # Juntar
    df = pd.merge(df_temp_long, df_cob_long, on=['municipio', 'Ano'])

    #Garantir tipos corretos
    df['Ano'] = df['Ano'].astype(int)
    df['Temperatura'] = df['Temperatura'].astype(float)
    df['Cobertura'] = df['Cobertura'].astype(float)

    #print(df.head(100));
    #print("--------------------------------------------------");
    
    df = df.dropna(subset=['Cobertura'])

    '''print(df.isna().sum())
    print("--------------------------------------------------");
    print(df[df[['Temperatura','Cobertura']].isna().any(axis=1)].head())
    exit();'''

    #print(df.groupby("municipio")["Cobertura"].std().describe());
    #print("--------------------------------------------------");

    #print(df["Cobertura"].describe())
    #print("--------------------------------------------------");

    #print(df[df["Cobertura"] > 1])
    #print("--------------------------------------------------");

    #print((df["Cobertura"] > 1).sum());
    #print((df["Cobertura"] > 1).mean());

    #print(df[df["Cobertura"] > 1]["municipio"].nunique());
    #print(df[df["Cobertura"] > 1]["municipio"].value_counts().head(20))

    #print('------------------------------------------------');

    #print(df[df["municipio"] == "São Lourenço da Serra"][["Ano", "Cobertura"]]);



    #exit();


    #print(df.shape)
    #print(df['municipio'].nunique())
    #print(df['Ano'].nunique())


    
    # Passo: Criar dummies
    # Dummies município
    dummies_mun = pd.get_dummies(df['municipio'], drop_first=True)

    # Dummies ano
    dummies_ano = pd.get_dummies(df['Ano'], drop_first=True)

    # Variável principal
    X_main = df[['Cobertura']]

    # Matriz X completa
    X = pd.concat([X_main, dummies_mun, dummies_ano], axis=1)

    # Variável dependente
    Y = df['Temperatura']

    
    
    # Passo: ADICIONAR CONSTANTE
    X.insert(0, 'const', 1)

    

    #Passo: Estimar OLS matricial
    X = X.astype(float)
    Y = Y.astype(float)

    X_mat = X.values
    Y_mat = Y.values.reshape(-1, 1)

    beta = np.linalg.inv(X_mat.T @ X_mat) @ (X_mat.T @ Y_mat)

    beta_cobertura = beta[1][0]   # índice 1 porque 0 é constante

    print("Beta Cobertura:", beta_cobertura)


    #Cálculo do erro padrão OLS

    n = X_mat.shape[0]
    k = X_mat.shape[1]

    # Resíduos
    residuals = Y_mat - X_mat @ beta

    # Variância do erro
    sigma2 = (residuals.T @ residuals) / (n - k)

    # Matriz variância-covariância
    var_beta = sigma2[0][0] * np.linalg.inv(X_mat.T @ X_mat)

    # Erro padrão do beta da cobertura
    se_beta = np.sqrt(var_beta[1][1])

    print("Erro padrão:", se_beta)

    # Estatística t
    t_stat = beta_cobertura / se_beta
    print("t-valor:", t_stat)



    # PASSO: cluster por município
    
    #Preparações
    XtX_inv = np.linalg.inv(X_mat.T @ X_mat)
    residuals = Y_mat - X_mat @ beta 

    #Identificar clusters
    municipios = df['municipio'].values
    unique_municipios = np.unique(municipios)

    k = X_mat.shape[1]
    cluster_sum = np.zeros((k, k))

    #Loop por município
    for m in unique_municipios:
        idx = np.where(municipios == m)[0]
        X_g = X_mat[idx, :]
        u_g = residuals[idx]
        cluster_sum += X_g.T @ (u_g @ u_g.T) @ X_g
    

    #Variância clusterizada
    var_cluster = XtX_inv @ cluster_sum @ XtX_inv
    se_cluster = np.sqrt(np.diag(var_cluster))
    se_beta_cluster = se_cluster[1]
    t_cluster = beta[1][0] / se_beta_cluster
    print("Erro padrão cluster:", se_beta_cluster)
    print("t-valor cluster:", t_cluster)




#beta = twfe_from_csv("temperatura_media_anual_municipios-ES.csv", "desmatamento_apenas_ES.csv")
#beta = twfe_from_csv("temperatura_media_anual_municipios-ES.csv", "area_verde_apenas_ES.csv")

beta = twfe_from_csv("temperatura_media_anual_municipios-SP.csv", "percentual_SP3.csv")
#print("Beta estimado:", beta)

