from fractions import Fraction
from matplotlib import cm
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from plasTeX.TeX import TeX
from plasTeX.Renderers.HTML5 import Renderer
from PyQt5.QtCore import QCoreApplication, QMetaObject, QSize, Qt, QUrl, pyqtSignal, QTimer, QPropertyAnimation, QThreadPool
from PyQt5.QtGui import QFont, QPixmap, QIcon, QMovie
from PyQt5.QtWidgets import *
from sympy import integrate, latex, parsing, pi, preview, symbols, core
from sympy.abc import lamda, x, t, n, j
import atexit, os, shutil, matplotlib.widgets, mpl_toolkits.axes_grid1
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipy as sc
import sympy as sp

# Determina el directorio actual
directorio_base = os.path.dirname(__file__)

class Ui_VentanaCarga(QMainWindow):
    """Clase que contiene el diseño de la ventana de carga."""
    # El diseño y control de la ventana de carga se basan en Informative Blocks. (2023). Modern Splash Screen | Mini Series | PySide2 | Python. YouTube. https://www.youtube.com/playlist?list=PLT0hD2cyULPiVBXlFOwz2EJff_3oJtj8T

    def setupUi(self, ventana):
        """
         Diseño y configuración de la ventana de carga.
        
        Parámetros
        ----------
        **ventana** : QMainWindow
            Ventana de la pantalla de carga.
        """

        # El icono de la ventana.
        # Asigna la imagen a un ícono. Esto se basa en Andy M. (15 de diciembre de 2009). Respuesta a la pregunta "Python QPushButton setIcon: put icon on button". stackoverflow. https://stackoverflow.com/a/1905587
        # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 2.5 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/2.5/
        icono = QIcon()
        icono.addPixmap(QPixmap(os.path.join(directorio_base, "Iconos", "Icono.png")), QIcon.Normal, QIcon.Off)

        # Configuración de la ventana.
        ventana.resize(400, 270)
        ventana.setWindowTitle("GraPhEr - Ecuaciones Diferenciales Parciales Separables")
        ventana.setWindowIcon(icono)
        centralwidget = QWidget()
        centralwidget.setStyleSheet(u"QWidget{background-color: rgb(11, 61, 98); border-radius: 1in;} ")
        ventana.setCentralWidget(centralwidget)

        verticalLayout_1 = QVBoxLayout(centralwidget)
        verticalLayout_1.setContentsMargins(0, 30, 0, 0)

        frame = QFrame(centralwidget)
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)

        verticalLayout_2 = QVBoxLayout(frame)
        verticalLayout_2.setContentsMargins(10, 5, 30, 5)
        verticalLayout_2.setSpacing(10)
        verticalLayout_2.setStretch(0, 150)
        verticalLayout_2.setStretch(1, 100)

        # Diseño de la animación de carga.
        self.icono = QLabel()
        self.icono.setMaximumSize(QSize(400,150))
        self.icono.setMinimumSize(QSize(400,150))
        self.icono.setStyleSheet("background-color: rgb(11 , 61, 98)")
        self.icono.setAlignment(Qt.AlignCenter)

        # La configuración y el funcionamiento del gif de carga fue tomado de S. Nick. (13 de agosto de 2020). Respuesta a la pregunta "How to display a loading animated gif while a code is executing in backend of my Python Qt5 UI?". stackoverflow. https://stackoverflow.com/a/63395218
        # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 4.0 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/4.0/
        self.animacion = QMovie(os.path.join(directorio_base, "Carga", "LogoCargando.gif"))
        self.animacion.setScaledSize(QSize(227,150))
        self.icono.setMovie(self.animacion)

        verticalLayout_2.addWidget(self.icono, alignment=Qt.AlignHCenter)

        # Diseño de la etiqueta para mostrar mensajes en la pantalla de carga.
        self.label = QLabel()
        self.label.setText("Iniciando Proceso")
        self.label.setStyleSheet(u"color: rgb(234, 237, 239)")
        self.label.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        verticalLayout_2.addWidget(self.label)
        verticalLayout_1.addWidget(frame)

        QMetaObject.connectSlotsByName(ventana)
