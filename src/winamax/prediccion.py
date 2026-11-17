def calcular_prediccion(modelo_info: dict, valores_entrada: dict[str, float]) -> float:
    """
    Calcula el valor predicho aplicando la ecuación del modelo 
    (intercepto + suma de coeficientes * valores).
    """
    columnas = modelo_info["columnas_entrada"]
    coeficientes = modelo_info["coeficientes"]
    intercepto = float(modelo_info["intercepto"])

    resultado = intercepto
    for col, coef in zip(columnas, coeficientes):
        if col not in valores_entrada:
            raise ValueError(f"Falta el valor para la variable: {col}")
        resultado += float(coef) * float(valores_entrada[col])

    return resultado