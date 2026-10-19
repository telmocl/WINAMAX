from pathlib import Path
import sqlite3
import pandas as pd

class DataLoaderError(Exception):
    """Excepción base para los errores del módulo
    de importación."""
    pass
def _load_sqlite_single_table(path: Path) -> pd.DataFrame:
        """Lee una base de datos SQLite asumiendo
        que contiene exactamente una tabla."""
        try:
            conn = sqlite3.connect(path)
            query = """SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%';"""
            tables = pd.read_sql(query, conn)

            if tables.empty:
                raise DataLoaderError("no contiene ninguna tabla")
            if len(tables) > 1:
                raise DataLoaderError("más de una tabla" )

            table_name = tables.iloc[0, 0]
            df = pd.read_sql(f'SELECT * FROM "{table_name}"', conn)
            return df
        except sqlite3.Error as e:
            raise DataLoaderError(f"Error al leer la base de datos SQLite:{e}") from e
        finally:
            if "conn" in locals() and conn:
                conn.close()

def load_data(file_path: str | Path) -> pd.DataFrame:
    """Importa datos desde un archivo CSV, Excel o
      base de datos SQLite.

    Determina el formato según la extensión del
    archivo y devuelve los datos
    como un DataFrame de pandas con las
    columnas numéricas tipadas correctamente. """
    
    path = Path(file_path)

    if not path.exists() or not path.is_file():
        raise DataLoaderError(f"El archivo no existe o no es válido: '{path}'")

    ext = path.suffix.lower()
    supported_extensions = {".csv", ".xlsx", ".xls",
    ".sqlite", ".db"}
    if ext not in supported_extensions:
        raise DataLoaderError(
            f"La extensión '{ext}' no está soportada. "
            f"Extensiones permitidas:{sorted(supported_extensions)}")

    try:
        if ext == ".csv":
            df = pd.read_csv(path)
        elif ext in {".xlsx", ".xls"}:
            df = pd.read_excel(path)
        elif ext in {".sqlite", ".db"}:
            df = _load_sqlite_single_table(path)
    except DataLoaderError:
        raise
    except Exception as e:
        raise DataLoaderError( f"El archivo está dañado, vacío o su contenido no corresponde a su extensión:{e}" ) from e

    if df is None or df.empty:
        raise DataLoaderError("El archivo no contiene datos.")
    return df