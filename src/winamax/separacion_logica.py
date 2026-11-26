import logging
import math

import pandas as pd
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)

SEMILLA_MAXIMA = 2**32 - 1


def realizar_separacion_datos(
        df: pd.DataFrame, test_size_pct: float = 20.0,  random_state: int = 42
) -> tuple[pd.DataFrame | None, pd.DataFrame | None, str]:

    """Divide el DataFrame en conjuntos de entrenamiento y test de forma reproductible.

    Returns: (train_df, test_df, mensaje_error_o_exito)
    """

    #1. Validar tamaño minimo del dataset
    if df is None or len(df) < 5:
        return None, None, "El dataset debe tener al menos 5 filas para poder separarlo."

    #2. Validar porcentaje de test (1 a 99)
    if not isinstance(test_size_pct, (int,float)) or not (1 <= test_size_pct <= 99):
        return (
            None,
            None,
            "El porcentaje de test debe ser un número entre 1 y 99."
        )

    #3. Validar semilla (entero entre 0 y 2^32 - 1, el rango que admite scikit-learn)
    if not isinstance(random_state, int) or isinstance(random_state, bool):
        return None, None, "La semilla (seed) debe ser un número entero."
    if not (0 <= random_state <= SEMILLA_MAXIMA):
        return (
            None,
            None,
            f"La semilla (seed) debe ser un número entero entre 0 y {SEMILLA_MAXIMA}."
        )

    #Calcular fraccion de test.
    test_size = test_size_pct / 100.0

    #4. Verificar que ningún conjunto quede vacío (scikit-learn redondea el test hacia arriba).
    filas_test = math.ceil(len(df) * test_size)
    if filas_test == 0 or len(df) - filas_test == 0:
        return (
            None,
            None,
            "El porcentaje elegido deja alguno de los conjuntos vacío. Ajusta el porcentaje"
        )

    try:
        #Realizar separacion usando scikit-learn
        train_df, test_df = train_test_split(
            df, test_size = test_size, random_state=random_state
        )

    except Exception:
        logger.exception("Error al realizar la separación")
        return (
            None,
            None,
            "No se pudo realizar la separación. Revise el porcentaje de test y la semilla."
        )

    return train_df, test_df, "Separación realizada con éxito."
