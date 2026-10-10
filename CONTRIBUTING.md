## Pruebas

- Ejecutar todas las pruebas: `uv run pytest` (desde la raíz del repositorio).
- Cada módulo de la aplicación tiene su archivo de pruebas en `tests/`
  (por ejemplo, `tests/test_importacion.py`).
- Las pruebas importan el código por el nombre del paquete (`from winamax... import ...`),
  sin tocar `sys.path`.
- Los datos se definen dentro de la propia prueba: unas pocas filas con valores
  conocidos, incluidos los casos especiales (valores inexistentes, columnas no numéricas).
  No se usan archivos del repositorio ni de la carpeta `data/`.
- Si una prueba necesita un archivo, se crea en una carpeta temporal con `tmp_path`:

      def test_importar_csv(tmp_path):
          ruta = tmp_path / "datos.csv"
          ruta.write_text("x,y\n1,2\n3,4\n")
          ...

### Reglas de fusión

- Antes de fusionar una rama (`feature`, `fix` o `docs`) en `dev`: actualizarla con
  los últimos cambios de `dev` y ejecutar `uv run pytest`. Solo se fusiona si todas pasan.
- `dev` solo se fusiona en `main` si todas las pruebas pasan sobre `dev`.