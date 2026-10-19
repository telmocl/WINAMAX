"""Interfaz gráfica para cargar, revisar datasets y seleccionar variables.

La lectura de archivos la hace winamax.data_loader; la validación de
columnas la hace winamax.selector_logic.
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
    self.setWindowTitle("WINAMAX - Carga de datos y Selección de Variables")
    self.resize(900, 750)

    # Estado para los pasos siguientes (columnas, train/test, modelo...)
    self.datos: pd.DataFrame | None = None
    self.ruta_actual: Path | None = None
    self.modelo_tabla: ModeloTabla | None = None
    self.features_seleccionadas: list[str] = []
    self.target_seleccionado: str | None = None

    widget_central = QWidget()
    self.setCentralWidget(widget_central)
    layout_principal = QVBoxLayout(widget_central)

    # --- Selección de archivo ---
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

    # --- Tabla con scroll horizontal y vertical ---
    grupo_tabla = QGroupBox("Datos")
    layout_tabla = QVBoxLayout(grupo_tabla)

    self.tabla = QTableView()
    self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
    self.tabla.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
    self.tabla.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
    layout_tabla.addWidget(self.tabla)

    layout_principal.addWidget(grupo_tabla, stretch=1)

    # --- Selección de Variables (Features y Target) ---
    grupo_variables = QGroupBox("Selección de Variables para el Modelo")
    layout_vars = QVBoxLayout(grupo_variables)

    layout_vars.addWidget(
        QLabel("Columnas de Entrada (Features) - Selección Múltiple:")
    )
    self.list_features = QListWidget()
    self.list_features.setSelectionMode(QListWidget.MultiSelection)
    self.list_features.setMaximumHeight(120)
    layout_vars.addWidget(self.list_features)

    layout_vars.addWidget(QLabel("Columna de Salida (Target) - Selección Única:"))
    self.combo_target = QComboBox()
    layout_vars.addWidget(self.combo_target)

    self.btn_confirmar_vars = QPushButton("Confirmar Selección de Variables")
    self.btn_confirmar_vars.setMinimumHeight(32)
    self.btn_confirmar_vars.clicked.connect(self.confirmar_variables)
    layout_vars.addWidget(self.btn_confirmar_vars)

    layout_principal.addWidget(grupo_variables)

  def seleccionar_archivo(self):
    archivo, _ = QFileDialog.getOpenFileName(
        self, "Seleccionar dataset", "", FILTRO_ARCHIVOS
    )
    if not archivo:
      # El usuario cerró el explorador: se mantiene el estado anterior.
      return
    self.cargar_archivo(Path(archivo))

  def cargar_archivo(self, ruta: Path):
    ruta = ruta.resolve()
    try:
      datos = load_data(ruta)
    except DataLoaderError as e:
      # Tras un error se conservan los datos cargados antes.
      QMessageBox.critical(self, "Error al cargar el archivo", str(e))
      return

    self.datos = datos
    self.ruta_actual = ruta
    self.lbl_ruta.setText(str(ruta))
    self.lbl_ruta.setStyleSheet("color: black;")

    # Actualizar la tabla de datos
    self.modelo_tabla = ModeloTabla(datos)
    self.tabla.setModel(self.modelo_tabla)
    self.tabla.resizeColumnsToContents()

    # Actualizar los selectores de variables y reiniciar selecciones previas
    self.list_features.clear()
    self.combo_target.clear()
    self.features_seleccionadas = []
    self.target_seleccionado = None

    self.combo_target.addItem("-- Seleccionar Salida --", None)

    for col in datos.columns:
      col_str = str(col)
      self.list_features.addItem(QListWidgetItem(col_str))
      self.combo_target.addItem(col_str, col_str)

  def confirmar_variables(self):
    if self.datos is None:
      QMessageBox.warning(
          self, "Error", "Primero debes cargar un dataset válido."
      )
      return

    # Obtener variables elegidas
    features = [item.text() for item in self.list_features.selectedItems()]
    target = self.combo_target.currentData()

    # Validar mediante la lógica independiente
    valido, mensaje = validar_seleccion_columnas(self.datos, features, target)

    if not valido:
      QMessageBox.critical(self, "Error de Selección", mensaje)
    else:
      QMessageBox.information(
          self,
          "Selección Confirmada",
          f"<b>Variables confirmadas con éxito:</b><br><br>"
          f"<b>Entrada(s):</b> {', '.join(features)}<br>"
          f"<b>Salida:</b> {target}",
      )
      # Guardar selección para el pipeline posterior (división train/test, modelo, etc.)
      self.features_seleccionadas = features
      self.target_seleccionado = target


def main():
  app = QApplication(sys.argv)
  ventana = VentanaPrincipal()
  ventana.show()
  sys.exit(app.exec())


if __name__ == "__main__":
  main()