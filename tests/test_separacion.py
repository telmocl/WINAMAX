import pandas as pd 
import pytest 
from winamax.separacion_logica import realizar_separacion_datos

@pytest.fixture

def dataset_prueba():
    #Dataset de 10 filas para probar
    return pd.DataFrame({"x": range(10), "y": range(10,20)})

def test_tamanos_porcentaje(dataset_prueba):
    #20% de test en 10 filas = 2 filas de test, 8 de train
    train, test, msg = realizar_separacion_datos(
        dataset_prueba,test_size_pct=20.0, random_state=42
    )
    assert train is not None
    assert test is not None
    assert len(test) == 2
    assert len(train) == 8

def test_filas_exclusivas(dataset_prueba):
    #Ninguna fila debe aparecer en ambos conjuntos
    train, test, _ = realizar_separacion_datos(
        dataset_prueba, test_size_pct=30.0, random_state=123
    )
    comunes = set(train.index).intersection(set(test.index))
    assert len(comunes) == 0

def test_reproducible_semilla(dataset_prueba):
    #La misma semilla debe producir exactamente la misma particion 
    train_1, test_1, _ = realizar_separacion_datos(
        dataset_prueba, test_size_pct= 20.0, random_state=42
    )
    train_2, test_2, _ = realizar_separacion_datos(
        dataset_prueba, test_size_pct= 20.0, random_state= 42
    )
    pd.testing.assert_frame_equal(train_1,train_2)
    pd.testing.assert_frame_equal(test_1, test_2)

def test_errores_validacion():
    #Dataset muy pequeño (<5 filas)
    df_pequeño = pd.DataFrame({"x": [1,2]})
    train, test, msg = realizar_separacion_datos(df_pequeño)
    assert train is None 
    assert "al menos 5 filas" in msg 

    #Porcentaje fuera de rango
    df_valido = pd.DataFrame({"x": range(10)})
    train, test, msg = realizar_separacion_datos(df_valido, test_size_pct=105)
    assert train is None 
    assert "entre 1 y 99" in msg 
    