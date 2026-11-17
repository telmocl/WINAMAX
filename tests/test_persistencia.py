import os
import stat

import joblib
import pandas as pd
import pytest

from winamax import persistencia
from winamax.modelo_logica import entrenar_modelo_lineal
from winamax.persistencia import EXTENSION, asegurar_extension, guardar_modelo

CLAVES_ESPERADAS = {
    "version_formato", "modelo", "columnas_entrada", "columna_salida",
    "formula", "metricas", "descripcion",
}


@pytest.fixture
def modelo_info():
    train = pd.DataFrame({
        "superficie": [50, 60, 70, 80, 90, 100],
        "antigüedad": [30, 25, 20, 15, 10, 5],
        "precio": [100, 125, 148, 170, 195, 215],
    })
    test = pd.DataFrame({
        "superficie": [65, 85],
        "antigüedad": [22, 12],
        "precio": [135, 180],
    })
    info, _ = entrenar_modelo_lineal(
        train, test, ["superficie", "antigüedad"], "precio",
        descripcion="Modelo de pisos de A Coruña",
    )
    return info


def test_contiene_toda_la_informacion(tmp_path, modelo_info):
    ruta = guardar_modelo(modelo_info, tmp_path / "m")
    d = joblib.load(ruta)
    assert list(d["modelo"].coef_) == list(modelo_info.modelo.coef_)
    assert d["modelo"].intercept_ == modelo_info.modelo.intercept_
    assert d["formula"] == modelo_info.formula
    assert d["columnas_entrada"] == ["superficie", "antigüedad"]
    assert d["columna_salida"] == "precio"
    assert set(d["metricas"]) == {"r2_train", "mse_train", "r2_test", "mse_test"}
    assert d["metricas"] == modelo_info.metricas
    assert d["descripcion"] == "Modelo de pisos de A Coruña"


def test_modelo_guardado_sirve_para_predecir(tmp_path, modelo_info):
    d = joblib.load(guardar_modelo(modelo_info, tmp_path / "m"))
    X = pd.DataFrame({"superficie": [75], "antigüedad": [18]})
    assert d["modelo"].predict(X)[0] == pytest.approx(
        modelo_info.modelo.predict(X)[0])


@pytest.mark.parametrize("valor", ["", None])
def test_descripcion_vacia(tmp_path, modelo_info, valor):
    modelo_info.descripcion = valor
    d = joblib.load(guardar_modelo(modelo_info, tmp_path / "m"))
    assert d["descripcion"] == ""


def test_no_guarda_datos_ni_graficos(tmp_path, modelo_info):
    # Aunque el objeto lleve datos pegados, no deben acabar en el archivo
    modelo_info.train_df = pd.DataFrame({"a": [1]})
    modelo_info.figura = object()
    d = joblib.load(guardar_modelo(modelo_info, tmp_path / "m"))
    assert set(d) == CLAVES_ESPERADAS
    assert not any(isinstance(v, pd.DataFrame) for v in d.values())


def test_anade_extension(tmp_path, modelo_info):
    assert guardar_modelo(modelo_info, tmp_path / "m").suffix == EXTENSION


def test_no_duplica_extension(tmp_path):
    assert asegurar_extension(tmp_path / f"m{EXTENSION}").name == f"m{EXTENSION}"


def test_ruta_con_espacios_tildes_y_enie(tmp_path, modelo_info):
    carpeta = tmp_path / "mi carpeta ñandú áé"
    carpeta.mkdir()
    ruta = guardar_modelo(modelo_info, carpeta / "modelo núm 1")
    assert ruta.exists()
    assert joblib.load(ruta)["formula"] == modelo_info.formula


def test_sobrescribe_archivo_existente(tmp_path, modelo_info):
    guardar_modelo(modelo_info, tmp_path / "m")
    modelo_info.descripcion = "nueva"
    d = joblib.load(guardar_modelo(modelo_info, tmp_path / "m"))
    assert d["descripcion"] == "nueva"


def test_carpeta_inexistente(tmp_path, modelo_info):
    with pytest.raises(OSError):
        guardar_modelo(modelo_info, tmp_path / "no_existe" / "m")


@pytest.mark.skipif(os.name == "nt" or os.geteuid() == 0,
                    reason="permisos POSIX no aplicables")
def test_carpeta_sin_permisos(tmp_path, modelo_info):
    carpeta = tmp_path / "solo_lectura"
    carpeta.mkdir()
    carpeta.chmod(stat.S_IREAD | stat.S_IEXEC)
    try:
        with pytest.raises(PermissionError):
            guardar_modelo(modelo_info, carpeta / "m")
    finally:
        carpeta.chmod(stat.S_IRWXU)


def test_fallo_al_escribir_no_deja_temporales(tmp_path, modelo_info, monkeypatch):
    def falla(*args, **kwargs):
        raise OSError("disco lleno")

    monkeypatch.setattr(persistencia.joblib, "dump", falla)
    with pytest.raises(OSError):
        guardar_modelo(modelo_info, tmp_path / "m")
    assert list(tmp_path.iterdir()) == []