import sqlite3
import pandas as pd
import pytest

from winamax.importacion import DataLoaderError, load_data


# --- Pruebas de casos de éxito (ficheros válidos) ---

def test_load_data_csv_exito(tmp_path):
    """Verifica que se importan correctamente los datos desde un archivo CSV."""
    fichero_csv = tmp_path / "datos.csv"
    fichero_csv.write_text("nombre,edad,puntuacion\nAna,25,9.5\nCarlos,30,8.0\n")

    df = load_data(fichero_csv)

    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["nombre", "edad", "puntuacion"]
    assert len(df) == 2
    assert df.loc[0, "nombre"] == "Ana"
    assert df["edad"].dtype in ["int64", "int32"]
    assert df["puntuacion"].dtype in ["float64", "float32"]


def test_load_data_excel_exito(tmp_path):
    """Verifica que se importan correctamente los datos desde un archivo Excel."""
    fichero_excel = tmp_path / "datos.xlsx"
    df_original = pd.DataFrame({
        "producto": ["Manzana", "Pera"],
        "precio": [1.5, 2.0]
    })
    df_original.to_excel(fichero_excel, index=False)

    df = load_data(fichero_excel)

    assert len(df) == 2
    assert list(df.columns) == ["producto", "precio"]
    assert df.loc[1, "producto"] == "Pera"


def test_load_data_sqlite_exito(tmp_path):
    """Verifica que se importa correctamente una BD SQLite con exactamente una tabla."""
    fichero_db = tmp_path / "datos.db"
    conn = sqlite3.connect(fichero_db)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE usuarios (id INTEGER, nombre TEXT);")
    cursor.execute("INSERT INTO usuarios VALUES (1, 'Laura'), (2, 'Pedro');")
    conn.commit()
    conn.close()

    df = load_data(fichero_db)

    assert len(df) == 2
    assert list(df.columns) == ["id", "nombre"]
    assert df.loc[0, "nombre"] == "Laura"


# --- Pruebas de manejo de errores ---

def test_load_data_archivo_no_existe(tmp_path):
    """Lanza DataLoaderError si el archivo especificado no existe."""
    fichero_inexistente = tmp_path / "no_existo.csv"

    with pytest.raises(DataLoaderError, match="El archivo no existe"):
        load_data(fichero_inexistente)


def test_load_data_extension_no_soportada(tmp_path):
    """Lanza DataLoaderError si la extensión del archivo no está entre las permitidas."""
    fichero_txt = tmp_path / "datos.txt"
    fichero_txt.write_text("contenido no valido")

    with pytest.raises(DataLoaderError, match="no está soportada"):
        load_data(fichero_txt)


def test_load_data_csv_vacio(tmp_path):
    """Lanza DataLoaderError cuando el archivo CSV no contiene datos."""
    fichero_vacio = tmp_path / "vacio.csv"
    fichero_vacio.write_text("")

    with pytest.raises(DataLoaderError):
        load_data(fichero_vacio)


def test_load_data_sqlite_sin_tablas(tmp_path):
    """Lanza DataLoaderError si la base de datos SQLite no contiene ninguna tabla."""
    fichero_db = tmp_path / "sin_tablas.sqlite"
    conn = sqlite3.connect(fichero_db)
    conn.close()

    with pytest.raises(DataLoaderError, match="no contiene ninguna tabla"):
        load_data(fichero_db)


def test_load_data_sqlite_multiples_tablas(tmp_path):
    """Lanza DataLoaderError si la base de datos SQLite contiene más de una tabla."""
    fichero_db = tmp_path / "varias_tablas.db"
    conn = sqlite3.connect(fichero_db)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE t1 (id INT);")
    cursor.execute("CREATE TABLE t2 (id INT);")
    conn.commit()
    conn.close()

    with pytest.raises(DataLoaderError, match="más de una tabla"):
        load_data(fichero_db)


def test_load_data_fichero_corrupto(tmp_path):
    """Lanza DataLoaderError cuando un archivo Excel tiene contenido corrupto/inválido."""
    fichero_corrupto = tmp_path / "corrupto.xlsx"
    fichero_corrupto.write_text("Este texto no es un archivo excel real")

    with pytest.raises(DataLoaderError, match="dañado"):
        load_data(fichero_corrupto)