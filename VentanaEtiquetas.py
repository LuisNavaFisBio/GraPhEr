from PantallaGrafica import Lienzo

from fractions import Fraction
from matplotlib import cm
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from plasTeX.TeX import TeX
from plasTeX.Renderers.HTML5 import Renderer
from PyQt5.QtCore import QCoreApplication, QMetaObject, QSize, Qt, QUrl, pyqtSignal,QTimer, QPropertyAnimation
from PyQt5.QtGui import QFont, QPixmap, QIcon, QMovie
from PyQt5.QtWidgets import *
from PyQt5 import QtWebEngineWidgets
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

class Ui_VentanaEtiquetas(QMainWindow):
    """Clase que contiene el diseño de la ventana para la leyenda de las curvas de nivel."""

    def setupUi(self, ventana):
        """
         Diseño y configuración de la ventana de leyenda para las curvas de nivel.
        
        Parámetros
        ----------
        **ventana** : QMainWindow
            Ventana de la pantalla de leyenda..
        """

        # El icono de la ventana.
        # Asigna la imagen a un ícono. Esto se basa en Andy M. (15 de diciembre de 2009). Respuesta a la pregunta "Python QPushButton setIcon: put icon on button". stackoverflow. https://stackoverflow.com/a/1905587
        # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 2.5 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/2.5/
        icono = QIcon()
        icono.addPixmap(QPixmap(os.path.join(directorio_base, "Iconos", "Icono.png")), QIcon.Normal, QIcon.Off)

        # Configuración de la ventana.
        ventana.resize(780, 250)
        ventana.setStyleSheet(u"background-color: rgb(246, 247, 247); border-radius: 10px")
        ventana.setWindowTitle("GraPhEr - Leyenda de Curvas de Nivel")
        ventana.setMinimumSize(QSize(780,200))
        ventana.setWindowIcon(icono)
        self.centralwidget = QWidget(ventana)
        ventana.setCentralWidget(self.centralwidget)

        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout.setStretch(0, 180)
        
        # Diseño del lienzo en donde se mostrará la leyenda de las curvas de nivel.
        self.MostrarEtiqueta = Lienzo(self)
        self.MostrarEtiqueta.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.MostrarEtiqueta.setVisible(True)
        self.verticalLayout.addWidget(self.MostrarEtiqueta)

        QMetaObject.connectSlotsByName(ventana)