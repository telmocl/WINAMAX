"""Interfaz gráfica para cargar, revisar datasets y seleccionar variables.

La lectura de archivos la hace winamax.data_loader; la validación de
columnas la hace winamax.selector_logic y la separación winamax.separacion_logica.
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
    QTableView,
    QVBoxLayout,
    QWidget,
)

from winamax.data_loader import DataLoaderError, load_data
from winamax.separacion_logica import realizar_separacion_datos
from winamax.selector_logic import validar_seleccion_columnas

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
    self.resize(950, 800)

    # Estado del pipeline
    self.datos: pd.DataFrame | None = None
    self.ruta_actual: Path | None = None
    self.modelo_tabla: ModeloTabla | None = None
    self.features_seleccionadas: list[str] = []
    self.target_seleccionado: str | None = None
    self.train_df: pd.DataFrame | None = None
    self.test_df: pd.DataFrame | None = None

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

    # --- 3. Selección de Variables (Diseño en dos columnas) ---
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
    self.grupo_split.setEnabled(False)  # Desactivado por defecto hasta confirmar
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

    # Actualizar la tabla
    self.modelo_tabla = ModeloTabla(datos)
    self.tabla.setModel(self.modelo_tabla)
    self.tabla.resizeColumnsToContents()

    # Resetear selectores y desactivar bloques posteriores
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
    self.grupo_split.setEnabled(False)

  def confirmar_variables(self):
    if self.datos is None:
      QMessageBox.warning(
          self, "Error", "Primero debes cargar un dataset válido."
      )
      return

    features = [item.text() for item in self.list_features.selectedItems()]
    target = self.combo_target.currentData()

    valido, mensaje = validar_seleccion_columnas(self.datos, features, target)

    if not valido:
      QMessageBox.critical(self, "Error de Selección", mensaje)
      self.grupo_split.setEnabled(False)
    else:
      self.features_seleccionadas = features
      self.target_seleccionado = target
      self.train_df = None
      self.test_df = None
      self.grupo_split.setEnabled(True)  # Habilitar paso de separación
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
      QMessageBox.critical(
          self,
          "Error de Validación",
          "El porcentaje de test debe ser un número válido.",
      )
      return

    try:
      seed = int(self.input_seed.text())
    except ValueError:
      QMessageBox.critical(
          self, "Error de Validación", "La semilla (seed) debe ser un número entero."
      )
      return

    train_df, test_df, mensaje = realizar_separacion_datos(
        self.datos, test_size_pct=test_pct, random_state=seed
    )

    if train_df is None or test_df is None:
      QMessageBox.critical(self, "Error en la Separación", mensaje)
      return

    self.train_df = train_df
    self.test_df = test_df

    QMessageBox.information(
        self,
        "Separación Exitosa",
        f"<b>{mensaje}</b><br><br>"
        f"<b>Filas de Entrenamiento (Train):</b> {len(train_df)}<br>"
        f"<b>Filas de Test:</b> {len(test_df)}",
    )


def main():
  app = QApplication(sys.argv)
  ventana = VentanaPrincipal()
  ventana.show()
  sys.exit(app.exec())


if __name__ == "__main__":
  main()