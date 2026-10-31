"""
Prueba de concepto: Regresión Lineal con scikit-learn
Ubicación: prototipos/regresion_lineal.py
"""

from pathlib import Path
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


def main():
  
  data_path = Path("data/housing.csv")

  if not data_path.exists():
    raise FileNotFoundError(
        f"No se encontró el archivo de datos en: {data_path}. Asegúrate de"
        " colocarlo en data/"
    )

  df = pd.read_csv(data_path)
  print(f"--> Datos cargados exitosamente desde {data_path}")
  print(f"Dimensiones del dataset original: {df.shape}")

  
  df = df.dropna()
  print(f"Dimensiones tras eliminar valores nulos (NaN): {df.shape}\n")

  
  df_numeric = df.select_dtypes(include=["number"])
  print(
      "Dimensiones tras filtrar solo columnas numéricas:"
      f" {df_numeric.shape}\n"
  )

  if df_numeric.empty or df_numeric.shape[1] < 2:
    raise ValueError(
        "El dataset filtrado no tiene suficientes columnas numéricas para una"
        " regresión."
    )

  
  X = df_numeric.iloc[:, :-1]
  y = df_numeric.iloc[:, -1]

  
  X_train, X_test, y_train, y_test = train_test_split(
      X, y, test_size=0.2, random_state=42
  )

 
  model = LinearRegression()
  model.fit(X_train, y_train)

  
  intercepto = model.intercept_
  coeficientes = model.coef_
  columnas = X.columns

  
  formula_terms = [
      f"({coef:.4f} * {col})" for coef, col in zip(coeficientes, columnas)
  ]
  formula = f"{y.name} = " + " + ".join(formula_terms) + f" + {intercepto:.4f}"

  print("=== FÓRMULA DEL MODELO ===")
  print(formula)
  print("\n" + "=" * 30 + "\n")

  
  y_train_pred = model.predict(X_train)
  y_test_pred = model.predict(X_test)

  ecm_train = mean_squared_error(y_train, y_train_pred)
  r2_train = r2_score(y_train, y_train_pred)

  ecm_test = mean_squared_error(y_test, y_test_pred)
  r2_test = r2_score(y_test, y_test_pred)

  print("=== EVALUACIÓN DEL MODELO ===")
  print(f"[Entrenamiento] ECM: {ecm_train:.4f} | R²: {r2_train:.4f}")
  print(f"[Test          ] ECM: {ecm_test:.4f} | R²: {r2_test:.4f}")
  print("\n" + "=" * 30 + "\n")

  
  ejemplo_nuevo = X_test.iloc[[0]]
  prediccion_nueva = model.predict(ejemplo_nuevo)

  print("=== PREDICCIÓN DE EJEMPLO ===")
  print(f"Valores de entrada:\n{ejemplo_nuevo.to_string(index=False)}")
  print(f"Predicción de salida: {prediccion_nueva[0]:.4f}")
  print(f"Valor real (referencia): {y_test.iloc[0]}")


if __name__ == "__main__":
  main()