#    GraPhEr - Ecuaciones Diferenciales Parciales Separables. Un programa para la graficación de la solución aproximada a ecuaciones diferenciales parciales que admiten
#    soluciones en variables separadas.
   
#    Copyright (C) 2024  Luis Enrique Nava Garcia

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

#    Contact Email: navaluisfisbio@ciencias.unam.mx

################################################################################################
## Interfaz gráfica para la visualización gráfica de la solución de problemas a través del método de variables separables.
#
## Creada por: Luis Enrique Nava Garcia, estudiante de la Licenciatura en Física Biomédica. Correo de contacto navaluisfisbio@ciencias.unam.mx
#
## Diseño de la interfaz creado en Qt User Interface Compiler (versión 5.14.1) por Luis Enrique Nava Garcia.
#
## Fecha: Octubre 2024
#
## -*- coding: utf-8 -*-
#
## Se necesitan los archivos PantallaInicialInterfaz.py, PantallaEntradaInterpretada.py, PantallGrafica.py, Trabajo_Clases.py, Animaciones.py, 
## Errores.py, VentanaCarga.py y VentanaEtiquetas.py, así como las carpetas Iconos y Carga para la ejecución de la interfaz gráfica.
################################################################################################

from math import log10
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.collections import LineCollection
from plasTeX.TeX import TeX
from plasTeX.Renderers.HTML5 import Renderer
from PyQt5.QtCore import QCoreApplication, QMetaObject, QSize, Qt, QUrl, QRect, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QGuiApplication, QIcon
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from PyQt5 import QtWebEngineWidgets, QtCore
from string import ascii_uppercase, ascii_lowercase
from sympy import integrate, latex, parsing, pi, preview, symbols
from sympy.abc import j, m, n, r, s, x, y, z, t, rho, theta, phi
import atexit, matplotlib, os, shutil, matplotlib.widgets, mpl_toolkits.axes_grid1
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipy as sc
import sympy as sp
matplotlib.use('Qt5Agg')

# Determina el directorio actual
directorio_base = os.path.dirname(__file__)

class Ui_InterpretacionEDP(QMainWindow):
    """Clase que contiene el diseño e interactividad de la ventana de visualización de la interpretación."""

    # La interacción entre los botones de esta ventana y la ventana principal se basa en Moore, A. D. [Alan D Moore Codes] (08 de septiembre de 2019). Master PyQt5 part 5: Moving data between windows. YouTube. https://www.youtube.com/watch?v=wOxzhX0QnAw

    # Señales necesarias para la comunicación con la ventana principal.
    resolver_signal = pyqtSignal(str)
    modificar_signal = pyqtSignal(str)
    carga_signal = pyqtSignal(str)

    def setupUi(self, ventana):
        """Diseño y configuración de la ventana de visualización de la interpretación.
        
        Parámetros
        ----------
        **ventana** : QMainWindow
            Ventana de la pantalla de visualización de la interpretación.
        """

        # Algunos aspectos a utilizar de manera repetida.
        # Asigna la imagen a un ícono. Esto se basa en Andy M. (15 de diciembre de 2009). Respuesta a la pregunta "Python QPushButton setIcon: put icon on button". stackoverflow. https://stackoverflow.com/a/1905587
        # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 2.5 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/2.5/
        icono = QIcon()
        icono.addPixmap(QPixmap(os.path.join(directorio_base, "Iconos", "IconoGraPhEr.png")), QIcon.Normal, QIcon.Off)
        
        ventana.setWindowIcon(icono)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ventana.sizePolicy().hasHeightForWidth())
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)

        # Configuración de la ventana.
        ventana.resize(1180, 960)
        ventana.setWindowTitle(u"GraPhEr - Interpretación de Entrada")
        ventana.setSizePolicy(sizePolicy)
        ventana.setMinimumSize(QSize(1180, 960))
        ventana.setStyleSheet(u"background-color: rgb(246, 247, 247); color: rgb(11, 61, 98);")
        centralwidget = QWidget(ventana)
        centralwidget.setMinimumSize(QSize(1180, 920))
        ventana.setCentralWidget(centralwidget)

        verticalLayout_0 = QVBoxLayout(centralwidget)
        verticalLayout_0.setSpacing(10)
        verticalLayout_0.setContentsMargins(10, 10, 10, 10)
        verticalLayout_0.setStretch(0, 930)

        # Diseño de la ventana de visualización.
        frame = QFrame(centralwidget)
        frame.setStyleSheet(u"color: rgb(234, 237, 239); background-color: rgba(11, 61, 98, 255)")
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)

        verticalLayout_1 = QVBoxLayout(frame)
        verticalLayout_1.setSpacing(10)
        verticalLayout_1.setStretch(0, 40)
        verticalLayout_1.setStretch(1, 10)
        verticalLayout_1.setStretch(2, 770)
        verticalLayout_1.setStretch(3, 60)
        verticalLayout_1.setContentsMargins(0, 10, 0, 10)

        label = QLabel(frame)
        label.setText(u"Interpretaci\u00f3n de la Entrada")
        label.setFont(font)
        label.setAlignment(Qt.AlignCenter)
        verticalLayout_1.addWidget(label)

        line_1 = QFrame(frame)
        line_1.setMinimumSize(QSize(0, 1))
        line_1.setStyleSheet(u"color: rgb(234, 237, 239); background-color: rgb(234, 237, 239)")
        line_1.setFrameShape(QFrame.HLine)
        line_1.setFrameShadow(QFrame.Sunken)
        verticalLayout_1.addWidget(line_1)

        verticalLayout_2 = QVBoxLayout()
        verticalLayout_2.setContentsMargins(10, 10, 10, 10)

        # Diseño y configuración del visualizador html.
        self.VisualizacionInterpretacion = QtWebEngineWidgets.QWebEngineView(frame)
        self.VisualizacionInterpretacion.setMinimumSize(QSize(1100, 770))
        self.VisualizacionInterpretacion.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        pagina = self.VisualizacionInterpretacion.page()
        pagina.loadFinished.connect(self.cargaFinalizada)
        pagina.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.VisualizacionInterpretacion.setZoomFactor(1.5)
        verticalLayout_2.addWidget(self.VisualizacionInterpretacion)
        verticalLayout_1.addLayout(verticalLayout_2)

        line_2 = QFrame(frame)
        line_2.setMinimumSize(QSize(0, 1))
        line_2.setStyleSheet(u"color: rgb(234, 237, 239); background-color: rgb(234, 237, 239)")
        line_2.setFrameShape(QFrame.HLine)
        line_2.setFrameShadow(QFrame.Sunken)
        verticalLayout_1.addWidget(line_2)

        # Diseño de los botones de interactividad: resolver y modificar.
        horizontalLayout = QHBoxLayout()
        horizontalLayout.setSpacing(200)
        horizontalLayout.setContentsMargins(130, -1, 130, -1)

        # Diseño y configuración del botón de resolver entrada.
        self.Resolver = QPushButton(frame)
        self.Resolver.setText(u"Resolver")
        self.Resolver.setMinimumSize(QSize(200, 60))
        self.Resolver.setStyleSheet(u"color: rgb(11, 61, 98); background-color: rgb(234, 237, 239)")
        self.Resolver.clicked.connect(self.resolverEntrada)
        self.Resolver.setShortcut("Return")
        horizontalLayout.addWidget(self.Resolver)

        # Diseño y configuración del botón de modificar entrada.
        self.Modificar = QPushButton(frame)
        self.Modificar.setText(u"Modificar")
        self.Modificar.setMinimumSize(QSize(200, 60))
        self.Modificar.setStyleSheet(u"color: rgb(11, 61, 98); background-color: rgb(234, 237, 239)")
        self.Modificar.clicked.connect(self.modificarEntrada)
        self.Modificar.setShortcut("Backspace")
        horizontalLayout.addWidget(self.Modificar)
        verticalLayout_1.addLayout(horizontalLayout)
        verticalLayout_0.addWidget(frame)

        # Inicialización de variable auxiliar.
        self.ready = False

        QMetaObject.connectSlotsByName(ventana)

    def cargaFinalizada(self):
        """Envia la señal de finalización de carga de la página web para mostrar la ventana de interpretación."""

        if self.ready:
            # Envio de la señal de finalización de carga.
            self.carga_signal.emit("Cargado")

    def resolverEntrada(self):
        """Envia la señal para resolver la entrada del usuario."""

        # Borrado de archivos temporales.
        self.borrarDatosAplicacion()
        QCoreApplication.processEvents()

        self.resolver_signal.emit("Resolver")

    def modificarEntrada(self):
        """Envia la señal de modificación de la entrada del usuario, devolviendo el control a la ventana principal."""

        # Borrado de archivos temporales.
        self.borrarDatosAplicacion()
        QCoreApplication.processEvents()

        self.modificar_signal.emit("Modificar")

    def borrarDatosAplicacion(self):
        """Elimina archivos creados para la visualización de la interpretación."""

        if os.path.exists('EntradaUsuario.tex'):
            os.remove('EntradaUsuario.tex')
        if os.path.exists('Entrada.html'):
            os.remove('Entrada.html')
        if os.path.exists('js'):
            shutil.rmtree('js')
        if os.path.exists('.paux'):
            os.remove('.paux')
        if os.path.exists('symbol-defs.svg'):
            os.remove('symbol-defs.svg')
        if os.path.exists('PaginaBlanca.html'):
            os.remove('PaginaBlanca.html')
