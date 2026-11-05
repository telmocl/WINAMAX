"""Interfaz gráfica para cargar, revisar datasets y seleccionar variables.

La lectura de archivos la hace winamax.data_loader; la validación de
columnas la hace winamax.selector_logic; la separación winamax.separacion_logica;
el preprocesamiento de nulos winamax.preprocessing y el modelo winamax.modelo_logica.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
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
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from winamax.data_loader import DataLoaderError, load_data
from winamax.modelo_logica import entrenar_modelo_lineal
from winamax.separacion_logica import realizar_separacion_datos
from winamax.selector_logic import validar_seleccion_columnas

# Importación de funciones de detección y preprocesamiento de nulos
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
    self.resize(1000, 950)
    self.setMinimumSize(760, 650)
    self.setStyleSheet("""
      QMainWindow, QScrollArea, QWidget {
        background-color: #f5f7fa;
        color: #243247;
        font-family: "Segoe UI", sans-serif;
        font-size: 10pt;
      }
      QScrollArea {
        border: none;
      }
      QGroupBox {
        background-color: #ffffff;
        border: 1px solid #dce3ec;
        border-radius: 8px;
        margin-top: 12px;
        padding: 14px 12px 12px;
        font-weight: 600;
      }
      QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 5px;
        color: #334b68;
      }
      QPushButton {
        background-color: #2563a6;
        color: #ffffff;
        border: none;
        border-radius: 5px;
        padding: 8px 14px;
        min-height: 18px;
        font-weight: 600;
      }
      QPushButton:hover {
        background-color: #1d528d;
      }
      QPushButton:pressed {
        background-color: #174371;
      }
      QPushButton:disabled {
        background-color: #cbd5e1;
        color: #64748b;
      }
      QLineEdit, QComboBox, QListWidget, QTableView, QTableWidget {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 5px;
        padding: 6px;
        selection-background-color: #dbeafe;
        selection-color: #1e3a5f;
      }
      QLineEdit:focus, QComboBox:focus, QListWidget:focus, QTableView:focus {
        border: 1px solid #4b8ac6;
      }
      QTableView, QTableWidget {
        gridline-color: #e2e8f0;
        alternate-background-color: #f8fafc;
      }
      QHeaderView::section {
        background-color: #edf2f7;
        color: #334b68;
        border: none;
        border-right: 1px solid #dce3ec;
        border-bottom: 1px solid #dce3ec;
        padding: 7px;
        font-weight: 600;
      }
      QRadioButton {
        spacing: 7px;
        padding: 3px 0;
      }
      QRadioButton::indicator {
        width: 15px;
        height: 15px;
      }
    """)

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
    self.modelo_entrenado = None

    area_desplazable = QScrollArea()
    area_desplazable.setWidgetResizable(True)
    contenido = QWidget()
    area_desplazable.setWidget(contenido)
    self.setCentralWidget(area_desplazable)
    layout_principal = QVBoxLayout(contenido)
    layout_principal.setContentsMargins(18, 18, 18, 18)
    layout_principal.setSpacing(12)

    # --- 1. Selección de archivo ---
    grupo_archivo = QGroupBox("Dataset")
    layout_archivo = QHBoxLayout(grupo_archivo)

    self.btn_cargar = QPushButton("Cargar dataset")
    self.btn_cargar.setMinimumHeight(36)
    self.btn_cargar.setMaximumWidth(180)
    self.btn_cargar.clicked.connect(self.seleccionar_archivo)
    layout_archivo.addWidget(self.btn_cargar)

    self.lbl_ruta = QLabel("Ningún archivo cargado")
    self.lbl_ruta.setStyleSheet("color: #64748b;")
    self.lbl_ruta.setWordWrap(True)
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
    self.tabla.setAlternatingRowColors(True)
    self.tabla.setMinimumHeight(190)
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
    self.list_features.setMinimumHeight(110)
    layout_entradas.addWidget(self.list_features)
    layout_dos_columnas.addLayout(layout_entradas, stretch=2)

    # Columna Derecha: Salida (Target) y Botón Aceptar
    layout_derecha = QVBoxLayout()
    layout_derecha.addWidget(QLabel("Salida:"))
    self.combo_target = QComboBox()
    self.combo_target.setMinimumHeight(34)
    layout_derecha.addWidget(self.combo_target)

    layout_derecha.addStretch(1)

    self.btn_confirmar_vars = QPushButton("Aceptar")
    self.btn_confirmar_vars.setMinimumHeight(36)
    self.btn_confirmar_vars.setMaximumWidth(180)
    self.btn_confirmar_vars.clicked.connect(self.confirmar_variables)
    layout_derecha.addWidget(self.btn_confirmar_vars, alignment=Qt.AlignLeft)

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
    self.input_test_pct.setMaximumWidth(100)
    layout_params.addWidget(self.input_test_pct)

    layout_params.addWidget(QLabel("Semilla (Seed):"))
    self.input_seed = QLineEdit("42")
    self.input_seed.setMaximumWidth(100)
    layout_params.addWidget(self.input_seed)
    layout_params.addStretch(1)

    layout_split.addLayout(layout_params)

    self.btn_separar = QPushButton("Separar datos")
    self.btn_separar.setMinimumHeight(32)
    self.btn_separar.setMaximumWidth(200)
    self.btn_separar.clicked.connect(self.ejecutar_separacion)
    layout_split.addWidget(self.btn_separar, alignment=Qt.AlignLeft)

    layout_principal.addWidget(self.grupo_split)

    # --- 5. Preprocesamiento de Valores Inexistentes ---
    self.grupo_preproc = QGroupBox("Preprocesamiento de Valores Inexistentes")
    self.grupo_preproc.setEnabled(False)
    layout_preproc = QVBoxLayout(self.grupo_preproc)

    self.lbl_info_nulos = QLabel("Realice la separación de datos para detectar valores inexistentes.")
    self.lbl_info_nulos.setWordWrap(True)
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
    self.input_constante.setMaximumWidth(180)
    self.input_constante.setEnabled(False)
    layout_constante.addWidget(self.input_constante)
    layout_estrategias.addLayout(layout_constante)

    layout_preproc.addLayout(layout_estrategias)

    self.rb_constant.toggled.connect(self.input_constante.setEnabled)

    self.btn_aplicar_preproc = QPushButton("Aplicar preprocesado")
    self.btn_aplicar_preproc.setMinimumHeight(32)
    self.btn_aplicar_preproc.setMaximumWidth(220)
    self.btn_aplicar_preproc.clicked.connect(self.aplicar_preprocesamiento)
    layout_preproc.addWidget(self.btn_aplicar_preproc, alignment=Qt.AlignLeft)

    layout_principal.addWidget(self.grupo_preproc)

    # --- 6. Creación y Evaluación del Modelo ---
    self.grupo_modelo = QGroupBox("Creación y Evaluación del Modelo")
    self.grupo_modelo.setEnabled(False)
    layout_modelo = QVBoxLayout(self.grupo_modelo)
    
    self.btn_crear_modelo = QPushButton("Crear Modelo de Regresión Lineal")
    self.btn_crear_modelo.setMinimumHeight(36)
    self.btn_crear_modelo.setMaximumWidth(260)
    self.btn_crear_modelo.clicked.connect(self.crear_modelo)
    layout_modelo.addWidget(self.btn_crear_modelo, alignment=Qt.AlignLeft)

    # Fórmula del modelo
    self.lbl_formula = QLabel("<b>Fórmula:</b> -")
    self.lbl_formula.setWordWrap(True)
    self.lbl_formula.setStyleSheet("color: #1e3a5f; margin-top: 6px;")
    layout_modelo.addWidget(self.lbl_formula)

    # Métricas de error (Tabla compacta)
    layout_modelo.addWidget(QLabel("Métricas de Error:"))
    self.tabla_metricas = QTableWidget(2, 2)
    self.tabla_metricas.setHorizontalHeaderLabels(["Entrenamiento (Train)", "Test"])
    self.tabla_metricas.setVerticalHeaderLabels(["R² (Coeff)", "MSE (Error)"])
    self.tabla_metricas.setMaximumHeight(95)
    self.tabla_metricas.horizontalHeader().setStretchLastSection(True)
    layout_modelo.addWidget(self.tabla_metricas)

    # Gráfico de ajuste embebido con Matplotlib
    self.fig, self.ax = plt.subplots(figsize=(6, 3.5))
    self.canvas = FigureCanvas(self.fig)
    layout_modelo.addWidget(self.canvas)

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
    self.lbl_ruta.setStyleSheet("color: #243247;")

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
    self.modelo_entrenado = None
    
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
      self.modelo_entrenado = None
      
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
    self.modelo_entrenado = None
    self.grupo_modelo.setEnabled(False)

    # Detectar nulos
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

    self.train_processed = train_res
    self.test_processed = test_res
    self.modelo_entrenado = None

    QMessageBox.information(self, "Preprocesamiento Exitoso", msg_exito)

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

    try:
      modelo, metricas, formula, (y_train, y_pred_train, y_test, y_pred_test) = (
          entrenar_modelo_lineal(
              self.train_processed,
              self.test_processed,
              self.features_seleccionadas,
              self.target_seleccionado,
          )
      )
      self.modelo_entrenado = modelo

      # Mostrar fórmula matemática
      self.lbl_formula.setText(f"<b>Fórmula:</b> {formula}")

      # Mostrar métricas en la tabla de resultados
      self.tabla_metricas.setItem(0, 0, QTableWidgetItem(f"{metricas['r2_train']:.4f}"))
      self.tabla_metricas.setItem(1, 0, QTableWidgetItem(f"{metricas['mse_train']:.4f}"))
      self.tabla_metricas.setItem(0, 1, QTableWidgetItem(f"{metricas['r2_test']:.4f}"))
      self.tabla_metricas.setItem(1, 1, QTableWidgetItem(f"{metricas['mse_test']:.4f}"))

      # Dibujar gráfico de ajuste con Matplotlib
      self.ax.clear()
      if len(self.features_seleccionadas) == 1:
        # Regresión simple: Dispersión Train/Test + Línea de ajuste
        feat = self.features_seleccionadas[0]
        self.ax.scatter(
            self.train_processed[feat],
            y_train,
            color="#2563a6",
            alpha=0.6,
            label="Train",
        )
        self.ax.scatter(
            self.test_processed[feat],
            y_test,
            color="#f97316",
            alpha=0.6,
            label="Test",
        )
        X_line = pd.DataFrame({feat: sorted(self.train_processed[feat].tolist())})
        y_line = modelo.predict(X_line)
        self.ax.plot(X_line, y_line, color="#dc2626", linewidth=2, label="Ajuste")
        self.ax.set_xlabel(feat)
        self.ax.set_ylabel(self.target_seleccionado)
      else:
        # Regresión múltiple: Valores Reales vs Predichos
        self.ax.scatter(
            y_train, y_pred_train, color="#2563a6", alpha=0.6, label="Train"
        )
        self.ax.scatter(
            y_test, y_pred_test, color="#f97316", alpha=0.6, label="Test"
        )
        min_val = min(y_train.min(), y_test.min())
        max_val = max(y_train.max(), y_test.max())
        self.ax.plot(
            [min_val, max_val],
            [min_val, max_val],
            color="#64748b",
            linestyle="--",
            label="Ideal (y=x)",
        )
        self.ax.set_xlabel("Valor Real")
        self.ax.set_ylabel("Valor Predicho")

      self.ax.legend()
      self.ax.grid(True, linestyle=":", alpha=0.7)
      self.fig.tight_layout()
      self.canvas.draw()

      QMessageBox.information(
          self, "Éxito", "Modelo de regresión lineal creado y evaluado correctamente."
      )

    except Exception as e:
      QMessageBox.critical(
          self, "Error al crear el modelo", f"Ocurrió un error durante el entrenamiento: {str(e)}"
      )


def main():
  app = QApplication(sys.argv)
  ventana = VentanaPrincipal()
  ventana.show()
  sys.exit(app.exec())


if __name__ == "__main__":
  main()