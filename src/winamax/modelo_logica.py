"""Módulo de lógica para el entrenamiento y evaluación del modelo de regresión lineal."""

from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


class ModeloInfo:
    """Estructura de datos que encapsula la información completa del modelo."""

    def __init__(
        self,
        modelo: LinearRegression,
        features: List[str],
        target: str,
        formula: str,
        metricas: Dict[str, float],
        descripcion: str = "",
    ):
        self.modelo = modelo
        self.features = features
        self.target = target
        self.formula = formula
        self.metricas = metricas
        self.descripcion = descripcion

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la estructura de datos a un diccionario serializable."""
        return {
            "modelo": self.modelo,
            "features": self.features,
            "target": self.target,
            "formula": self.formula,
            "metricas": self.metricas,
            "descripcion": self.descripcion,
        }


def entrenar_modelo_lineal(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    features: List[str],
    target: str,
    descripcion: str = "",
) -> Tuple[ModeloInfo, Tuple[pd.Series, np.ndarray, pd.Series, np.ndarray]]:
    """Entrena un modelo de regresión lineal, calcula métricas, genera la fórmula y retorna ModeloInfo."""
    # Validación de nulos en las columnas seleccionadas
    cols = features + [target]
    if train_df[cols].isnull().any().any() or test_df[cols].isnull().any().any():
        raise ValueError(
            "Existen valores nulos en las columnas seleccionadas de entrenamiento o test."
        )

    X_train = train_df[features]
    y_train = train_df[target]
    X_test = test_df[features]
    y_test = test_df[target]

    # Ajuste del modelo exclusivamente con entrenamiento
    modelo = LinearRegression()
    modelo.fit(X_train, y_train)

    # Predicciones
    y_pred_train = modelo.predict(X_train)
    y_pred_test = modelo.predict(X_test)

    # Métricas
    metricas = {
        "r2_train": float(r2_score(y_train, y_pred_train)),
        "mse_train": float(mean_squared_error(y_train, y_pred_train)),
        "r2_test": float(r2_score(y_test, y_pred_test)),
        "mse_test": float(mean_squared_error(y_test, y_pred_test)),
    }

    # Generación de la fórmula formateada
    formula = generar_formula_texto(target, features, modelo.coef_, modelo.intercept_)

    modelo_info = ModeloInfo(
        modelo=modelo,
        features=features,
        target=target,
        formula=formula,
        metricas=metricas,
        descripcion=descripcion,
    )

    return modelo_info, (y_train, y_pred_train, y_test, y_pred_test)


def generar_formula_texto(
    target: str, features: List[str], coefs: List[float], intercept: float
) -> str:
    """Genera el texto de la fórmula asegurando un formato limpio (ej. restas si coef < 0)."""
    partes = [f"{target} ="]

    for i, (coef, feat) in enumerate(zip(coefs, features)):
        if coef < 0:
            partes.append(f"- {abs(coef):.4f} * {feat}")
        else:
            signo = "+ " if i > 0 else ""
            partes.append(f"{signo}{coef:.4f} * {feat}")

    if intercept < 0:
        partes.append(f"- {abs(intercept):.4f}")
    else:
        partes.append(f"+ {intercept:.4f}")

    formula = " ".join(partes)
    formula = formula.replace("= + ", "= ")
    return formula