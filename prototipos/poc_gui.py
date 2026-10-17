import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class VentanaPrincipal(QMainWindow):

  def __init__(self):
    super().__init__()

    # 1. Ventana con título y tamaño inicial
    self.setWindowTitle("Prueba de Concepto - PySide6")
    self.resize(650, 550)

    # Widget central y layout principal
    widget_central = QWidget()
    self.setCentralWidget(widget_central)
    layout_principal = QVBoxLayout(widget_central)

    # --- SECCIÓN 1: Selección de archivo ---
    grupo_archivo = QGroupBox("1. Selección de Archivos")
    layout_archivo = QHBoxLayout()

    self.btn_explorar = QPushButton("Seleccionar Archivo")
    self.btn_explorar.clicked.connect(self.seleccionar_archivo)
    layout_archivo.addWidget(self.btn_explorar)

    self.lbl_ruta = QLabel("Ningún archivo seleccionado")
    self.lbl_ruta.setStyleSheet("color: gray;")
    layout_archivo.addWidget(self.lbl_ruta, stretch=1)

    grupo_archivo.setLayout(layout_archivo)
    layout_principal.addWidget(grupo_archivo)

    # --- SECCIÓN 2: Tabla con scroll ---
    grupo_tabla = QGroupBox("2. Tabla de Datos (Ejemplo)")
    layout_tabla = QVBoxLayout()

    self.tabla = QTableWidget()
    self.tabla.setColumnCount(3)
    self.tabla.setHorizontalHeaderLabels(["ID", "Nombre de Muestra", "Valor IA"])

    # Ajustar ancho de columnas al contenido
    header = self.tabla.horizontalHeader()
    header.setSectionResizeMode(1, QHeaderView.Stretch)

    # Insertar datos de ejemplo
    datos_ejemplo = [
        ("1", "Dataset_Entrenamiento_v1.csv", "0.95"),
        ("2", "Dataset_Prueba_v1.csv", "0.88"),
        ("3", "Matriz_Confucion.json", "0.92"),
        ("4", "Modelo_Pesos.h5", "0.97"),
        ("5", "Parametros_Optimos.yaml", "0.89"),
    ]

    self.tabla.setRowCount(len(datos_ejemplo))
    for fila_idx, fila_data in enumerate(datos_ejemplo):
      for col_idx, valor in enumerate(fila_data):
        item = QTableWidgetItem(valor)
        if col_idx in [0, 2]:
          item.setTextAlignment(Qt.AlignCenter)
        self.tabla.setItem(fila_idx, col_idx, item)

    layout_tabla.addWidget(self.tabla)
    grupo_tabla.setLayout(layout_tabla)
    layout_principal.addWidget(grupo_tabla)

    # --- SECCIÓN 3: Desplegable y cuadro de texto ---
    grupo_controles = QGroupBox("3. Entradas y Controles")
    layout_controles = QHBoxLayout()

    # Layout vertical para las entradas
    layout_entradas = QVBoxLayout()

    # Desplegable (QComboBox)
    layout_combo = QHBoxLayout()
    layout_combo.addWidget(QLabel("Modelo:"))
    self.combo_modelos = QComboBox()
    self.combo_modelos.addItems(
        ["Regresión Lineal", "Red Neuronal", "SVM", "Random Forest"]
    )
    layout_combo.addWidget(self.combo_modelos)
    layout_entradas.addLayout(layout_combo)

    # Cuadro de texto (QLineEdit)
    layout_texto = QHBoxLayout()
    layout_texto.addWidget(QLabel("Parámetro/Texto:"))
    self.txt_entrada = QLineEdit()
    self.txt_entrada.setPlaceholderText("Ej: 0.01 (learning rate)")
    layout_texto.addWidget(self.txt_entrada)
    layout_entradas.addLayout(layout_texto)

    layout_controles.addLayout(layout_entradas)

    # --- SECCIÓN 4: Botón de acción con mensaje ---
    self.btn_procesar = QPushButton("Procesar Datos")
    self.btn_procesar.setFixedHeight(50)
    self.btn_procesar.clicked.connect(self.mostrar_mensaje)
    layout_controles.addWidget(self.btn_procesar)

    grupo_controles.setLayout(layout_controles)
    layout_principal.addWidget(grupo_controles)

  def seleccionar_archivo(self):
    archivo, _ = QFileDialog.getOpenFileName(
        self,
        "Seleccionar archivo de datos",
        "",
        "Archivos de datos (*.csv *.json *.txt);;Todos los archivos (*)",
    )
    if archivo:
      self.lbl_ruta.setText(archivo)
      self.lbl_ruta.setStyleSheet("color: black;")

  def mostrar_mensaje(self):
    modelo = self.combo_modelos.currentText()
    texto = self.txt_entrada.text() or "No especificado"
    archivo = self.lbl_ruta.text()

    mensaje = (
        f"<b>Modelo seleccionado:</b> {modelo}<br>"
        f"<b>Texto introducido:</b> {texto}<br>"
        f"<b>Archivo cargado:</b> {archivo}"
    )

    msg_box = QMessageBox(self)
    msg_box.setWindowTitle("Resultado de la Prueba de Concepto")
    msg_box.setText(mensaje)
    msg_box.setIcon(QMessageBox.Information)
    msg_box.exec()


if __name__ == "__main__":
  app = QApplication(sys.argv)
  ventana = VentanaPrincipal()
  ventana.show()
  sys.exit(app.exec())