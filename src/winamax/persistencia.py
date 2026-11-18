"""Guardado del modelo en disco (formato definido en #20), independiente de la GUI."""

import os
import tempfile
from pathlib import Path

import joblib

EXTENSION = ".joblib"
VERSION_FORMATO = 1


def asegurar_extension(ruta) -> Path:
    """Devuelve la ruta con la extensión del formato, añadiéndola si falta."""
    ruta = Path(ruta)
    if ruta.suffix.lower() == EXTENSION:
        return ruta
    return ruta.with_name(ruta.name + EXTENSION)


def modelo_a_diccionario(modelo_info) -> dict:
    """Solo el modelo y sus metadatos: nunca datos ni gráficos."""
    return {
        "version_formato": VERSION_FORMATO,
        "modelo": modelo_info.modelo,
        "columnas_entrada": list(modelo_info.features),
        "columna_salida": modelo_info.target,
        "formula": modelo_info.formula,
        "metricas": {k: float(v) for k, v in modelo_info.metricas.items()},
        "descripcion": modelo_info.descripcion or "",
    }


def guardar_modelo(modelo_info, ruta) -> Path:
    """Guarda el modelo en `ruta` (añade la extensión si falta).

    Devuelve la ruta final. Propaga OSError/PermissionError si falla.
    """
    ruta = asegurar_extension(ruta)
    contenido = modelo_a_diccionario(modelo_info)

    fd, tmp = tempfile.mkstemp(dir=ruta.parent, suffix=".tmp")
    os.close(fd)
    try:
        joblib.dump(contenido, tmp)
        os.chmod(tmp, 0o644)
        os.replace(tmp, ruta)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise
    return ruta

def cargar_modelo(ruta: Path):
    """Carga un modelo guardado desde 'ruta' y devuelve una instancia de ModeloInfo"""
    import joblib
    from winamax.modelo_logica import ModeloInfo

    datos=joblib.load(ruta)

    if not isinstance(datos, dict) or "modelo" not in datos:
        raise ValueError("El archivo no tiene el formato de modelo esperado.")

    # Reconstruir el objeto ModeloInfo o estructura equivalente
    modelo_info = ModeloInfo(modelo=datos["modelo"],
            features=datos["columnas_entrada"],
            target=datos["columna_salida"],
            formula=datos["formula"],
            metricas=datos["metricas"],
            descripcion=datos.get("descripcion",""))
    
    if "descripcion" in datos:
        modelo_info.descripcion = datos["descripcion"]
    return modelo_info
