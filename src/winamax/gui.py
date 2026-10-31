"""Interfaz gráfica para cargar, revisar datasets y seleccionar variables.

La lectura de archivos la hace winamax.data_loader; la validación de
columnas la hace winamax.selector_logic; la separación winamax.separacion_logica
y el preprocesamiento de nulos winamax.preprocessing.
"""

import sys
from pathlib import Path

import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from winamax.data_loader import DataLoaderError, load_data
from winamax.separacion_logica import realizar_separacion_datos
from winamax.selector_logic import validar_seleccion_columnas

# Importación de tus funciones de detección y preprocesamiento de nulos
from winamax.utilidades import (
    detectar_nulos,
    preprocesar_eliminar_filas,
    preprocesar_media,
    preprocesar_mediana,
    preprocesar_constante,
)

FILTRO_ARCHIVOS = "Datasets (*.csv *.xlsx *.xls *.sqlite *.db)"


class ModeloTabla(QAbstractTableModel):
  """Adapta un DataFrame de pandas para mostrarlo en un QTableView."""

  def __init__(self, datos: pd.DataFrame):
    super().__init__()
    self._datos = datos

  def rowCount(self, parent=QModelIndex()):
    return len(self._datos)

  def columnCount(self, parent=QModelIndex()):
    return len(self._datos.columns)

  def data(self, index, role=Qt.DisplayRole):
    if role != Qt.DisplayRole or not index.isValid():
      return None
    valor = self._datos.iat[index.row(), index.column()]
    return "NaN" if pd.isna(valor) else str(valor)

  def headerData(self, section, orientation, role=Qt.DisplayRole):
    if role != Qt.DisplayRole:
      return None
    if orientation == Qt.Horizontal:
      return str(self._datos.columns[section])
    return str(section + 1)


class VentanaPrincipal(QMainWindow):

  def __init__(self):
    super().__init__()
    self.setWindowTitle("WINAMAX - Pipeline de Machine Learning")
    self.resize(950, 850)

    # Estado del pipeline
    self.datos: pd.DataFrame | None = None
    self.ruta_actual: Path | None = None
    self.modelo_tabla: ModeloTabla | None = None
    self.features_seleccionadas: list[str] = []
    self.target_seleccionado: str | None = None
    self.train_df: pd.DataFrame | None = None
    self.test_df: pd.DataFrame | None = None
    
    # Datos preprocesados finales listos para el modelo
    self.train_processed: pd.DataFrame | None = None
    self.test_processed: pd.DataFrame | None = None

    widget_central = QWidget()
    self.setCentralWidget(widget_central)
    layout_principal = QVBoxLayout(widget_central)

    # --- 1. Selección de archivo ---
    grupo_archivo = QGroupBox("Dataset")
    layout_archivo = QHBoxLayout(grupo_archivo)

    self.btn_cargar = QPushButton("Cargar dataset")
    self.btn_cargar.setMinimumHeight(36)
    self.btn_cargar.clicked.connect(self.seleccionar_archivo)
    layout_archivo.addWidget(self.btn_cargar)

    self.lbl_ruta = QLabel("Ningún archivo cargado")
    self.lbl_ruta.setStyleSheet("color: gray;")
    self.lbl_ruta.setTextInteractionFlags(Qt.TextSelectableByMouse)
    layout_archivo.addWidget(self.lbl_ruta, stretch=1)

    layout_principal.addWidget(grupo_archivo)

    # --- 2. Tabla de datos ---
    grupo_tabla = QGroupBox("Datos")
    layout_tabla = QVBoxLayout(grupo_tabla)

    self.tabla = QTableView()
    self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
    self.tabla.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
    self.tabla.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
    layout_tabla.addWidget(self.tabla)

    layout_principal.addWidget(grupo_tabla, stretch=1)

    # --- 3. Selección de Variables ---
    self.grupo_variables = QGroupBox("Selección de Variables para el Modelo")
    layout_grupo_vars = QVBoxLayout(self.grupo_variables)

    layout_dos_columnas = QHBoxLayout()

    # Columna Izquierda: Entradas (Features)
    layout_entradas = QVBoxLayout()
    layout_entradas.addWidget(QLabel("Entradas:"))
    self.list_features = QListWidget()
    self.list_features.setSelectionMode(QListWidget.MultiSelection)
    layout_entradas.addWidget(self.list_features)
    layout_dos_columnas.addLayout(layout_entradas, stretch=2)

    # Columna Derecha: Salida (Target) y Botón Aceptar
    layout_derecha = QVBoxLayout()
    layout_derecha.addWidget(QLabel("Salida:"))
    self.combo_target = QComboBox()
    layout_derecha.addWidget(self.combo_target)

    layout_derecha.addStretch(1)

    self.btn_confirmar_vars = QPushButton("Aceptar")
    self.btn_confirmar_vars.setMinimumHeight(36)
    self.btn_confirmar_vars.clicked.connect(self.confirmar_variables)
    layout_derecha.addWidget(self.btn_confirmar_vars)

    layout_dos_columnas.addLayout(layout_derecha, stretch=1)
    layout_grupo_vars.addLayout(layout_dos_columnas)

    layout_principal.addWidget(self.grupo_variables)

    # --- 4. Separación de Datos (Train / Test) ---
    self.grupo_split = QGroupBox("Separación de Datos (Train / Test)")
    self.grupo_split.setEnabled(False)
    layout_split = QVBoxLayout(self.grupo_split)

    layout_params = QHBoxLayout()
    layout_params.addWidget(QLabel("% Test (1-99):"))
    self.input_test_pct = QLineEdit("20.0")
    layout_params.addWidget(self.input_test_pct)

    layout_params.addWidget(QLabel("Semilla (Seed):"))
    self.input_seed = QLineEdit("42")
    layout_params.addWidget(self.input_seed)

    layout_split.addLayout(layout_params)

    self.btn_separar = QPushButton("Separar datos")
    self.btn_separar.setMinimumHeight(32)
    self.btn_separar.clicked.connect(self.ejecutar_separacion)
    layout_split.addWidget(self.btn_separar)

    layout_principal.addWidget(self.grupo_split)

    # --- 5. Preprocesamiento de Valores Inexistentes ---
    self.grupo_preproc = QGroupBox("Preprocesamiento de Valores Inexistentes")
    self.grupo_preproc.setEnabled(False)
    layout_preproc = QVBoxLayout(self.grupo_preproc)

    self.lbl_info_nulos = QLabel("Realice la separación de datos para detectar valores inexistentes.")
    layout_preproc.addWidget(self.lbl_info_nulos)

    # Opciones de estrategia
    layout_estrategias = QVBoxLayout()
    self.rb_drop = QRadioButton("Eliminar las filas que contengan valores inexistentes")
    self.rb_mean = QRadioButton("Rellenar con la media de cada columna (Train)")
    self.rb_median = QRadioButton("Rellenar con la mediana de cada columna (Train)")
    self.rb_constant = QRadioButton("Rellenar con un valor constante:")
    
    self.rb_mean.setChecked(True)  # Por defecto

    layout_estrategias.addWidget(self.rb_drop)
    layout_estrategias.addWidget(self.rb_mean)
    layout_estrategias.addWidget(self.rb_median)
    
    # Sublayout para constante
    layout_constante = QHBoxLayout()
    layout_constante.addWidget(self.rb_constant)
    self.input_constante = QLineEdit()
    self.input_constante.setEnabled(False)
    layout_constante.addWidget(self.input_constante)
    layout_estrategias.addLayout(layout_constante)

    layout_preproc.addLayout(layout_estrategias)

    # Habilitar/deshabilitar campo constante dinámicamente
    self.rb_constant.toggled.connect(self.input_constante.setEnabled)

    self.btn_aplicar_preproc = QPushButton("Aplicar preprocesado")
    self.btn_aplicar_preproc.setMinimumHeight(32)
    self.btn_aplicar_preproc.clicked.connect(self.aplicar_preprocesamiento)
    layout_preproc.addWidget(self.btn_aplicar_preproc)

    layout_principal.addWidget(self.grupo_preproc)

    # --- 6. Creación del Modelo ---
    self.grupo_modelo = QGroupBox("Creación y Evaluación del Modelo")
    self.grupo_modelo.setEnabled(False)
    layout_modelo = QVBoxLayout(self.grupo_modelo)
    
    self.btn_crear_modelo = QPushButton("Crear Modelo de Regresión Lineal")
    self.btn_crear_modelo.setMinimumHeight(36)
    self.btn_crear_modelo.clicked.connect(self.crear_modelo)
    layout_modelo.addWidget(self.btn_crear_modelo)

    layout_principal.addWidget(self.grupo_modelo)

  def seleccionar_archivo(self):
    archivo, _ = QFileDialog.getOpenFileName(
        self, "Seleccionar dataset", "", FILTRO_ARCHIVOS
    )
    if not archivo:
      return
    self.cargar_archivo(Path(archivo))

  def cargar_archivo(self, ruta: Path):
    ruta = ruta.resolve()
    try:
      datos = load_data(ruta)
    except DataLoaderError as e:
      QMessageBox.critical(self, "Error al cargar el archivo", str(e))
      return

    self.datos = datos
    self.ruta_actual = ruta
    self.lbl_ruta.setText(str(ruta))
    self.lbl_ruta.setStyleSheet("color: black;")

    self.modelo_tabla = ModeloTabla(datos)
    self.tabla.setModel(self.modelo_tabla)
    self.tabla.resizeColumnsToContents()

    self.list_features.clear()
    self.combo_target.clear()
    self.combo_target.addItem("-- Seleccionar Salida --", None)

    for col in datos.columns:
      col_str = str(col)
      self.list_features.addItem(QListWidgetItem(col_str))
      self.combo_target.addItem(col_str, col_str)

    self.features_seleccionadas = []
    self.target_seleccionado = None
    self.train_df = None
    self.test_df = None
    self.train_processed = None
    self.test_processed = None
    
    self.grupo_split.setEnabled(False)
    self.grupo_preproc.setEnabled(False)
    self.grupo_modelo.setEnabled(False)

  def confirmar_variables(self):
    if self.datos is None:
      QMessageBox.warning(self, "Error", "Primero debes cargar un dataset válido.")
      return

    features = [item.text() for item in self.list_features.selectedItems()]
    target = self.combo_target.currentData()

    valido, mensaje = validar_seleccion_columnas(self.datos, features, target)

    if not valido:
      QMessageBox.critical(self, "Error de Selección", mensaje)
      self.grupo_split.setEnabled(False)
      self.grupo_preproc.setEnabled(False)
      self.grupo_modelo.setEnabled(False)
    else:
      self.features_seleccionadas = features
      self.target_seleccionado = target
      self.train_df = None
      self.test_df = None
      self.train_processed = None
      self.test_processed = None
      
      self.grupo_split.setEnabled(True)
      self.grupo_preproc.setEnabled(False)
      self.grupo_modelo.setEnabled(False)
      
      QMessageBox.information(
          self,
          "Selección Confirmada",
          f"<b>Variables confirmadas correctamente.</b><br><br>"
          f"<b>Entradas:</b> {', '.join(features)}<br>"
          f"<b>Salida:</b> {target}",
      )

  def ejecutar_separacion(self):
    if self.datos is None:
      QMessageBox.warning(self, "Error", "No hay ningún dataset cargado.")
      return

    try:
      test_pct = float(self.input_test_pct.text())
    except ValueError:
      QMessageBox.critical(self, "Error de Validación", "El porcentaje de test debe ser un número válido.")
      return

    try:
      seed = int(self.input_seed.text())
    except ValueError:
      QMessageBox.critical(self, "Error de Validación", "La semilla (seed) debe ser un número entero.")
      return

    train_df, test_df, mensaje = realizar_separacion_datos(
        self.datos, test_size_pct=test_pct, random_state=seed
    )

    if train_df is None or test_df is None:
      QMessageBox.critical(self, "Error en la Separación", mensaje)
      return

    self.train_df = train_df
    self.test_df = test_df
    self.train_processed = None
    self.test_processed = None
    self.grupo_modelo.setEnabled(False)

    # Detectar nulos usando tu función 'detectar_nulos'
    columnas_modelo = self.features_seleccionadas + [self.target_seleccionado]
    resultado_nulos = detectar_nulos(self.train_df, self.test_df, columnas_modelo)
    train_m = resultado_nulos["train"]
    test_m = resultado_nulos["test"]

    total_train_nulos = sum(train_m.values())
    total_test_nulos = sum(test_m.values())

    info_texto = f"<b>{mensaje}</b><br><br><b>Valores inexistentes detectados:</b><br>"
    for col in columnas_modelo:
      info_texto += f"- <b>{col}</b> -> Train: {train_m[col]} | Test: {test_m[col]}<br>"

    if total_train_nulos == 0 and total_test_nulos == 0:
      info_texto += "<br><i>No hay valores inexistentes. Puede continuar sin preprocesar o aplicar una estrategia.</i>"
      self.train_processed = self.train_df
      self.test_processed = self.test_df
      self.grupo_modelo.setEnabled(True)

    self.lbl_info_nulos.setText(info_texto)
    self.grupo_preproc.setEnabled(True)

    QMessageBox.information(self, "Separación y Detección Exitosa", info_texto)

  def aplicar_preprocesamiento(self):
    if self.train_df is None or self.test_df is None:
      QMessageBox.warning(self, "Error", "Debe separar los datos antes de preprocesar.")
      return

    columnas_modelo = self.features_seleccionadas + [self.target_seleccionado]

    try:
      if self.rb_drop.isChecked():
        train_res, test_res = preprocesar_eliminar_filas(self.train_df, self.test_df, columnas_modelo)
        
        # Validar si la eliminación deja vacíos los conjuntos
        if train_res.empty or test_res.empty:
          QMessageBox.warning(
              self, 
              "Aviso de Preprocesamiento", 
              "La eliminación de filas dejaría vacío el conjunto de entrenamiento o el de test. No se aplicó el cambio."
          )
          return

        dropped_train = len(self.train_df) - len(train_res)
        dropped_test = len(self.test_df) - len(test_res)
        msg_exito = (
            f"<b>Preprocesamiento aplicado con éxito (Eliminación de filas):</b><br>"
            f"- Filas eliminadas en Train: {dropped_train}<br>"
            f"- Filas eliminadas en Test: {dropped_test}"
        )

      elif self.rb_mean.isChecked():
        train_res, test_res = preprocesar_media(self.train_df, self.test_df, columnas_modelo)
        msg_exito = "<b>Preprocesamiento aplicado con éxito:</b><br>Valores rellenados usando la <b>MEDIA</b> calculada en el conjunto de entrenamiento."

      elif self.rb_median.isChecked():
        train_res, test_res = preprocesar_mediana(self.train_df, self.test_df, columnas_modelo)
        msg_exito = "<b>Preprocesamiento aplicado con éxito:</b><br>Valores rellenados usando la <b>MEDIANA</b> calculada en el conjunto de entrenamiento."

      elif self.rb_constant.isChecked():
        # Validación de valor constante numérico
        try:
          const_val = float(self.input_constante.text())
        except ValueError:
          QMessageBox.critical(self, "Error de Validación", "El valor constante introducido no es numérico.")
          return

        train_res, test_res = preprocesar_constante(self.train_df, self.test_df, columnas_modelo, const_val)
        msg_exito = f"<b>Preprocesamiento aplicado con éxito:</b><br>Valores rellenados con el valor constante: <b>{const_val}</b>"
      else:
        return

    except Exception as e:
      QMessageBox.critical(self, "Error de Preprocesamiento", str(e))
      return

    # Guardar resultados procesados
    self.train_processed = train_res
    self.test_processed = test_res

    QMessageBox.information(self, "Preprocesamiento Exitoso", msg_exito)

    # Verificar si aún quedan nulos en las columnas seleccionadas
    nulos_restantes_train = train_res[columnas_modelo].isna().sum().sum()
    nulos_restantes_test = test_res[columnas_modelo].isna().sum().sum()

    if nulos_restantes_train == 0 and nulos_restantes_test == 0:
      self.grupo_modelo.setEnabled(True)
    else:
      self.grupo_modelo.setEnabled(False)

  def crear_modelo(self):
    if self.train_processed is None or self.test_processed is None:
      QMessageBox.warning(self, "Error", "Los datos procesados no están listos.")
      return

    QMessageBox.information(
        self,
        "Creación de Modelo",
        "¡Los conjuntos de entrenamiento y test están listos! Aquí se inicializará el modelo de Regresión Lineal.",
    )


def main():
  app = QApplication(sys.argv)
  ventana = VentanaPrincipal()
  ventana.show()
  sys.exit(app.exec())


if __name__ == "__main__":
  main()
  