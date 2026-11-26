import pandas as pd
import pytest

from winamax.separacion_logica import realizar_separacion_datos


@pytest.fixture
def df():
    return pd.DataFrame({"a": range(20), "y": range(20)})


def test_mensaje_de_porcentaje_con_tilde(df):
    _, _, msg = realizar_separacion_datos(df, test_size_pct=0, random_state=0)
    assert msg == "El porcentaje de test debe ser un número entre 1 y 99."


def test_mensaje_de_exito_con_tilde(df):
    _, _, msg = realizar_separacion_datos(df, test_size_pct=20, random_state=0)
    assert msg == "Separación realizada con éxito."


@pytest.mark.parametrize("semilla", [-1, 2**32])
def test_semilla_fuera_de_rango_mensaje_en_espanol(df, semilla):
    tr, te, msg = realizar_separacion_datos(df, test_size_pct=20, random_state=semilla)
    assert tr is None and te is None
    assert msg.startswith("La semilla (seed) debe ser un número entero entre 0 y")
    assert "random_state" not in msg


@pytest.mark.parametrize("semilla", [0, 2**32 - 1])
def test_semillas_limite_validas(df, semilla):
    tr, te, _ = realizar_separacion_datos(df, test_size_pct=20, random_state=semilla)
    assert tr is not None and te is not None


def test_porcentaje_que_vacia_el_entrenamiento():
    cinco = pd.DataFrame({"a": range(5), "b": range(5)})
    tr, te, msg = realizar_separacion_datos(cinco, test_size_pct=99, random_state=42)
    assert tr is None and te is None
    assert msg == "El porcentaje elegido deja alguno de los conjuntos vacío. Ajusta el porcentaje"
