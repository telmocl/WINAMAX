import numpy as np
import pandas as pd
import pytest

from winamax.utilidades import (
    detectar_nulos, preprocesar_constante, preprocesar_eliminar_filas,
    preprocesar_media, preprocesar_mediana,
)

COLS = ["a", "y"]


@pytest.fixture
def datos():
    train = pd.DataFrame({"a": [1.0, 3.0, np.nan, 5.0],
                          "y": [10.0, 20.0, 30.0, np.nan]})
    test = pd.DataFrame({"a": [np.nan, 2.0], "y": [5.0, np.nan]})
    return train, test


def test_detectar_nulos_cuenta_por_columna(datos):
    r = detectar_nulos(*datos, COLS)
    assert r["train"] == {"a": 1, "y": 1}
    assert r["test"] == {"a": 1, "y": 1}


def test_detectar_nulos_sin_nulos():
    df = pd.DataFrame({"a": [1, 2], "y": [3, 4]})
    r = detectar_nulos(df, df, COLS)
    assert sum(r["train"].values()) == 0 and sum(r["test"].values()) == 0


def test_detectar_nulos_ignora_columnas_no_pedidas(datos):
    train, test = datos
    train["otra"] = np.nan
    assert "otra" not in detectar_nulos(train, test, COLS)["train"]


def test_media_usa_la_media_de_train(datos):
    tr, te = preprocesar_media(*datos, COLS)
    assert tr.loc[2, "a"] == pytest.approx(3.0)   # media de 1, 3, 5
    assert te.loc[0, "a"] == pytest.approx(3.0)   # misma media en test


def test_media_no_deja_nulos(datos):
    tr, te = preprocesar_media(*datos, COLS)
    assert tr[COLS].isna().sum().sum() == 0
    assert te[COLS].isna().sum().sum() == 0


def test_mediana_usa_la_mediana_de_train():
    train = pd.DataFrame({"a": [1.0, 2.0, 100.0, np.nan], "y": [1.0, 2, 3, 4]})
    test = pd.DataFrame({"a": [np.nan], "y": [1.0]})
    tr, te = preprocesar_mediana(train, test, COLS)
    assert tr.loc[3, "a"] == pytest.approx(2.0)
    assert te.loc[0, "a"] == pytest.approx(2.0)


def test_constante_rellena_con_el_valor(datos):
    tr, te = preprocesar_constante(*datos, COLS, -1.0)
    assert tr.loc[2, "a"] == -1.0 and te.loc[1, "y"] == -1.0
    assert tr[COLS].isna().sum().sum() == 0


def test_eliminar_filas_quita_las_que_tienen_nulos(datos):
    tr, te = preprocesar_eliminar_filas(*datos, COLS)
    assert len(tr) == 2 and len(te) == 0
    assert tr[COLS].isna().sum().sum() == 0


def test_eliminar_filas_no_toca_nulos_de_otras_columnas():
    train = pd.DataFrame({"a": [1.0, 2.0], "y": [1.0, 2.0],
                          "otra": [np.nan, np.nan]})
    tr, _ = preprocesar_eliminar_filas(train, train.copy(), COLS)
    assert len(tr) == 2


@pytest.mark.parametrize("fn", [preprocesar_media, preprocesar_mediana])
def test_no_modifica_los_originales(fn, datos):
    train, test = datos
    t0, s0 = train.copy(), test.copy()
    fn(train, test, COLS)
    pd.testing.assert_frame_equal(train, t0)
    pd.testing.assert_frame_equal(test, s0)


def test_sin_nulos_los_datos_quedan_iguales():
    df = pd.DataFrame({"a": [1.0, 2.0], "y": [3.0, 4.0]})
    tr, te = preprocesar_media(df, df.copy(), COLS)
    pd.testing.assert_frame_equal(tr, df)