import pandas as pd 
from winamax.selector_logic import validar_seleccion_columnas

def test_validacion_correcta():
    df = pd.DataFrame({"x1": [1,2,3], "x2": [4,5,6], "y": [10,20,30]})
    valido, msg = validar_seleccion_columnas(df, ["x1", "x2"], "y")
    assert valido is True

def test_error_falta_seleccion():
    df = pd.DataFrame({"x1": [1,2,3], "y": [10,20,30]})
    valido,msg = validar_seleccion_columnas(df,[], "y")
    assert valido is False
    assert "al menos una columna de entrada" in msg 

def test_error_target_en_features():
    df = pd.DataFrame({"x1": [1,2,3], "y":[10,20,30]})
    valido, msg = validar_seleccion_columnas(df, ["x1", "y"], "y")
    assert valido is False
    assert "no puede seleccionarse también como entrada" in msg

def test_error_columna_no_numerica():
    df = pd.DataFrame({"x1": [1,2,3], "texto": ["A", "B", "C"], "y":[10,20,30]})
    valido,msg = validar_seleccion_columnas(df, ["x1", "texto"], "y") 
    assert valido is False
    assert "no son numéricas" in msg 