import pandas as pd  
from sklearn.model_selection import train_test_split

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
            "El porcentaje de test debe ser un numero entre 1 y 99."
        )

    #3. Validar semilla (entero)
    if not isinstance(random_state,int):
        return None, None, "La semilla (seed) debe ser un numero entero."

    #Calcular fraccion de test.
    test_size = test_size_pct / 100.0

    try:
        #Realizar separacion usando scikit-learn 
        train_df, test_df = train_test_split(
            df, test_size = test_size, random_state=random_state
        )

    except Exception as e:
        return None, None, f"Error al realizar la separación: {str(e)}"

    #4. Verificar que ningún conjunto quede vacío.
    if len(train_df) == 0 or len(test_df) == 0:
        return( 
            None, 
            None,
            "El porcentaje elegido deja alguno de los conjuntos vacío. Ajusta el porcentaje"
        )

    return train_df, test_df, "Separacion realizada con éxito."
