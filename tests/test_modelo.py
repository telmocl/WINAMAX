"""Pruebas unitarias para la lógica del modelo de regresión lineal."""

import pandas as pd
import pytest
from winamax.modelo_logica import entrenar_modelo_lineal, generar_formula_texto


def test_generar_formula_negativa():
  formula = generar_formula_texto("precio", ["habitaciones"], [-2.54321], 10.5)
  assert "precio = -2.5432 * habitaciones + 10.5000" in formula or "- 2.5432" in formula


def test_entrenar_modelo_exitoso():
    df = pd.DataFrame(
        {
            "x1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "y": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
        }
    )
    train = df.iloc[:8]
    test = df.iloc[8:]

    modelo_info, _ = entrenar_modelo_lineal(
        train, test, ["x1"], "y"
    )

    assert modelo_info.modelo is not None
    assert modelo_info.metricas["r2_train"] > 0.99
    assert "y =" in modelo_info.formula