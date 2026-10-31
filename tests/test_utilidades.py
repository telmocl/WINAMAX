import pytest
import pandas as pd
import numpy as np
from winamax.utilidades import (
    media,
    detectar_nulos,
    preprocesar_eliminar_filas,
    preprocesar_media,
    preprocesar_constante
)

def test_media_valores_conocidos():
    assert media([1, 2, 3]) == 2

def test_media_lista_vacia():
    with pytest.raises(ValueError):
        media([])

def test_detectar_nulos():
    df_train = pd.DataFrame({"A": [1, np.nan, 3], "B": [4, 5, 6]})
    df_test = pd.DataFrame({"A": [np.nan, 2, 3], "B": [7, 8, 9]})
    
    nulos = detectar_nulos(df_train, df_test, ["A", "B"])
    assert nulos["train"]["A"] == 1
    assert nulos["test"]["A"] == 1
    assert nulos["train"]["B"] == 0

def test_preprocesar_media():
    # La media de train en A es (2 + 4) / 2 = 3.0
    df_train = pd.DataFrame({"A": [2.0, np.nan, 4.0]})
    df_test = pd.DataFrame({"A": [np.nan, 5.0]})
    
    train_res, test_res = preprocesar_media(df_train, df_test, ["A"])
    
    assert train_res["A"].isna().sum() == 0
    assert test_res["A"].iloc[0] == 3.0  # Rellenado con la media de train

def test_preprocesar_constante():
    df_train = pd.DataFrame({"A": [1.0, np.nan]})
    df_test = pd.DataFrame({"A": [np.nan, 2.0]})
    
    train_res, test_res = preprocesar_constante(df_train, df_test, ["A"], valor=10.0)
    
    assert train_res["A"].iloc[1] == 10.0
    assert test_res["A"].iloc[0] == 10.0