"""Interfaz gráfica para cargar, revisar datasets y seleccionar variables."""

import logging
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QObject,
    Qt,
    QThread,
    Signal,
)
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QTableView,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from winamax.data_loader import DataLoaderError, load_data
from winamax.modelo_logica import ModeloInfo, entrenar_modelo_lineal
from winamax.persistencia import EXTENSION, asegurar_extension, guardar_modelo, cargar_modelo
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

logger = logging.getLogger(__name__)

FILTRO_ARCHIVOS = "Datasets (*.csv *.xlsx *.xls *.sqlite *.db)"

TEXTO_INICIO = (
    "Para empezar, cargue un dataset para crear un modelo "
    "o cargue un modelo guardado."
)


class ModeloTabla(QAbstractTableModel):
  """Adapta un DataFrame de pandas para mostrarlo en un QTableView.

  Técnica para datasets grandes: scroll virtual. QTableView + un modelo
  propio solo pide (data()) las celdas visibles en cada momento, por lo que
  no se crean widgets ni items para las decenas de miles de filas.
  """

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


class TrabajadorCarga(QObject):
  """Carga un dataset en un hilo secundario para no bloquear la ventana."""

  terminado = Signal(object)  # DataFrame cargado
  fallido = Signal(str)       # mensaje apto para el usuario

  def __init__(self, ruta: Path):
    super().__init__()
    self._ruta = ruta

  def ejecutar(self):
    try:
      datos = load_data(self._ruta)
    except DataLoaderError as e:
      logger.warning("Error al cargar %s: %s", self._ruta, e)
      self.fallido.emit(str(e))
    except Exception:
      logger.exception("Error inesperado al cargar %s", self._ruta)
      self.fallido.emit("No se pudo leer el archivo.")
    else:
      self.terminado.emit(datos)


class VentanaPrincipal(QMainWindow):

  def __init__(self):
    super().__init__()
    self.setWindowTitle("WINAMAX - Pipeline de Machine Learning")

    # Tamaño inicial adaptado a la pantalla (válido para 1366x768).
    pantalla = QGuiApplication.primaryScreen().availableGeometry()
    self.resize(min(1000, pantalla.width()), min(720, pantalla.height()))
    self.setMinimumSize(640, 480)

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
      QGroupBox:disabled {
        color: #94a3b8;
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
      QLineEdit, QComboBox, QListWidget, QTableView, QTableWidget, QTextEdit {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 5px;
        padding: 6px;
        selection-background-color: #dbeafe;
        selection-color: #1e3a5f;
      }
      QLineEdit:focus, QComboBox:focus, QListWidget:focus, QTableView:focus, QTableWidget:focus, QTextEdit:focus {
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
      QStatusBar {
        background-color: #edf2f7;
        border-top: 1px solid #dce3ec;
      }
      QProgressBar {
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        background-color: #ffffff;
        max-height: 14px;
      }
      QProgressBar::chunk {
        background-color: #2563a6;
      }
    """)

    # Estado del pipeline
    self.datos: pd.DataFrame | None = None
    self.ruta_actual: Path | None = None
    self.nombre_dataset: str | None = None
    self.modelo_tabla: ModeloTabla | None = None
    self.features_seleccionadas: list[str] = []
    self.target_seleccionado: str | None = None
    self.train_df: pd.DataFrame | None = None
    self.test_df: pd.DataFrame | None = None

    # Datos preprocesados y modelo
    self.train_processed: pd.DataFrame | None = None
    self.test_processed: pd.DataFrame | None = None
    self.modelo_info: ModeloInfo | None = None
    self.modelo_origen: str | None = None   # "creado" | "cargado"
    self.cambios_sin_guardar: bool = False

    # Carga en segundo plano
    self._hilo: QThread | None = None
    self._trabajador: TrabajadorCarga | None = None
    self._ruta_en_carga: Path | None = None
    self._estados_previos: dict[QWidget, bool] = {}

    area_desplazable = QScrollArea()
    area_desplazable.setWidgetResizable(True)
    contenido = QWidget()
    area_desplazable.setWidget(contenido)
    self.setCentralWidget(area_desplazable)
    layout_principal = QVBoxLayout(contenido)
    layout_principal.setContentsMargins(18, 18, 18, 18)
    layout_principal.setSpacing(12)

    # --- 1. Selección de archivo y Carga de Modelo ---
    grupo_archivo = QGroupBox("1. Cargar datos (o cargar un modelo guardado)")
    layout_archivo = QHBoxLayout(grupo_archivo)

    self.btn_cargar = QPushButton("Cargar dataset")
    self.btn_cargar.setMinimumHeight(36)
    self.btn_cargar.setMaximumWidth(160)
    self.btn_cargar.clicked.connect(self.seleccionar_archivo)
    layout_archivo.addWidget(self.btn_cargar)

    self.btn_cargar_modelo = QPushButton("Cargar modelo")
    self.btn_cargar_modelo.setMinimumHeight(36)
    self.btn_cargar_modelo.setMaximumWidth(160)
    self.btn_cargar_modelo.clicked.connect(self.dialogo_cargar_modelo)
    layout_archivo.addWidget(self.btn_cargar_modelo)

    self.lbl_ruta = QLabel(TEXTO_INICIO)
    self.lbl_ruta.setStyleSheet("color: #64748b;")
    self.lbl_ruta.setWordWrap(True)
    self.lbl_ruta.setTextInteractionFlags(Qt.TextSelectableByMouse)
    layout_archivo.addWidget(self.lbl_ruta, stretch=1)

    layout_principal.addWidget(grupo_archivo)

    # --- Tabla de datos ---
    self.grupo_tabla = QGroupBox("Datos")
    layout_tabla = QVBoxLayout(self.grupo_tabla)

    self.tabla = QTableView()
    self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
    self.tabla.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
    self.tabla.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
    self.tabla.setAlternatingRowColors(True)
    self.tabla.setMinimumHeight(190)
    # Filas de alto fijo y muestreo reducido para ajustar columnas:
    # evita calcular el tamaño de decenas de miles de filas.
    self.tabla.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
    self.tabla.verticalHeader().setDefaultSectionSize(26)
    self.tabla.horizontalHeader().setResizeContentsPrecision(200)
    layout_tabla.addWidget(self.tabla)

    layout_principal.addWidget(self.grupo_tabla, stretch=1)

    # --- 2. Selección de Variables ---
    self.grupo_variables = QGroupBox("2. Seleccionar columnas")
    self.grupo_variables.setEnabled(False)
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

    # --- 3. Separación de Datos (Train / Test) ---
    self.grupo_split = QGroupBox("3. Separar datos (Train / Test)")
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

    # --- 4. Preprocesamiento de Valores Inexistentes ---
    self.grupo_preproc = QGroupBox("4. Preprocesar valores inexistentes")
    self.grupo_preproc.setEnabled(False)
    layout_preproc = QVBoxLayout(self.grupo_preproc)

    self.lbl_info_nulos = QLabel("Realice la separación de datos para detectar valores inexistentes.")
    self.lbl_info_nulos.setWordWrap(True)
    layout_preproc.addWidget(self.lbl_info_nulos)

    layout_estrategias = QVBoxLayout()
    self.rb_drop = QRadioButton("Eliminar las filas que contengan valores inexistentes")
    self.rb_mean = QRadioButton("Rellenar con la media de cada columna (Train)")
    self.rb_median = QRadioButton("Rellenar con la mediana de cada columna (Train)")
    self.rb_constant = QRadioButton("Rellenar con un valor constante:")

    self.rb_mean.setChecked(True)

    layout_estrategias.addWidget(self.rb_drop)
    layout_estrategias.addWidget(self.rb_mean)
    layout_estrategias.addWidget(self.rb_median)

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

    # --- 5. Creación y Evaluación del Modelo ---
    self.grupo_modelo = QGroupBox("5. Crear modelo")
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

    # Área de texto para Descripción del modelo
    layout_modelo.addWidget(QLabel("<b>Descripción (opcional):</b>"))
    self.txt_descripcion = QTextEdit()
    self.txt_descripcion.setPlaceholderText("Escriba aquí una descripción o propósito de este modelo...")
    self.txt_descripcion.setMaximumHeight(80)
    self.txt_descripcion.setEnabled(False)
    self.txt_descripcion.textChanged.connect(self.actualizar_descripcion_modelo)
    layout_modelo.addWidget(self.txt_descripcion)

    # Métricas de error (Tabla compacta)
    layout_modelo.addWidget(QLabel("Métricas de Error:"))
    self.tabla_metricas = QTableWidget(2, 2)
    self.tabla_metricas.setHorizontalHeaderLabels(["Entrenamiento (Train)", "Test"])
    self.tabla_metricas.setVerticalHeaderLabels(["R² (Coeff)", "MSE (Error)"])
    self.tabla_metricas.setMaximumHeight(95)
    self.tabla_metricas.horizontalHeader().setStretchLastSection(True)
    layout_modelo.addWidget(self.tabla_metricas)

    self.btn_guardar = QPushButton("Guardar modelo")
    self.btn_guardar.setMinimumHeight(36)
    self.btn_guardar.setMaximumWidth(260)
    self.btn_guardar.setEnabled(False)
    self.btn_guardar.clicked.connect(self.guardar_modelo_disco)
    layout_modelo.addWidget(self.btn_guardar, alignment=Qt.AlignLeft)

    # Gráfico de ajuste embebido con Matplotlib
    self.fig, self.ax = plt.subplots(figsize=(6, 3.5))
    self.canvas = FigureCanvas(self.fig)
    self.canvas.setMinimumHeight(260)
    layout_modelo.addWidget(self.canvas)

    layout_principal.addWidget(self.grupo_modelo)

    self._inicializar_panel_prediccion()
    layout_principal.addWidget(self.grupo_prediccion)

    # --- Barra de estado ---
    self.lbl_estado = QLabel()
    self.statusBar().addWidget(self.lbl_estado, 1)
    self.progreso = QProgressBar()
    self.progreso.setRange(0, 0)  # indeterminada
    self.progreso.setTextVisible(False)
    self.progreso.setMaximumWidth(160)
    self.progreso.setVisible(False)
    self.statusBar().addPermanentWidget(self.progreso)
    self._actualizar_barra_estado()

    # Widgets que se bloquean mientras dura una operación larga
    self._widgets_bloqueables = [
        self.btn_cargar,
        self.btn_cargar_modelo,
        self.grupo_variables,
        self.grupo_split,
        self.grupo_preproc,
        self.grupo_modelo,
        self.grupo_prediccion,
    ]

  # ------------------------------------------------------------------
  # Mensajes al usuario (siempre mediante ventanas emergentes)
  # ------------------------------------------------------------------
  def _exito(self, titulo: str, texto: str):
    QMessageBox.information(self, titulo, texto)

  def _aviso(self, titulo: str, texto: str):
    QMessageBox.warning(self, titulo, texto)

  def _error(self, titulo: str, texto: str):
    QMessageBox.critical(self, titulo, texto)

  # ------------------------------------------------------------------
  # Estado de la aplicación
  # ------------------------------------------------------------------
  def _actualizar_barra_estado(self):
    if self.datos is not None:
      n_filas = f"{len(self.datos):,}".replace(",", ".")
      dataset = f"{self.nombre_dataset} ({n_filas} filas)"
    else:
      dataset = "ninguno"

    if self.modelo_info is not None:
      modelo = self.modelo_origen or "creado"
    else:
      modelo = "ninguno"

    if self.modelo_info is not None and self.cambios_sin_guardar:
      cambios = "Modelo con cambios sin guardar"
    else:
      cambios = "Sin cambios pendientes"

    self.lbl_estado.setText(
        f"Dataset: {dataset}  |  Modelo: {modelo}  |  {cambios}"
    )

  def _descartar_modelo(self):
    """Descarta el modelo actual y limpia los controles visuales asociados."""
    self.modelo_info = None
    self.modelo_origen = None
    self.cambios_sin_guardar = False
    self._actualizar_boton_guardar()

    self.txt_descripcion.blockSignals(True)
    self.txt_descripcion.clear()
    self.txt_descripcion.blockSignals(False)
    self.txt_descripcion.setEnabled(False)

    self.lbl_formula.setText("<b>Fórmula:</b> -")
    self.tabla_metricas.clearContents()

    self.ax.clear()
    self.ax.grid(True, linestyle=":", alpha=0.7)
    self.fig.tight_layout()
    self.canvas.draw()

    self.configurar_campos_prediccion([])
    self.grupo_prediccion.setEnabled(False)

    self._actualizar_barra_estado()

  def _bloquear_interfaz(self, bloquear: bool):
    """Deshabilita (o restaura) los controles que iniciarían otra operación."""
    if bloquear:
      self._estados_previos = {w: w.isEnabled() for w in self._widgets_bloqueables}
      for w in self._widgets_bloqueables:
        w.setEnabled(False)
      self.progreso.setVisible(True)
    else:
      for w, estado in self._estados_previos.items():
        w.setEnabled(estado)
      self._estados_previos = {}
      self.progreso.setVisible(False)
      self._actualizar_barra_estado()

  # ------------------------------------------------------------------
  # Carga de dataset (en segundo plano)
  # ------------------------------------------------------------------
  def seleccionar_archivo(self):
    if self.modelo_info is not None:
      resp = QMessageBox.question(
          self,
          "Descartar modelo",
          "Tiene un modelo cargado o creado. Si carga un nuevo dataset se descartará. ¿Desea continuar?",
          QMessageBox.Yes | QMessageBox.Cancel,
          QMessageBox.Cancel
      )
      if resp != QMessageBox.Yes:
        return

    archivo, _ = QFileDialog.getOpenFileName(
        self, "Seleccionar dataset", "", FILTRO_ARCHIVOS
    )
    if not archivo:
      return
    self.cargar_archivo(Path(archivo))

  def cargar_archivo(self, ruta: Path):
    ruta = ruta.resolve()

    # Por seguridad: si quedara un hilo anterior terminando, esperarlo.
    if self._hilo is not None and self._hilo.isRunning():
      self._hilo.wait()

    self._ruta_en_carga = ruta
    self._bloquear_interfaz(True)
    self.lbl_estado.setText(f"Cargando «{ruta.name}»... Espere, por favor.")

    self._hilo = QThread(self)
    self._trabajador = TrabajadorCarga(ruta)
    self._trabajador.moveToThread(self._hilo)

    self._hilo.started.connect(self._trabajador.ejecutar)
    self._trabajador.terminado.connect(self._carga_terminada)
    self._trabajador.fallido.connect(self._carga_fallida)
    self._trabajador.terminado.connect(self._hilo.quit)
    self._trabajador.fallido.connect(self._hilo.quit)
    self._hilo.start()

  def _carga_terminada(self, datos):
    self._bloquear_interfaz(False)
    self._aplicar_dataset(datos, self._ruta_en_carga)

  def _carga_fallida(self, mensaje: str):
    self._bloquear_interfaz(False)
    self._error(
        "No se pudo cargar el archivo",
        f"{mensaje}\n\nCompruebe que el archivo no está dañado ni abierto en "
        "otro programa y que su formato es compatible (CSV, Excel o SQLite). "
        "Si el problema continúa, pruebe con otro archivo."
    )

  def _aplicar_dataset(self, datos: pd.DataFrame, ruta: Path):
    self.datos = datos
    self.ruta_actual = ruta
    self.nombre_dataset = ruta.name

    self.lbl_ruta.setText(str(ruta))
    self.lbl_ruta.setStyleSheet("color: #243247;")

    # Volver a mostrar secciones de datos
    self.grupo_tabla.setVisible(True)
    self.grupo_variables.setEnabled(True)

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

    self.lbl_info_nulos.setText(
        "Realice la separación de datos para detectar valores inexistentes."
    )

    self._descartar_modelo()  # Se descarta cualquier modelo anterior

    self.grupo_split.setEnabled(False)
    self.grupo_preproc.setEnabled(False)
    self.grupo_modelo.setEnabled(False)
    self.grupo_prediccion.setEnabled(False)

  def closeEvent(self, event):
    if self._hilo is not None and self._hilo.isRunning():
      self._hilo.quit()
      self._hilo.wait()
    super().closeEvent(event)

  # ------------------------------------------------------------------
  # Carga de modelo
  # ------------------------------------------------------------------
  def dialogo_cargar_modelo(self):
    if self.modelo_info is not None or self.datos is not None:
      resp = QMessageBox.question(
          self,
          "Sustituir estado actual",
          "¿Desea cargar un modelo guardado? Se perderá el estado actual de trabajo.",
          QMessageBox.Yes | QMessageBox.Cancel,
          QMessageBox.Cancel
      )
      if resp != QMessageBox.Yes:
        return

    archivo, _ = QFileDialog.getOpenFileName(
        self, "Cargar modelo", "", f"Modelo (*{EXTENSION})"
    )
    if not archivo:
      return

    self.cargar_modelo_desde_archivo(Path(archivo))

  def cargar_modelo_desde_archivo(self, ruta: Path):
    ruta = ruta.resolve()
    try:
      modelo_info = cargar_modelo(ruta)
    except Exception:
      logger.exception("Error al cargar el modelo %s", ruta)
      self._error(
          "No se pudo cargar el modelo",
          "El archivo está dañado, no tiene el formato esperado o le falta "
          "parte de la información. Seleccione otro archivo de modelo."
      )
      return

    # Actualizar estado interno
    self.modelo_info = modelo_info
    self.modelo_origen = "cargado"
    self.cambios_sin_guardar = False
    self.ruta_actual = ruta
    self.datos = None
    self.nombre_dataset = None
    self.train_df = None
    self.test_df = None
    self.train_processed = None
    self.test_processed = None

    self.lbl_ruta.setText(f"Modelo cargado: {ruta}")
    self.lbl_ruta.setStyleSheet("color: #243247;")

    # Ocultar secciones relacionadas con datos
    self.grupo_tabla.setVisible(False)
    self.grupo_variables.setEnabled(False)
    self.grupo_split.setEnabled(False)
    self.grupo_preproc.setEnabled(False)

    # Mostrar información del modelo
    self.lbl_formula.setText(f"<b>Fórmula:</b> {modelo_info.formula}")

    self.txt_descripcion.blockSignals(True)
    self.txt_descripcion.setText(modelo_info.descripcion or "")
    self.txt_descripcion.blockSignals(False)
    self.txt_descripcion.setEnabled(True)

    metricas = modelo_info.metricas
    self.tabla_metricas.setItem(0, 0, QTableWidgetItem(f"{metricas.get('r2_train', 0):.4f}"))
    self.tabla_metricas.setItem(1, 0, QTableWidgetItem(f"{metricas.get('mse_train', 0):.4f}"))
    self.tabla_metricas.setItem(0, 1, QTableWidgetItem(f"{metricas.get('r2_test', 0):.4f}"))
    self.tabla_metricas.setItem(1, 1, QTableWidgetItem(f"{metricas.get('mse_test', 0):.4f}"))

    self.grupo_modelo.setEnabled(True)
    self.btn_guardar.setEnabled(True)

    # Configurar panel de predicción con las variables del modelo
    columnas_entrada = getattr(modelo_info, "features", [])
    if not columnas_entrada and "columnas_entrada" in modelo_info:
        columnas_entrada = modelo_info["columnas_entrada"]
    self.configurar_campos_prediccion(columnas_entrada)

    self._actualizar_barra_estado()
    self._exito("Modelo cargado", "El modelo se ha cargado correctamente.")

  # ------------------------------------------------------------------
  # Pasos del pipeline
  # ------------------------------------------------------------------
  def confirmar_variables(self):
    if self.datos is None:
      self._aviso(
          "Falta el dataset",
          "Primero cargue un dataset (paso 1) y después seleccione las columnas."
      )
      return

    features = [item.text() for item in self.list_features.selectedItems()]
    target = self.combo_target.currentData()

    valido, mensaje = validar_seleccion_columnas(self.datos, features, target)

    if not valido:
      self._error("Error de selección", mensaje)
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
      self._descartar_modelo()

      self.grupo_split.setEnabled(True)
      self.grupo_preproc.setEnabled(False)
      self.grupo_modelo.setEnabled(False)

      self._exito(
          "Selección confirmada",
          f"<b>Variables confirmadas correctamente.</b><br><br>"
          f"<b>Entradas:</b> {', '.join(features)}<br>"
          f"<b>Salida:</b> {target}",
      )

  def ejecutar_separacion(self):
    if self.datos is None:
      self._aviso(
          "Falta el dataset",
          "No hay ningún dataset cargado. Cárguelo en el paso 1 antes de separar los datos."
      )
      return

    try:
      test_pct = float(self.input_test_pct.text())
    except ValueError:
      self._error(
          "Porcentaje de test no válido",
          "El porcentaje de test debe ser un número (por ejemplo 20). "
          "Corríjalo e inténtelo de nuevo."
      )
      return

    try:
      seed = int(self.input_seed.text())
    except ValueError:
      self._error(
          "Semilla no válida",
          "La semilla debe ser un número entero (por ejemplo 42). "
          "Corríjala e inténtelo de nuevo."
      )
      return

    train_df, test_df, mensaje = realizar_separacion_datos(
        self.datos, test_size_pct=test_pct, random_state=seed
    )

    if train_df is None or test_df is None:
      self._error("Error en la separación", mensaje)
      return

    self.train_df = train_df
    self.test_df = test_df
    self.train_processed = None
    self.test_processed = None
    self._descartar_modelo()
    self.grupo_modelo.setEnabled(False)

    columnas_modelo = self.features_seleccionadas + [self.target_seleccionado]
    resultado_nulos = detectar_nulos(self.train_df, self.test_df, columnas_modelo)
    train_m = resultado_nulos["train"]
    test_m = resultado_nulos["test"]

    total_train_nulos = sum(train_m.values())
    total_test_nulos = sum(test_m.values())

    info_texto = (
        f"<b>{mensaje}</b><br>"
        f"Entrenamiento: {len(self.train_df)} filas | Test: {len(self.test_df)} filas<br><br>"
        f"<b>Valores inexistentes detectados:</b><br>"
    )
    for col in columnas_modelo:
      info_texto += f"- <b>{col}</b> -> Train: {train_m[col]} | Test: {test_m[col]}<br>"

    if total_train_nulos == 0 and total_test_nulos == 0:
      info_texto += "<br><i>No hay valores inexistentes. Puede continuar sin preprocesar o aplicar una estrategia.</i>"
      self.train_processed = self.train_df
      self.test_processed = self.test_df
      self.grupo_modelo.setEnabled(True)

    self.lbl_info_nulos.setText(info_texto)
    self.grupo_preproc.setEnabled(True)

    self._exito("Separación y detección exitosa", info_texto)

  def aplicar_preprocesamiento(self):
    if self.train_df is None or self.test_df is None:
      self._aviso(
          "Faltan datos separados",
          "Debe separar los datos (paso 3) antes de preprocesar."
      )
      return

    columnas_modelo = self.features_seleccionadas + [self.target_seleccionado]

    try:
      if self.rb_drop.isChecked():
        train_res, test_res = preprocesar_eliminar_filas(self.train_df, self.test_df, columnas_modelo)

        if train_res.empty or test_res.empty:
          self._aviso(
              "Aviso de preprocesamiento",
              "La eliminación de filas dejaría vacío el conjunto de entrenamiento o el de test. "
              "No se aplicó el cambio. Pruebe con otra estrategia, por ejemplo rellenar con la media."
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
          self._error(
              "Valor constante no válido",
              "El valor constante debe ser un número (por ejemplo 0 o 3.5). "
              "Corríjalo e inténtelo de nuevo."
          )
          return

        train_res, test_res = preprocesar_constante(self.train_df, self.test_df, columnas_modelo, const_val)
        msg_exito = f"<b>Preprocesamiento aplicado con éxito:</b><br>Valores rellenados con el valor constante: <b>{const_val}</b>"
      else:
        return

    except Exception:
      logger.exception("Error durante el preprocesamiento")
      self._error(
          "Error de preprocesamiento",
          "No se pudo aplicar el preprocesado. Compruebe que las columnas "
          "seleccionadas son numéricas o pruebe con otra estrategia."
      )
      return

    self.train_processed = train_res
    self.test_processed = test_res
    self._descartar_modelo()

    self._exito("Preprocesamiento exitoso", msg_exito)

    nulos_restantes_train = train_res[columnas_modelo].isna().sum().sum()
    nulos_restantes_test = test_res[columnas_modelo].isna().sum().sum()

    if nulos_restantes_train == 0 and nulos_restantes_test == 0:
      self.grupo_modelo.setEnabled(True)
    else:
      self.grupo_modelo.setEnabled(False)

  def actualizar_descripcion_modelo(self):
    """Sincroniza el contenido del área de texto con la estructura de datos del modelo."""
    if self.modelo_info is not None:
      self.modelo_info.descripcion = self.txt_descripcion.toPlainText()
      self.cambios_sin_guardar = True
      self._actualizar_barra_estado()

  def _actualizar_boton_guardar(self):
      self.btn_guardar.setEnabled(self.modelo_info is not None)

  def guardar_modelo_disco(self):
    if self.modelo_info is None:
      return

    if not self.modelo_info.descripcion.strip():
      r = QMessageBox.question(
          self, "Descripción vacía",
          "El modelo no tiene descripción. ¿Guardar igualmente?",
          QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Yes)
      if r != QMessageBox.Yes:
        return

    # Si se cargó desde un archivo, propone por defecto su carpeta y nombre
    sugerencia = (
        str(self.ruta_actual)
        if (self.ruta_actual is not None and self.datos is None)
        else ("modelo" + EXTENSION)
    )

    ruta, _ = QFileDialog.getSaveFileName(
        self, "Guardar modelo", sugerencia,
        f"Modelo (*{EXTENSION})")
    if not ruta:
      return

    ruta_final = asegurar_extension(ruta)
    if ruta_final != Path(ruta) and ruta_final.exists():
      r = QMessageBox.question(
          self, "Sobrescribir",
          f"«{ruta_final.name}» ya existe. ¿Desea sobrescribirlo?")
      if r != QMessageBox.Yes:
        return

    try:
      guardada = guardar_modelo(self.modelo_info, ruta_final)
      self.ruta_actual = guardada
    except PermissionError:
      self._error(
          "No se pudo guardar",
          "No tiene permisos para escribir en esa carpeta. "
          "Elija otra carpeta e inténtelo de nuevo.")
      return
    except OSError:
      self._error(
          "No se pudo guardar",
          "No se pudo escribir el archivo. Compruebe que la carpeta existe "
          "y que hay espacio en disco, o elija otra ubicación.")
      return
    except Exception:
      logger.exception("Error inesperado al guardar el modelo")
      self._error(
          "No se pudo guardar",
          "Ocurrió un error inesperado al guardar el modelo. "
          "Inténtelo de nuevo o elija otra ubicación.")
      return

    self.cambios_sin_guardar = False
    self._actualizar_barra_estado()
    self._exito("Modelo guardado", f"Modelo guardado en:\n{guardada}")

  def crear_modelo(self):
    if self.train_processed is None or self.test_processed is None:
      self._aviso(
          "Datos no preparados",
          "Los datos procesados no están listos. Complete antes los pasos 3 y 4."
      )
      return

    try:
      modelo_info, (y_train, y_pred_train, y_test, y_pred_test) = (
          entrenar_modelo_lineal(
              self.train_processed,
              self.test_processed,
              self.features_seleccionadas,
              self.target_seleccionado,
          )
      )
      self.modelo_info = modelo_info
      self.modelo_origen = "creado"
      self.cambios_sin_guardar = True
      self.ruta_actual = None

      self.txt_descripcion.blockSignals(True)
      self.txt_descripcion.setText(self.modelo_info.descripcion)
      self.txt_descripcion.blockSignals(False)
      self.txt_descripcion.setEnabled(True)
      self._actualizar_boton_guardar()
      self._actualizar_barra_estado()

      self.lbl_formula.setText(f"<b>Fórmula:</b> {modelo_info.formula}")

      metricas = modelo_info.metricas
      self.tabla_metricas.setItem(0, 0, QTableWidgetItem(f"{metricas['r2_train']:.4f}"))
      self.tabla_metricas.setItem(1, 0, QTableWidgetItem(f"{metricas['mse_train']:.4f}"))
      self.tabla_metricas.setItem(0, 1, QTableWidgetItem(f"{metricas['r2_test']:.4f}"))
      self.tabla_metricas.setItem(1, 1, QTableWidgetItem(f"{metricas['mse_test']:.4f}"))

      self.ax.clear()
      if len(self.features_seleccionadas) == 1:
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
        y_line = modelo_info.modelo.predict(X_line)
        self.ax.plot(X_line, y_line, color="#dc2626", linewidth=2, label="Ajuste")
        self.ax.set_xlabel(feat)
        self.ax.set_ylabel(self.target_seleccionado)
      else:
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

      # Configurar panel de predicción
      self.configurar_campos_prediccion(self.features_seleccionadas)

      self._exito(
          "Modelo creado", "Modelo de regresión lineal creado y evaluado correctamente."
      )

    except Exception:
      logger.exception("Error al crear el modelo")
      self._error(
          "No se pudo crear el modelo",
          "Ocurrió un error durante el entrenamiento. Compruebe que las columnas "
          "seleccionadas son numéricas y que hay datos suficientes en entrenamiento "
          "y test. Si el problema continúa, repita los pasos desde la selección de columnas."
      )

  # ------------------------------------------------------------------
  # Predicción
  # ------------------------------------------------------------------
  def _inicializar_panel_prediccion(self):
      self.grupo_prediccion = QGroupBox("6. Realizar predicción")
      self.grupo_prediccion.setEnabled(False)

      layout_principal_pred = QVBoxLayout(self.grupo_prediccion)
      self.form_prediccion = QFormLayout()
      layout_principal_pred.addLayout(self.form_prediccion)

      self.btn_predecir = QPushButton("Realizar predicción")
      self.btn_predecir.clicked.connect(self._on_click_realizar_prediccion)
      layout_principal_pred.addWidget(self.btn_predecir)

      self.lbl_resultado_prediccion = QLabel("")
      layout_principal_pred.addWidget(self.lbl_resultado_prediccion)

      self.inputs_prediccion: dict[str, QLineEdit] = {}

  def configurar_campos_prediccion(self, columnas_entrada: list[str]):
      while self.form_prediccion.rowCount() > 0:
          self.form_prediccion.removeRow(0)
      self.inputs_prediccion.clear()
      self.lbl_resultado_prediccion.setText("")

      for col in columnas_entrada:
          campo = QLineEdit()
          campo.setPlaceholderText(f"Valor para {col}")
          self.form_prediccion.addRow(f"{col}:", campo)
          self.inputs_prediccion[col] = campo

      self.grupo_prediccion.setEnabled(True)

  def _on_click_realizar_prediccion(self):
      if not hasattr(self, "modelo_info") or not self.modelo_info:
          return

      from winamax.prediccion import calcular_prediccion

      valores_validos = {}
      faltantes = []
      invalidos = []

      for col, campo in self.inputs_prediccion.items():
          texto = campo.text().strip()
          if not texto:
              faltantes.append(col)
              continue

          texto_norm = texto.replace(",", ".")
          try:
              valores_validos[col] = float(texto_norm)
          except ValueError:
              invalidos.append(col)

      if faltantes or invalidos:
          mensajes = []
          if faltantes:
              mensajes.append(f"Faltan valores en: {', '.join(faltantes)}")
          if invalidos:
              mensajes.append(f"Valores no numéricos en: {', '.join(invalidos)}")
          mensajes.append("Corríjalos e inténtelo de nuevo.")
          self._aviso("Error de validación", "\n".join(mensajes))
          return

      try:
          resultado = calcular_prediccion(self.modelo_info, valores_validos)
          col_salida = getattr(self.modelo_info, "target", None) or self.target_seleccionado or "Salida"
          decimales = getattr(self.modelo_info, "decimales", 4)
          if not isinstance(decimales, int):
              decimales = 4

          self.lbl_resultado_prediccion.setText(
              f"{col_salida} = {resultado:.{decimales}f}"
          )
          self.lbl_resultado_prediccion.setVisible(True)
          self.lbl_resultado_prediccion.show()

      except Exception:
          logger.exception("Error al calcular la predicción")
          self._error(
              "No se pudo calcular la predicción",
              "Ocurrió un error al calcular la predicción. Compruebe los valores "
              "introducidos e inténtelo de nuevo."
          )


def main():
  logging.basicConfig(level=logging.INFO)
  app = QApplication(sys.argv)
  ventana = VentanaPrincipal()
  ventana.show()
  sys.exit(app.exec())


if __name__ == "__main__":
  main()