import pandas as pd
import pytest

from winamax.separacion_logica import realizar_separacion_datos


@pytest.fixture
def df():
    return pd.DataFrame({"a": range(100), "y": range(100)})


def test_20_por_ciento(df):
    tr, te, _ = realizar_separacion_datos(df, test_size_pct=20, random_state=42)
    assert len(te) == 20 and len(tr) == 80


def test_tamanos_suman_el_total(df):
    tr, te, _ = realizar_separacion_datos(df, test_size_pct=33, random_state=1)
    assert len(tr) + len(te) == len(df)


def test_no_hay_filas_repetidas_entre_train_y_test(df):
    tr, te, _ = realizar_separacion_datos(df, test_size_pct=30, random_state=3)
    assert set(tr["a"]).isdisjoint(set(te["a"]))


def test_no_se_pierde_ninguna_fila(df):
    tr, te, _ = realizar_separacion_datos(df, test_size_pct=30, random_state=3)
    assert set(tr["a"]) | set(te["a"]) == set(df["a"])


def test_misma_semilla_mismo_resultado(df):
    a = realizar_separacion_datos(df, test_size_pct=20, random_state=7)
    b = realizar_separacion_datos(df, test_size_pct=20, random_state=7)
    pd.testing.assert_frame_equal(a[0], b[0])
    pd.testing.assert_frame_equal(a[1], b[1])


def test_distinta_semilla_distinto_resultado(df):
    a = realizar_separacion_datos(df, test_size_pct=20, random_state=1)
    b = realizar_separacion_datos(df, test_size_pct=20, random_state=2)
    assert list(a[1]["a"]) != list(b[1]["a"])


def test_conserva_las_columnas(df):
    tr, te, _ = realizar_separacion_datos(df, test_size_pct=20, random_state=0)
    assert list(tr.columns) == list(df.columns) == list(te.columns)


def test_devuelve_mensaje_de_texto(df):
    assert isinstance(realizar_separacion_datos(df, 20, 0)[2], str)


@pytest.mark.parametrize("pct", [0, -5, 100, 150])
def test_porcentaje_invalido(df, pct):
    tr, te, msg = realizar_separacion_datos(df, test_size_pct=pct, random_state=0)
    assert tr is None and te is None and msg


@pytest.mark.parametrize("pct", [1, 99])
def test_porcentajes_limite_validos(df, pct):
    tr, te, _ = realizar_separacion_datos(df, test_size_pct=pct, random_state=0)
    assert tr is not None and len(tr) > 0 and len(te) > 0


def test_no_modifica_el_dataframe_original(df):
    copia = df.copy()
    realizar_separacion_datos(df, test_size_pct=20, random_state=0)
    pd.testing.assert_frame_equal(df, copia)