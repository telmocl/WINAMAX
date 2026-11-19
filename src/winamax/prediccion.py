def calcular_prediccion(modelo_info, valores_entrada: dict[str, float]) -> float:
  """Calcula el valor predicho aplicando la ecuación del modelo (intercepto + suma de coeficientes * valores)."""

  def _leer(obj, clave, por_defecto=None):
    if isinstance(obj, dict):
      return obj.get(clave, por_defecto)
    return getattr(obj, clave, por_defecto)

  columnas = _leer(modelo_info, "columnas_entrada") or _leer(modelo_info, "features")
  coeficientes = _leer(modelo_info, "coeficientes")
  intercepto = _leer(modelo_info, "intercepto")

  if coeficientes is None or intercepto is None:
    modelo_sk = _leer(modelo_info, "modelo")
    if modelo_sk is not None:
      if columnas is None and hasattr(modelo_sk, "feature_names_in_"):
        columnas = list(modelo_sk.feature_names_in_)
      coeficientes = modelo_sk.coef_
      intercepto = modelo_sk.intercept_

  if columnas is None or coeficientes is None or intercepto is None:
    raise ValueError("El modelo no contiene columnas, coeficientes o intercepto válidos.")

  resultado = float(intercepto)
  for col, coef in zip(columnas, coeficientes):
    if col not in valores_entrada:
      raise ValueError(f"Falta el valor para la variable: {col}")
    resultado += float(coef) * float(valores_entrada[col])

  return resultado