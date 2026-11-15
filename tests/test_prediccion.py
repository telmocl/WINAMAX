import numpy as np
import pytest
from sklearn.linear_model import LinearRegression
from winamax.prediccion import calcular_prediccion

def test_prediccion_coincide_con_calculo_manual():
    # Creamos datos con fórmula exacta: y = 2.0*x1 + 3.0*x2 + 5.0
    X = np.array([[1.0, 1.0], [2.0, 1.0], [1.0, 2.0], [3.0, 2.0]])
    y = 2.0 * X[:, 0] + 3.0 * X[:, 1] + 5.0

    reg = LinearRegression().fit(X, y)

    modelo_info = {
        "coeficientes": reg.coef_.tolist(),
        "intercepto": float(reg.intercept_),
        "columnas_entrada": ["x1", "x2"],
        "columna_salida": "y",
    }

    # Cálculo manual para x1 = 4.0, x2 = 3.0 -> 2(4) + 3(3) + 5 = 22.0
    valor_esperado = 22.0
    resultado = calcular_prediccion(modelo_info, {"x1": 4.0, "x2": 3.0})

    assert resultado == pytest.approx(valor_esperado)