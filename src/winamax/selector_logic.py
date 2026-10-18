import pandas as pd


def validar_seleccion_columnas(
    df: pd.DataFrame, features: list[str], target: str | None
) -> tuple[bool, str]:
  """Valida las columnas seleccionadas para el modelo.

  Devuelve: (es_valido: bool, mensaje: str)
  """
  # 1. Verificar selección vacía
  if not features or not target:
    faltantes = []
    if not features:
      faltantes.append("al menos una columna de entrada (features)")
    if not target:
      faltantes.append("una columna de salida (target)")
    return False, f"Falta seleccionar: {' y '.join(faltantes)}."

  # 2. Verificar que la salida no esté en las entradas
  if target in features:
    return (
        False,
        f"La columna de salida '{target}' no puede seleccionarse también como"
        " entrada.",
    )

  # 3. Verificar que existan en el DataFrame
  cols_invalidas = [col for col in features + [target] if col not in df.columns]
  if cols_invalidas:
    return (
        False,
        f"Las siguientes columnas no existen en el dataset: {', '.join(cols_invalidas)}.",
    )

  # 4. Verificar que sean numéricas
  cols_no_numericas = [
      col
      for col in features + [target]
      if not pd.api.types.is_numeric_dtype(df[col])
  ]
  if cols_no_numericas:
    return (
        False,
        f"Las siguientes columnas no son numéricas y no se pueden usar en"
        f" regresión: {', '.join(cols_no_numericas)}.",
    )

  return True, "Selección válida."