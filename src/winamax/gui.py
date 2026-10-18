"""Interfaz gráfica para cargar y revisar datasets.

La lectura de archivos la hace winamax.data_loader; este módulo solo
se ocupa de mostrar el botón, la ruta, la tabla y los errores.
"""

import sys
from pathlib import Path

import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from winamax.data_loader import DataLoaderError, load_data

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
        self.setWindowTitle("WINAMAX - Carga de datos")
        self.resize(900, 600)

        # Estado para los pasos siguientes (columnas, train/test, modelo...)
        self.datos: pd.DataFrame | None = None
        self.ruta_actual: Path | None = None
        self.modelo_tabla: ModeloTabla | None = None

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

        self.modelo_tabla = ModeloTabla(datos)
        self.tabla.setModel(self.modelo_tabla)
        self.tabla.resizeColumnsToContents()


def main():
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()