"""Pruebas unitarias para validar la descripción y persistencia del modelo."""

import tempfile
from pathlib import Path
import joblib
import pandas as pd
import pytest

from winamax.modelo_logica import ModeloInfo, entrenar_modelo_lineal


@pytest.fixture
def datos_ejemplo():
    """Genera datos sencillos para probar el entrenamiento."""
    df_train = pd.DataFrame({"x1": [1.0, 2.0, 3.0, 4.0], "y": [2.0, 4.0, 6.0, 8.0]})
    df_test = pd.DataFrame({"x1": [5.0, 6.0], "y": [10.0, 12.0]})
    return df_train, df_test


def test_modelo_nuevo_crea_descripcion_vacia(datos_ejemplo):
    """Comprueba que un modelo recién creado cuenta por defecto con una descripción vacía."""
    train_df, test_df = datos_ejemplo
    modelo_info, _ = entrenar_modelo_lineal(
        train_df, test_df, features=["x1"], target="y"
    )

    assert isinstance(modelo_info, ModeloInfo)
    assert modelo_info.descripcion == ""


def test_modelo_almacena_y_actualiza_descripcion(datos_ejemplo):
    """Comprueba que la descripción forma parte de la estructura de datos y refleja los cambios."""
    train_df, test_df = datos_ejemplo
    descripcion_inicial = "Modelo inicial de prueba"
    modelo_info, _ = entrenar_modelo_lineal(
        train_df, test_df, features=["x1"], target="y", descripcion=descripcion_inicial
    )

    assert modelo_info.descripcion == descripcion_inicial

    # Actualizar descripción directamente en la estructura
    nueva_descripcion = "Modelo actualizado con nuevos parámetros de negocio"
    modelo_info.descripcion = nueva_descripcion
    assert modelo_info.descripcion == nueva_descripcion

    # Comprobar la representación en diccionario
    diccionario = modelo_info.to_dict()
    assert diccionario["descripcion"] == nueva_descripcion


def test_persistencia_descripcion_con_joblib(datos_ejemplo):
    """Comprueba que la descripción y el modelo se persisten y recuperan correctamente usando joblib."""
    train_df, test_df = datos_ejemplo
    descripcion_test = "Modelo listo para producción serializado con joblib"
    modelo_info, _ = entrenar_modelo_lineal(
        train_df, test_df, features=["x1"], target="y", descripcion=descripcion_test
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        ruta_archivo = Path(tmpdir) / "modelo_entrenado.joblib"
        
        # Guardar con joblib
        joblib.dump(modelo_info, ruta_archivo)

        # Cargar con joblib
        modelo_cargado: ModeloInfo = joblib.load(ruta_archivo)

        assert modelo_cargado.descripcion == descripcion_test
        assert modelo_cargado.features == ["x1"]
        assert modelo_cargado.target == "y"
        assert modelo_cargado.formula is not None