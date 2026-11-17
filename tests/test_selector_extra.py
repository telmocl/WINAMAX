import pandas as pd
import pytest

from winamax.selector_logic import validar_seleccion_columnas


@pytest.fixture
def df():
    return pd.DataFrame({"a": [1, 2], "b": [3.0, 4.0],
                         "texto": ["x", "y"], "y": [5, 6]})


def test_seleccion_valida(df):
    ok, _ = validar_seleccion_columnas(df, ["a", "b"], "y")
    assert ok is True


def test_sin_entradas(df):
    ok, msg = validar_seleccion_columnas(df, [], "y")
    assert ok is False and msg


def test_sin_salida(df):
    ok, msg = validar_seleccion_columnas(df, ["a"], None)
    assert ok is False and msg


def test_salida_dentro_de_las_entradas(df):
    ok, _ = validar_seleccion_columnas(df, ["a", "y"], "y")
    assert ok is False


def test_entrada_inexistente(df):
    ok, _ = validar_seleccion_columnas(df, ["zzz"], "y")
    assert ok is False


def test_salida_inexistente(df):
    ok, _ = validar_seleccion_columnas(df, ["a"], "zzz")
    assert ok is False


def test_entrada_no_numerica(df):
    ok, _ = validar_seleccion_columnas(df, ["texto"], "y")

def test_entrada_no_numerica(df):
    ok, _ = validar_seleccion_columnas(df, ["texto"], "y")
    assert ok is False


def test_salida_no_numerica(df):
    ok, _ = validar_seleccion_columnas(df, ["a"], "texto")
    assert ok is False


def test_el_mensaje_es_texto(df):
    assert isinstance(validar_seleccion_columnas(df, ["a"], "y")[1], str)