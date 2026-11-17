import numpy as np
import pandas as pd
import pytest

from winamax.modelo_logica import (
    ModeloInfo, entrenar_modelo_lineal, generar_formula_texto,
)


@pytest.fixture
def lineal():
    """y = 2x + 1 exacta."""
    train = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [3, 5, 7, 9, 11]})
    test = pd.DataFrame({"x": [6, 7, 8], "y": [13, 15, 17]})
    return train, test


# ---------- generar_formula_texto ----------

def test_formula_coeficientes_positivos():
    f = generar_formula_texto("y", ["a", "b"], [2.0, 3.0], 1.0)
    assert f == "y = 2.0000 * a + 3.0000 * b + 1.0000"


def test_formula_coeficiente_negativo_intermedio():
    f = generar_formula_texto("y", ["a", "b"], [2.0, -3.0], 1.0)
    assert f == "y = 2.0000 * a - 3.0000 * b + 1.0000"


def test_formula_primer_coeficiente_negativo():
    f = generar_formula_texto("y", ["a"], [-2.0], 1.0)
    assert f == "y = - 2.0000 * a + 1.0000"


def test_formula_intercepto_negativo():
    f = generar_formula_texto("y", ["a"], [2.0], -1.5)
    assert f == "y = 2.0000 * a - 1.5000"


def test_formula_intercepto_cero_se_muestra_como_suma():
    assert generar_formula_texto("y", ["a"], [2.0], 0.0).endswith("+ 0.0000")


def test_formula_usa_nombres_con_tildes_y_espacios():
    f = generar_formula_texto("precio total", ["antigüedad"], [1.0], 0.0)
    assert f.startswith("precio total =") and "antigüedad" in f


def test_formula_redondea_a_cuatro_decimales():
    assert "0.3333" in generar_formula_texto("y", ["a"], [1 / 3], 0.0)


# ---------- entrenar_modelo_lineal ----------

def test_ajuste_exacto(lineal):
    info, _ = entrenar_modelo_lineal(*lineal, ["x"], "y")
    assert info.modelo.coef_[0] == pytest.approx(2.0)
    assert info.modelo.intercept_ == pytest.approx(1.0)


def test_metricas_perfectas_en_datos_lineales(lineal):
    info, _ = entrenar_modelo_lineal(*lineal, ["x"], "y")
    m = info.metricas
    assert m["r2_train"] == pytest.approx(1.0)
    assert m["r2_test"] == pytest.approx(1.0)
    assert m["mse_train"] == pytest.approx(0.0, abs=1e-9)
    assert m["mse_test"] == pytest.approx(0.0, abs=1e-9)


def test_metricas_tienen_las_cuatro_claves_y_son_float(lineal):
    info, _ = entrenar_modelo_lineal(*lineal, ["x"], "y")
    assert set(info.metricas) == {"r2_train", "mse_train", "r2_test", "mse_test"}
    assert all(isinstance(v, float) for v in info.metricas.values())


def test_devuelve_y_y_predicciones_con_longitud_correcta(lineal):
    train, test = lineal
    _, (y_tr, p_tr, y_te, p_te) = entrenar_modelo_lineal(train, test, ["x"], "y")
    assert len(y_tr) == len(p_tr) == len(train)
    assert len(y_te) == len(p_te) == len(test)


def test_descripcion_por_defecto_vacia(lineal):
    info, _ = entrenar_modelo_lineal(*lineal, ["x"], "y")
    assert info.descripcion == ""


def test_descripcion_se_conserva(lineal):
    info, _ = entrenar_modelo_lineal(*lineal, ["x"], "y", descripcion="hola")
    assert info.descripcion == "hola"


def test_guarda_features_target_y_formula(lineal):
    info, _ = entrenar_modelo_lineal(*lineal, ["x"], "y")
    assert info.features == ["x"]
    assert info.target == "y"
    assert info.formula.startswith("y =")


def test_modelo_multiple():
    rng = np.random.default_rng(0)
    a, b = rng.normal(size=50), rng.normal(size=50)
    df = pd.DataFrame({"a": a, "b": b, "y": 3 * a - 2 * b + 5})
    info, _ = entrenar_modelo_lineal(df.iloc[:40], df.iloc[40:], ["a", "b"], "y")
    assert list(info.modelo.coef_) == pytest.approx([3.0, -2.0])
    assert info.modelo.intercept_ == pytest.approx(5.0)


def test_el_orden_de_features_se_respeta_en_la_formula():
    df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [4, 1, 3, 2],
                       "y": [5, 4, 9, 8]})
    info, _ = entrenar_modelo_lineal(df, df, ["b", "a"], "y")
    assert info.formula.index("b") < info.formula.index("a")


def test_nulos_en_train_lanzan_error(lineal):
    train, test = lineal
    train = train.astype(float)
    train.loc[0, "x"] = np.nan
    with pytest.raises(ValueError):
        entrenar_modelo_lineal(train, test, ["x"], "y")


def test_nulos_en_test_lanzan_error(lineal):
    train, test = lineal
    test = test.astype(float)
    test.loc[test.index[0], "y"] = np.nan
    with pytest.raises(ValueError):
        entrenar_modelo_lineal(train, test, ["x"], "y")


def test_columna_inexistente_lanza_error(lineal):
    with pytest.raises(KeyError):
        entrenar_modelo_lineal(*lineal, ["no_existe"], "y")


def test_no_modifica_los_dataframes_de_entrada(lineal):
    train, test = lineal
    t0, s0 = train.copy(), test.copy()
    entrenar_modelo_lineal(train, test, ["x"], "y")
    pd.testing.assert_frame_equal(train, t0)
    pd.testing.assert_frame_equal(test, s0)


def test_el_ajuste_solo_usa_entrenamiento(lineal):
    train, _ = lineal
    test_raro = pd.DataFrame({"x": [10, 20], "y": [-500, 900]})
    info, _ = entrenar_modelo_lineal(train, test_raro, ["x"], "y")
    assert info.modelo.coef_[0] == pytest.approx(2.0)


def test_columnas_extra_se_ignoran(lineal):
    train, test = lineal
    train = train.assign(ruido=["a", "b", "c", "d", "e"])
    test = test.assign(ruido=["a", "b", "c"])
    info, _ = entrenar_modelo_lineal(train, test, ["x"], "y")
    assert info.features == ["x"]


# ---------- ModeloInfo ----------

def test_to_dict_contiene_las_claves(lineal):
    info, _ = entrenar_modelo_lineal(*lineal, ["x"], "y", descripcion="d")
    d = info.to_dict()
    assert set(d) == {"modelo", "features", "target", "formula",
                      "metricas", "descripcion"}
    assert d["descripcion"] == "d"


def test_descripcion_modificable_despues():
    info = ModeloInfo(None, ["x"], "y", "f", {})
    info.descripcion = "nueva"
    assert info.to_dict()["descripcion"] == "nueva"