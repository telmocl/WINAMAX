import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression

def probar_persistencia_joblib():
    df = pd.DataFrame({
        "superficie": [50, 70, 90, 120, 150],
        "habitaciones": [1, 2, 3, 3, 4],
        "precio": [150000, 200000, 260000, 330000, 410000]
    })
    
    X = df[["superficie", "habitaciones"]]
    y = df["precio"]
    
    modelo = LinearRegression()
    modelo.fit(X, y)
    
    datos_modelo = {
        "modelo": modelo,
        "columnas_entrada": ["superficie", "habitaciones"],
        "columna_salida": "precio",
        "formula": f"precio = {modelo.coef_[0]:.2f}*superficie + {modelo.coef_[1]:.2f}*habitaciones + {modelo.intercept_:.2f}",
        "metricas": {"r2_score": float(modelo.score(X, y))},
        "descripcion": "Modelo de regresión lineal para la estimación de precios."
    }
    
    ruta_archivo = "prototipos/modelo_prueba.joblib"
    joblib.dump(datos_modelo, ruta_archivo)
    print(f"Modelo guardado en: {ruta_archivo}")
    
    datos_cargados = joblib.load(ruta_archivo)
    modelo_recuperado = datos_cargados["modelo"]
    
    print("\n--- Metadatos ---")
    print("Descripción:", datos_cargados["descripcion"])
    print("Fórmula:", datos_cargados["formula"])
    print("Métricas:", datos_cargados["metricas"])
    
    pred_original = modelo.predict(X[:1])
    pred_cargado = modelo_recuperado.predict(X[:1])
    
    assert pred_original[0] == pred_cargado[0], "Las predicciones no coinciden"
    print("\n✓ Validación exitosa: Las predicciones coinciden exactamente.")

if __name__ == "__main__":
    probar_persistencia_joblib()