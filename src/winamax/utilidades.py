import pandas as pd
import numpy as np

def media(valores):
    if not valores:
        raise ValueError("La lista no puede estar vacía")
    return sum(valores) / len(valores)

def detectar_nulos(df_train, df_test, columnas):
    """
    Cuenta los valores inexistentes (NaN) en las columnas seleccionadas
    para los conjuntos de entrenamiento y test.
    """
    nulos_train = df_train[columnas].isna().sum().to_dict()
    nulos_test = df_test[columnas].isna().sum().to_dict()
    return {"train": nulos_train, "test": nulos_test}

def preprocesar_eliminar_filas(df_train, df_test, columnas):
    """
    Elimina las filas que contengan NaN en las columnas seleccionadas.
    """
    train_limpio = df_train.dropna(subset=columnas).copy()
    test_limpio = df_test.dropna(subset=columnas).copy()
    return train_limpio, test_limpio

def preprocesar_media(df_train, df_test, columnas):
    """
    Rellena los nulos usando la media calculada EXCLUSIVAMENTE en el train.
    """
    train_limpio = df_train.copy()
    test_limpio = df_test.copy()
    
    for col in columnas:
        media_val = train_limpio[col].mean()
        train_limpio[col] = train_limpio[col].fillna(media_val)
        test_limpio[col] = test_limpio[col].fillna(media_val)
        
    return train_limpio, test_limpio

def preprocesar_mediana(df_train, df_test, columnas):
    """
    Rellena los nulos usando la mediana calculada EXCLUSIVAMENTE en el train.
    """
    train_limpio = df_train.copy()
    test_limpio = df_test.copy()
    
    for col in columnas:
        mediana_val = train_limpio[col].median()
        train_limpio[col] = train_limpio[col].fillna(mediana_val)
        test_limpio[col] = test_limpio[col].fillna(mediana_val)
        
    return train_limpio, test_limpio

def preprocesar_constante(df_train, df_test, columnas, valor):
    """
    Rellena los nulos con un valor constante numérico.
    """
    train_limpio = df_train.copy()
    test_limpio = df_test.copy()
    
    for col in columnas:
        train_limpio[col] = train_limpio[col].fillna(valor)
        test_limpio[col] = test_limpio[col].fillna(valor)
        
    return train_limpio, test_limpio