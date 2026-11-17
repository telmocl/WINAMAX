import joblib
import numpy as np
import pandas as pd
import pytest

from winamax import persistencia
from winamax.modelo_logica import entrenar_modelo_lineal
from winamax.persistencia import (
    EXTENSION, VERSION_FORMATO, asegurar_extension,
    guardar_modelo, modelo_a_diccionario,
)


@pytest.fixture
def info():
    df = pd.DataFrame({"x": [1, 2, 3, 4, 5, 6], "y": [3, 5, 7, 9, 11, 13]})
    i, _ = entrenar_modelo_lineal(df.iloc[:4], df.iloc[4:], ["x"], "y",
                                  descripcion="d")
    return i


def test_extension_es_joblib():
    assert EXTENSION == ".joblib"


def test_extension_en_mayusculas_no_se_duplica(tmp_path):
    assert asegurar_extension(tmp_path / "m.JOBLIB").name == "m.JOBLIB"


def test_otra_extension_se_conserva_y_se_anade_la_correcta(tmp_path):
    assert asegurar_extension(tmp_path / "m.json").name == "m.json.joblib"


def test_nombre_con_puntos(tmp_path):
    assert asegurar_extension(tmp_path / "modelo.v2").name == "modelo.v2.joblib"


def test_acepta_ruta_como_cadena(tmp_path, info):
    ruta = guardar_modelo(info, str(tmp_path / "m"))
    assert ruta.exists()


def test_devuelve_la_ruta_final(tmp_path, info):
    assert guardar_modelo(info, tmp_path / "m") == tmp_path / ("m" + EXTENSION)


def test_incluye_version_de_formato(tmp_path, info):
    d = joblib.load(guardar_modelo(info, tmp_path / "m"))
    assert d["version_formato"] == VERSION_FORMATO


def test_metricas_guardadas_son_float_nativos(info):
    info.metricas = {k: np.float64(v) for k, v in info.metricas.items()}
    d = modelo_a_diccionario(info)
    assert all(type(v) is float for v in d["metricas"].values())


def test_ida_y_vuelta_predice_igual(tmp_path, info):
    d = joblib.load(guardar_modelo(info, tmp_path / "m"))
    X = pd.DataFrame({"x": [10, 20, 30]})
    assert list(d["modelo"].predict(X)) == pytest.approx(
        list(info.modelo.predict(X)))


def test_ida_y_vuelta_conserva_tildes_y_enie(tmp_path, info):
    info.descripcion = "Año 2026: niño, pingüino, camión"
    d = joblib.load(guardar_modelo(info, tmp_path / "m"))
    assert d["descripcion"] == "Año 2026: niño, pingüino, camión"


def test_descripcion_multilinea(tmp_path, info):
    info.descripcion = "línea 1\nlínea 2\n\nlínea 4"
    d = joblib.load(guardar_modelo(info, tmp_path / "m"))
    assert d["descripcion"] == "línea 1\nlínea 2\n\nlínea 4"


def test_columnas_se_guardan_como_lista(tmp_path, info):
    d = joblib.load(guardar_modelo(info, tmp_path / "m"))
    assert isinstance(d["columnas_entrada"], list)


def test_no_deja_temporales_tras_guardar_bien(tmp_path, info):
    guardar_modelo(info, tmp_path / "m")
    assert [p.name for p in tmp_path.iterdir()] == ["m" + EXTENSION]


def test_fallo_al_sobrescribir_conserva_el_original(tmp_path, info, monkeypatch):
    ruta = guardar_modelo(info, tmp_path / "m")
    original = ruta.read_bytes()

    def falla(*a, **k):
        raise OSError("disco lleno")

    monkeypatch.setattr(persistencia.joblib, "dump", falla)
    with pytest.raises(OSError):
        guardar_modelo(info, tmp_path / "m")
    assert ruta.read_bytes() == original
    assert [p.name for p in tmp_path.iterdir()] == ["m" + EXTENSION]


def test_guardar_dos_modelos_distintos(tmp_path, info):
    guardar_modelo(info, tmp_path / "a")
    guardar_modelo(info, tmp_path / "b")
    assert {p.name for p in tmp_path.iterdir()} == {"a.joblib", "b.joblib"}


def test_no_guarda_el_dataset_original(tmp_path, info):
    d = joblib.load(guardar_modelo(info, tmp_path / "m"))
    assert not any(isinstance(v, (pd.DataFrame, pd.Series)) for v in d.values())