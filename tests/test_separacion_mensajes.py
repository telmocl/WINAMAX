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
