#    GraPhEr - Ecuaciones Diferenciales Parciales Separables. Un programa para la graficación de la solución aproximada a ecuaciones diferenciales párciales que admiten }
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

from Errores import ComandoInvalidoError, DimensionError, EntradaVaciaError, ExcesoEntradaError, ExtremoFaltanteError, ExcesoIncognitasError, NoExistenciaError, NoNumeroError, ValorFueraDominioError
from PantallaGrafica import Ui_Graficacion, Lienzo
from PantallaEntradaInterpretada import Ui_InterpretacionEDP
from VentanaCarga import Ui_VentanaCarga
from VentanaEtiquetas import Ui_VentanaEtiquetas
from Trabajos_Clases import Inicializacion, TrabajoInterpretacion, TrabajoResolucion, TrabajoCambiarCoordenada, TrabajoCorteEspecifico, TrabajoCurvasNivel, TrabajoCambioProyeccion, TrabajoGuardado, TrabajoVisualizacion


from matplotlib.animation import FuncAnimation, FFMpegFileWriter
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.collections import LineCollection
from plasTeX.TeX import TeX
from plasTeX.Renderers.HTML5 import Renderer
from PyQt5.QtCore import QCoreApplication, QMetaObject, QSize, Qt, QUrl, QRect, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QGuiApplication, QIcon, QMovie
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from string import ascii_uppercase, ascii_lowercase
from sympy import integrate, latex, parsing, pi, preview, symbols, Symbol
from sympy.abc import j, m, n, r, s, x, y, z, t, rho, theta, phi
from threading import Timer
import atexit, matplotlib, os, shutil, matplotlib.widgets, mpl_toolkits.axes_grid1, time, traceback
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipy as sc
import sympy as sp
matplotlib.use('Qt5Agg')

# Determina el directorio actual
directorio_base = os.path.dirname(__file__)
            
class Ui_GraficadoraVentanaPrincipal(QMainWindow):
    """Clase que contiene el diseño e interactividad de la ventana principal de la aplicación."""

    def __init__(self, ventana):
        """
        Inicializa la pantalla principal y la aplicación.
        
        Parámetros
        ----------
        **ventana** : QMainWindow
            Ventana principal.
        """

        super(self.__class__, self).__init__(ventana)
        self.VentanaPrincipal = ventana

        # Creación del thread para el procesamiento en paralelo (esta implementación es únicamente para cuestiones de interactividad mientras aparezcan pantallas de carga durante el uso de la aplicación).
        self.threadpool = QtCore.QThreadPool()
        self.threadpool.setMaxThreadCount(4)

        # Creación de la ventana principal.
        self.setupUi(self.VentanaPrincipal)

        # Creación de la ventana de carga a utilizar sin bordes.
        # La conectividad para abrir la ventana de carga a partir de la ventana principal fue tomada de Elder, J. [Codemy.com] (05 de agosto de 2021). How To Open A Second Window - PyQt5 GUI Thursdays #24. YouTube. https://www.youtube.com/watch?v=R5N8TA0KFxc
        self.VentanaCarga = QMainWindow()
        self.VentanaCarga.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.Ui_Carga = Ui_VentanaCarga()
        self.Ui_Carga.setupUi(self.VentanaCarga)

        self.Ui_Carga.label.setText("Cargando Aplicación")
        self.VentanaCarga.show()

        # El comando QCoreApplication.processEvents() fuerza a la aplicación a actualizarse, por lo que su uso aquí y en el resto de archivos tiene dicha finalidad. La utilización de esta línea de código está basada en Cárdenes, R. (06 de febrero de 2014). Respuesta a la pregunta "QDialog.show() method has a delayed reaction". stackoverflow. https://stackoverflow.com/a/21592466
        # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 3.0 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/3.0/
        QCoreApplication.processEvents()

        self.Ui_Carga.animacion.start()

        # Este trabajo solo se realiza para mostrar la pantalla de carga de la aplicación. 
        # La configuracion de las señales en los trabajos, la utilización de un pool de hilos y la configuración de las señales de comunicación fue tomada y modificada de S. Nick. (13 de agosto de 2020). Respuesta a la pregunta "How to display a loading animated gif while a code is executing in backend of my Python Qt5 UI?". stackoverflow. https://stackoverflow.com/a/63395218
        # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 4.0 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/4.0/
        trabajo = Inicializacion()
        trabajo.signals.finalizar_signal.connect(self.terminar)
        trabajo.autoDelete()
        self.threadpool.start(trabajo)

    def terminar(self, string):
        """
        Función para cerrar la ventana de carga inicial y mostrar la ventana principal de la aplicación.
        """

        self.Ui_Carga.label.setText(string)
        QCoreApplication.processEvents()
        QtCore.QThread.msleep(500)
        self.VentanaCarga.close()
        self.VentanaPrincipal.show()

    def setupUi(self, ventana):
        """Diseño y configuración de la ventana principal.
        
        Parámetros
        ----------
        **ventana** : QMainWindow
            Ventana de la pantalla principal.
        """

        # Algunos aspectos a utilizar de manera repetida.
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ventana.sizePolicy().hasHeightForWidth())
        fuente1 = QFont()
        fuente1.setPointSize(10)
        fuente1.setBold(True)
        fuente1.setWeight(75)
        fuente2 = QFont()
        fuente2.setPointSize(10)

        # Asigna la imagen a un ícono. Esto se basa en Andy M. (15 de diciembre de 2009). Respuesta a la pregunta "Python QPushButton setIcon: put icon on button". stackoverflow. https://stackoverflow.com/a/1905587
        # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 2.5 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/2.5/
        self.icono = QIcon()
        self.icono.addPixmap(QPixmap(os.path.join(directorio_base, "Iconos", "IconoGraPhEr.png")), QIcon.Normal, QIcon.Off)

        # Configuración de la ventana principal.
        ventana.resize(1680, 570)
        ventana.setWindowTitle("GraPhEr - Ecuaciones Diferenciales Parciales Separables")
        ventana.setSizePolicy(sizePolicy)
        ventana.setWindowIcon(self.icono)
        ventana.setMinimumSize(QSize(1680, 570))
        ventana.setMaximumSize(QSize(1680, 570))
        ventana.setStyleSheet("background-color: rgb(246, 247, 247); color: rgb(11, 61, 98);")
        self.centralwidget = QWidget(ventana)
        self.centralwidget.setMinimumSize(QSize(1680, 570))
        ventana.setCentralWidget(self.centralwidget)

        verticalLayout_0 = QVBoxLayout(self.centralwidget)
        verticalLayout_0.setSpacing(10)
        verticalLayout_0.setContentsMargins(10, 10, 10, 10)
        verticalLayout_0.setStretch(0, 550)

        # Diseño del cuadro superior (entrada del usuario).
        frame_1 = QFrame(self.centralwidget)
        frame_1.setSizePolicy(sizePolicy)
        frame_1.setMinimumSize(QSize(1660, 500))
        frame_1.setStyleSheet("color: rgb(11, 61, 98); background-color: rgb(246, 247, 247)")
        frame_1.setFrameShape(QFrame.StyledPanel)
        frame_1.setFrameShadow(QFrame.Raised)

        verticalLayout_1 = QVBoxLayout(frame_1)
        verticalLayout_1.setSpacing(10)
        verticalLayout_1.setContentsMargins(0, 10, 0, 5)
        verticalLayout_1.setStretch(0, 40)
        verticalLayout_1.setStretch(1, 10)
        verticalLayout_1.setStretch(2, 370)
        verticalLayout_1.setStretch(3, 10)
        verticalLayout_1.setStretch(4, 35)
           
        self.label_1 = QLabel(frame_1)
        self.label_1.setText("Entrada")
        self.label_1.setMinimumSize(QSize(1660, 20))
        self.label_1.setFont(fuente1)
        self.label_1.setAlignment(Qt.AlignCenter)
        verticalLayout_1.addWidget(self.label_1)

        line_1 = QFrame(frame_1)
        line_1.setMinimumSize(QSize(0, 5))
        line_1.setStyleSheet("color: rgb(11, 61, 98); background-color: rgb(11, 61, 98)")
        line_1.setFrameShape(QFrame.HLine)
        line_1.setFrameShadow(QFrame.Sunken)
        verticalLayout_1.addWidget(line_1)

        horizontalLayout_1 = QHBoxLayout()
        horizontalLayout_1.setSpacing(10)
        horizontalLayout_1.setContentsMargins(10, -1, 10, -1)
        horizontalLayout_1.setStretch(0, 400)
        horizontalLayout_1.setStretch(1, 10)
        horizontalLayout_1.setStretch(2, 1230)

        # Diseño de la entrada de dimensiones y sistema de coordenadas.
        verticalLayout_2 = QVBoxLayout()
        verticalLayout_2.setSpacing(10)
        verticalLayout_2.setStretch(0, 20)
        verticalLayout_2.setStretch(1, 10)
        verticalLayout_2.setStretch(2, 90)
        verticalLayout_2.setStretch(3, 10)
        verticalLayout_2.setStretch(4, 20)
        verticalLayout_2.setStretch(5, 10)
        verticalLayout_2.setStretch(6, 50)
        verticalLayout_2.setStretch(7, 10)
        verticalLayout_2.setStretch(8, 20)
        verticalLayout_2.setStretch(9, 10)
        verticalLayout_2.setStretch(10, 20)

        self.label_2 = QLabel(frame_1)
        self.label_2.setText("Dimensiones y Coordenadas")
        self.label_2.setMinimumSize(QSize(0, 25))
        self.label_2.setFont(fuente2)
        self.label_2.setAlignment(Qt.AlignCenter)
        verticalLayout_2.addWidget(self.label_2)

        line_2 = QFrame(frame_1)
        line_2.setMinimumSize(QSize(0, 10))
        line_2.setFrameShadow(QFrame.Plain)
        line_2.setFrameShape(QFrame.HLine)
        verticalLayout_2.addWidget(line_2)
        
        verticalLayout_3 = QVBoxLayout()
        verticalLayout_3.setSpacing(10)
        verticalLayout_3.setContentsMargins(10, 0, 10, 0)
        verticalLayout_3.setStretch(0, 40)
        verticalLayout_3.setStretch(1, 40)

        horizontalLayout_2 = QHBoxLayout()
        horizontalLayout_2.setSpacing(20)
        horizontalLayout_2.setContentsMargins(10, 0, 10, 0)
        horizontalLayout_2.setStretch(0, 140)
        horizontalLayout_2.setStretch(1, 200)

        horizontalLayout_3 = QHBoxLayout()
        horizontalLayout_3.setSpacing(10)
        horizontalLayout_3.setContentsMargins(10, 0, 0, 0)
        horizontalLayout_3.setStretch(0, 50)
        horizontalLayout_3.setStretch(1, 50)

        self.label_3 = QLabel()
        self.label_3.setText("Temporal")
        self.label_3.setMinimumSize(QSize(60, 30))
        self.label_3.setAlignment(Qt.AlignCenter)
        horizontalLayout_3.addWidget(self.label_3)

        self.DimensionTemporalEntrada = QCheckBox(frame_1)
        self.DimensionTemporalEntrada.setText("")
        self.DimensionTemporalEntrada.setMinimumSize(QSize(30, 40))
        self.DimensionTemporalEntrada.stateChanged.connect(self.dependenciaTemporal)
        self.DimensionTemporalEntrada.setLayoutDirection(Qt.RightToLeft)

        # La configuración para activar botones o casillas con atajos de teclado se tomó de tisaconundrum. (05 de septiembre de 2017). PyQt trigger a button with ctrl+Enter. stackoverflow. https://stackoverflow.com/q/46055411
        # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 3.0 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/3.0/
        self.DimensionTemporalEntrada.setShortcut("Ctrl+t")

        horizontalLayout_3.addWidget(self.DimensionTemporalEntrada, alignment=Qt.AlignHCenter)
        horizontalLayout_2.addLayout(horizontalLayout_3)

        horizontalLayout_4 = QHBoxLayout()
        horizontalLayout_4.setSpacing(20)
        horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        horizontalLayout_4.setStretch(0, 100)
        horizontalLayout_4.setStretch(1, 100)

        self.label_4 = QLabel()
        self.label_4.setText("# Dimensiones Espaciales")
        self.label_4.setMinimumSize(QSize(100, 30))
        self.label_4.setAlignment(Qt.AlignCenter)
        horizontalLayout_4.addWidget(self.label_4)

        self.DimensionEspacialEntrada = QSpinBox(frame_1)
        self.DimensionEspacialEntrada.setMinimumSize(QSize(60, 30))
        self.DimensionEspacialEntrada.setStyleSheet("color: rgb(11, 61, 98); background-color: rgb(255, 255, 255)")
        self.DimensionEspacialEntrada.setMaximum(3)
        self.DimensionEspacialEntrada.setMinimum(1)
        self.DimensionEspacialEntrada.valueChanged.connect(self.restriccionDimension)
        horizontalLayout_4.addWidget(self.DimensionEspacialEntrada, alignment=Qt.AlignHCenter)
        horizontalLayout_2.addLayout(horizontalLayout_4)
        verticalLayout_3.addLayout(horizontalLayout_2)

        horizontalLayout_5 = QHBoxLayout()
        horizontalLayout_5.setSpacing(20)
        horizontalLayout_5.setContentsMargins(0, 0, 10, 0)
        horizontalLayout_5.setStretch(0, 60)
        horizontalLayout_5.setStretch(1, 140)

        self.label_5 = QLabel()
        self.label_5.setText("Sistema de Coordenadas")
        self.label_5.setMinimumSize(QSize(60, 30))
        self.label_5.setAlignment(Qt.AlignCenter)
        horizontalLayout_5.addWidget(self.label_5)
        
        horizontalLayout_6 = QHBoxLayout()

        self.SistemaCoordenadas1 = QPushButton()

        # Colocación de un ícono al botón especificado (se utiliza en todos los botones a los que se les coloca un ícono). Este procedimiento se basa en Andy M. (15 de diciembre de 2009). Respuesta a la pregunta "Python QPushButton setIcon: put icon on button". stackoverflow. https://stackoverflow.com/a/1905587
        # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 2.5 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/2.5/
        self.SistemaCoordenadas1.setIcon(QIcon(os.path.join(directorio_base, "Iconos", "CoordCartesianas.png")))

        self.SistemaCoordenadas1.setIconSize(QSize(40, 30))
        self.SistemaCoordenadas1.setMaximumSize(QSize(50,40))
        self.SistemaCoordenadas1.setMinimumSize(QSize(50,40))
        self.SistemaCoordenadas1.setCheckable(True)
        self.SistemaCoordenadas1.setFlat(True)
        self.SistemaCoordenadas1.setObjectName("Cartesianas")
        self.SistemaCoordenadas1.setChecked(True)
        
        # El cambio de la apariencia cuando cualquier botón de coordenadas es presionado se basa en:
        # tomsk. (07 de enero de 2016). Flat QPushButton, background-color doesn't work. stackoverflow. https://stackoverflow.com/q/34654545. Su uso está licenciado bajo la licencia CC BY-SA 4.0 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/4.0/
        # ThorngardSO. (07 de enero de 2016). Respuesta a la pregunta "Flat QPushButton, background-color doesn't work". stackoverflow. https://stackoverflow.com/a/34654801. Su uso está licenciado bajo la licencia CC BY-SA 3.0 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/3.0/
        self.SistemaCoordenadas1.setStyleSheet("QPushButton::checked{\n border-radius: 5px;\n background-color: rgb(208, 208, 208);\n }")
        horizontalLayout_6.addWidget(self.SistemaCoordenadas1)
        
        self.SistemaCoordenadas2 = QPushButton()
        self.SistemaCoordenadas2.setIcon(QIcon(os.path.join(directorio_base, "Iconos", "CoordCilindricas.png")))
        self.SistemaCoordenadas2.setIconSize(QSize(40, 30))
        self.SistemaCoordenadas2.setMaximumSize(QSize(50,40))
        self.SistemaCoordenadas2.setMinimumSize(QSize(50,40))
        self.SistemaCoordenadas2.setCheckable(True)
        self.SistemaCoordenadas2.setFlat(True)
        self.SistemaCoordenadas2.setObjectName("Cilíndricas / Polares")
        self.SistemaCoordenadas2.setEnabled(False)
        self.SistemaCoordenadas2.setStyleSheet("QPushButton::checked{\n border-radius: 5px;\n background-color: rgb(208, 208, 208);\n }")
        horizontalLayout_6.addWidget(self.SistemaCoordenadas2)
        
        self.SistemaCoordenadas3 = QPushButton()
        self.SistemaCoordenadas3.setFlat(True)
        self.SistemaCoordenadas3.setIcon(QIcon(os.path.join(directorio_base, "Iconos", "CoordEsfericas.png")))
        self.SistemaCoordenadas3.setIconSize(QSize(40, 30))
        self.SistemaCoordenadas3.setMaximumSize(QSize(50,40))
        self.SistemaCoordenadas3.setMinimumSize(QSize(50,40))
        self.SistemaCoordenadas3.setCheckable(True)
        self.SistemaCoordenadas3.setObjectName("Esféricas")
        self.SistemaCoordenadas3.setEnabled(False)
        self.SistemaCoordenadas3.setStyleSheet("QPushButton::checked{\n border-radius: 5px;\n background-color: rgb(208, 208, 208);\n }")
        horizontalLayout_6.addWidget(self.SistemaCoordenadas3)
        horizontalLayout_5.addLayout(horizontalLayout_6)
        verticalLayout_3.addLayout(horizontalLayout_5)
        verticalLayout_2.addLayout(verticalLayout_3)

        # Configuración de los tres sistemas de coordenadas como botones mutuamente excluyentes.
        self.SistemaCoordenadasEntrada = QButtonGroup()
        self.SistemaCoordenadasEntrada.addButton(self.SistemaCoordenadas1, 1)
        self.SistemaCoordenadasEntrada.addButton(self.SistemaCoordenadas2, 2)
        self.SistemaCoordenadasEntrada.addButton(self.SistemaCoordenadas3, 3)
        self.SistemaCoordenadasEntrada.setExclusive(True)
        self.SistemaCoordenadasEntrada.buttonClicked.connect(self.restriccionDimensionSistema)

        line_3 = QFrame(frame_1)
        line_3.setMinimumSize(QSize(0, 10))
        line_3.setFrameShadow(QFrame.Plain)
        line_3.setFrameShape(QFrame.HLine)
        verticalLayout_2.addWidget(line_3)

        # Diseño de la entrada de dominios y condiciones (frontera y/o iniciales) del problema.
        self.label_6 = QLabel(frame_1)
        self.label_6.setText("Dominio y Condiciones")
        self.label_6.setMinimumSize(QSize(0, 25))
        self.label_6.setFont(fuente2)
        self.label_6.setAlignment(Qt.AlignCenter)
        verticalLayout_2.addWidget(self.label_6)

        line_4 = QFrame(frame_1)
        line_4.setMinimumSize(QSize(0, 10))
        line_4.setFrameShadow(QFrame.Plain)
        line_4.setFrameShape(QFrame.HLine)
        verticalLayout_2.addWidget(line_4)

        verticalLayout_4 = QVBoxLayout()
        verticalLayout_4.setSpacing(10)
        verticalLayout_4.setContentsMargins(10,-1,10,-1)
        verticalLayout_4.setStretch(0, 20)
        verticalLayout_4.setStretch(1, 35)

        self.x_label = QPixmap(os.path.join(directorio_base, "Iconos", 'x.svg'))
        self.y_label = QPixmap(os.path.join(directorio_base, "Iconos", 'y.svg'))
        self.z_label = QPixmap(os.path.join(directorio_base, "Iconos", 'z.svg'))
        self.t_label = QPixmap(os.path.join(directorio_base, "Iconos", 't.svg'))
        self.r_label = QPixmap(os.path.join(directorio_base, "Iconos", 'r.svg'))
        self.phi_label = QPixmap(os.path.join(directorio_base, "Iconos", 'phi.svg'))
        self.theta_label = QPixmap(os.path.join(directorio_base, "Iconos", 'theta.svg'))
        horizontalLayout_7 = QHBoxLayout()
        horizontalLayout_7.setSpacing(2)
        self.label_7 = QLabel()
        self.label_7.setPixmap(self.x_label)
        self.label_7.setMinimumSize(QSize(40, 40))
        self.label_7.setAlignment(Qt.AlignCenter)
        horizontalLayout_7.addWidget(self.label_7)

        self.DominioEspacial1Entrada = QLineEdit(frame_1)
        self.DominioEspacial1Entrada.setMinimumSize(QSize(50, 20))
        self.DominioEspacial1Entrada.setStyleSheet("background-color: rgb(255, 255, 255)")
        horizontalLayout_7.addWidget(self.DominioEspacial1Entrada)

        self.label_8 = QLabel()
        self.label_8.setPixmap(self.y_label)
        self.label_8.setMinimumSize(QSize(40, 40))
        self.label_8.setAlignment(Qt.AlignCenter)
        self.label_8.setEnabled(False)
        horizontalLayout_7.addWidget(self.label_8)

        self.DominioEspacial2Entrada = QLineEdit(frame_1)
        self.DominioEspacial2Entrada.setMinimumSize(QSize(50, 20))
        self.DominioEspacial2Entrada.setStyleSheet("background-color: rgb(255, 255, 255)")
        self.DominioEspacial2Entrada.setEnabled(False)
        horizontalLayout_7.addWidget(self.DominioEspacial2Entrada)

        self.label_9 = QLabel()
        self.label_9.setPixmap(self.z_label)
        self.label_9.setMinimumSize(QSize(40, 40))
        self.label_9.setAlignment(Qt.AlignCenter)
        self.label_9.setEnabled(False)
        horizontalLayout_7.addWidget(self.label_9)

        self.DominioEspacial3Entrada = QLineEdit(frame_1)
        self.DominioEspacial3Entrada.setMinimumSize(QSize(50, 20))
        self.DominioEspacial3Entrada.setStyleSheet("background-color: rgb(255, 255, 255)")
        self.DominioEspacial3Entrada.setEnabled(False)
        horizontalLayout_7.addWidget(self.DominioEspacial3Entrada)

        self.label_10 = QLabel()
        self.label_10.setPixmap(self.t_label)
        self.label_10.setMinimumSize(QSize(40, 40))
        self.label_10.setAlignment(Qt.AlignCenter)
        self.label_10.setEnabled(False)
        horizontalLayout_7.addWidget(self.label_10)

        self.DominioTemporalEntrada = QLineEdit(frame_1)
        self.DominioTemporalEntrada.setMinimumSize(QSize(50, 20))
        self.DominioTemporalEntrada.setStyleSheet("background-color: rgb(255, 255, 255)")
        self.DominioTemporalEntrada.setEnabled(False)
        horizontalLayout_7.addWidget(self.DominioTemporalEntrada)
        verticalLayout_4.addLayout(horizontalLayout_7)

        horizontalLayout_8 = QHBoxLayout()
        self.label_11 = QLabel(frame_1)
        self.label_11.setText(u"Condiciones Iniciales\n y/o de Frontera")
        self.label_11.setMinimumSize(QSize(150, 45))
        self.label_11.setMaximumSize(QSize(160,45))
        self.label_11.setAlignment(Qt.AlignCenter)
        self.label_11.setWordWrap(True)
        horizontalLayout_8.addWidget(self.label_11)

        self.CondicionesEntrada = QLineEdit(frame_1)
        self.CondicionesEntrada.setSizePolicy(sizePolicy)
        self.CondicionesEntrada.setMinimumSize(QSize(290, 40))
        self.CondicionesEntrada.setMaximumSize(QSize(300, 40))
        self.CondicionesEntrada.setStyleSheet("background-color: rgb(255, 255, 255)")
        horizontalLayout_8.addWidget(self.CondicionesEntrada, alignment=Qt.AlignCenter)
        verticalLayout_4.addLayout(horizontalLayout_8)
        verticalLayout_2.addLayout(verticalLayout_4)

        line_5 = QFrame(frame_1)
        line_5.setMinimumSize(QSize(0, 10))
        line_5.setFrameShadow(QFrame.Plain)
        line_5.setFrameShape(QFrame.HLine)
        verticalLayout_2.addWidget(line_5)

        # Diseño de la entrada de otras características: precisión, calidad y proyección.
        self.label_12 = QLabel(frame_1)
        self.label_12.setText("Otras Características")
        self.label_12.setMinimumSize(QSize(0, 20))
        self.label_12.setFont(fuente2)
        self.label_12.setAlignment(Qt.AlignCenter)
        verticalLayout_2.addWidget(self.label_12)

        line_6 = QFrame(frame_1)
        line_6.setMinimumSize(QSize(0, 10))
        line_6.setFrameShadow(QFrame.Plain)
        line_6.setFrameShape(QFrame.HLine)
        verticalLayout_2.addWidget(line_6)
        
        gridLayout_1 = QHBoxLayout()
        gridLayout_1.setSpacing(20)
        gridLayout_1.setContentsMargins(10, -1, 10, -1)
        gridLayout_1.setStretch(0, 80)
        gridLayout_1.setStretch(1, 40)
        gridLayout_1.setStretch(2, 10)
        gridLayout_1.setStretch(3, 60)
        gridLayout_1.setStretch(4, 30)
        gridLayout_1.setStretch(5, 60)
        gridLayout_1.setStretch(6, 30)

        self.label_13 = QLabel(frame_1)
        self.label_13.setText("Precisión")
        self.label_13.setMinimumSize(QSize(80, 30))
        self.label_13.setAlignment(Qt.AlignCenter)
        gridLayout_1.addWidget(self.label_13)

        self.PrecisionEntrada = QSpinBox(frame_1)
        self.PrecisionEntrada.setMinimumSize(QSize(50, 30))
        self.PrecisionEntrada.setMaximumSize(QSize(50, 30))
        self.PrecisionEntrada.setMinimum(2)
        self.PrecisionEntrada.setMaximum(9)
        self.PrecisionEntrada.setStyleSheet("background-color: rgb(255, 255, 255)")
        gridLayout_1.addWidget(self.PrecisionEntrada)

        self.label_14 = QLabel()
        self.label_14.setText("")
        self.label_14.setMinimumSize(QSize(5, 30))
        self.label_14.setMaximumSize(QSize(5, 30))
        self.label_14.setAlignment(Qt.AlignCenter)
        gridLayout_1.addWidget(self.label_14)

        self.label_15 = QLabel()
        self.label_15.setText("Calidad +")
        self.label_15.setMinimumSize(QSize(60, 30))
        self.label_15.setAlignment(Qt.AlignCenter)
        gridLayout_1.addWidget(self.label_15)

        self.CalidadEntrada = QCheckBox(frame_1)
        self.CalidadEntrada.setText("")
        self.CalidadEntrada.setMinimumSize(QSize(30, 40))
        self.CalidadEntrada.setMaximumSize(QSize(30, 40))
        self.CalidadEntrada.setShortcut("Ctrl+q")
        gridLayout_1.addWidget(self.CalidadEntrada)

        self.label_16 = QLabel()
        self.label_16.setText("Proyección")
        self.label_16.setMinimumSize(QSize(60, 30))
        self.label_16.setAlignment(Qt.AlignCenter)
        gridLayout_1.addWidget(self.label_16)

        self.ProyeccionEntrada = QCheckBox(frame_1)
        self.ProyeccionEntrada.setText("")
        self.ProyeccionEntrada.setMinimumSize(QSize(30, 40))
        self.ProyeccionEntrada.setMaximumSize(QSize(30, 40))
        self.ProyeccionEntrada.setShortcut("Ctrl+p")
        gridLayout_1.addWidget(self.ProyeccionEntrada)
        verticalLayout_2.addLayout(gridLayout_1)
        horizontalLayout_1.addLayout(verticalLayout_2)

        line_7 = QFrame(frame_1)
        line_7.setMinimumSize(QSize(10, 0))
        line_7.setFrameShadow(QFrame.Plain)
        line_7.setFrameShape(QFrame.VLine)
        horizontalLayout_1.addWidget(line_7)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setSpacing(10)
        self.verticalLayout_5.setStretch(0, 20)
        self.verticalLayout_5.setStretch(1, 10)
        self.verticalLayout_5.setStretch(2, 40)
        self.verticalLayout_5.setStretch(4, 400)
        self.label_17 = QLabel(frame_1)
        self.label_17.setText("Solución")
        self.label_17.setMinimumSize(QSize(0, 16))
        self.label_17.setFont(fuente2)
        self.label_17.setAlignment(Qt.AlignCenter)
        self.label_17.setWordWrap(True)
        self.verticalLayout_5.addWidget(self.label_17)

        line_8 = QFrame(frame_1)
        line_8.setFrameShadow(QFrame.Plain)
        line_8.setFrameShape(QFrame.HLine)
        self.verticalLayout_5.addWidget(line_8)

        horizontalLayout_9 = QHBoxLayout()
        horizontalLayout_9.setSpacing(50)
        horizontalLayout_9.setContentsMargins(50, -1 , 50, -1)
        horizontalLayout_9.setStretch(0, 300)
        horizontalLayout_9.setStretch(1, 600)

        # Diseño de la entrada de número de subproblemas (equivalente al número de subsoluciones) a ingresar.
        horizontalLayout_10 = QHBoxLayout()
        horizontalLayout_10.setSpacing(10)
        horizontalLayout_10.setContentsMargins(0, -1 , 0, -1)
        horizontalLayout_10.setStretch(0, 220)
        horizontalLayout_10.setStretch(1, 60)
        self.label_18 = QLabel(frame_1)
        self.label_18.setText("Número de Subproblemas")
        self.label_18.setMinimumSize(QSize(220, 30))
        self.label_18.setAlignment(Qt.AlignCenter)
        horizontalLayout_10.addWidget(self.label_18)

        self.NumeroEntradas = QLineEdit(frame_1)
        self.NumeroEntradas.setFixedSize(QSize(60, 30))
        self.NumeroEntradas.setStyleSheet("background-color: rgb(255, 255, 255)")
        self.NumeroEntradas.setEnabled(False)
        self.NumeroEntradas.setText("1")
        horizontalLayout_10.addWidget(self.NumeroEntradas)
        horizontalLayout_9.addLayout(horizontalLayout_10)

        self.NumeroEntradasS = QSlider(frame_1)
        self.NumeroEntradasS.setOrientation(Qt.Horizontal)
        self.NumeroEntradasS.setSingleStep(1)
        self.NumeroEntradasS.setMinimumSize(QSize(550, 30))
        self.NumeroEntradasS.setMinimum(1)
        self.NumeroEntradasS.setMaximum(10)
        self.NumeroEntradasS.valueChanged.connect(lambda: self.numeroSubproblemas(self.NumeroEntradasS.value()))
        horizontalLayout_9.addWidget(self.NumeroEntradasS)
        self.verticalLayout_5.addLayout(horizontalLayout_9)

        # Diseño de la ventana de expresiones solución a los subproblemas.
        # El diseño de la ventana de expresiones fue tomado y modificado de Lim, J. (16 de abril de 2024). Add scrollable regions with QScrollArea. Run out of space in your GUI? Add a scrollable region to your application. PythonGUIs. https://www.pythonguis.com/tutorials/qscrollarea/
        self.VentanaExpresiones = QScrollArea(frame_1)
        self.VentanaExpresiones.setMinimumSize(QSize(1120, 350))
        self.VentanaExpresiones.setStyleSheet("color: rgb(11, 61, 98); background-color: rgb(246, 247, 247)")
        self.VentanaExpresiones.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.VentanaExpresiones.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.VentanaExpresiones.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        deslizador = self.VentanaExpresiones.horizontalScrollBar()
        deslizador.setStyleSheet("color: rgb(246, 247, 247); background-color:  rgb(11, 61, 98)")
        deslizador.setPageStep(1120)
        deslizador.setSingleStep(1120)
        sizePolicy_1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.VentanaExpresiones.setSizePolicy(sizePolicy_1)
        self.widget = QWidget()
        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setSpacing(10)
        self.horizontalLayout_11.setContentsMargins(5, 0, 5, 0)
        self.horizontalLayout_11.setStretch(0, 1115)
        self.horizontalLayout_11.setStretch(1, 1115)
        self.horizontalLayout_11.setStretch(2, 1115)
        self.horizontalLayout_11.setStretch(3, 1115)
        self.horizontalLayout_11.setStretch(4, 1115)
        self.horizontalLayout_11.setStretch(5, 1115)
        self.horizontalLayout_11.setStretch(6, 1115)
        self.horizontalLayout_11.setStretch(7, 1115)
        self.horizontalLayout_11.setStretch(8, 1115)
        self.horizontalLayout_11.setStretch(9, 1115)

        # Diseño de los cuadros para cada subsolución.
        self.Cuadro1 = QFrame()
        self.Cuadro2 = QFrame()
        self.Cuadro3 = QFrame()
        self.Cuadro4 = QFrame()
        self.Cuadro5 = QFrame()
        self.Cuadro6 = QFrame()
        self.Cuadro7 = QFrame()
        self.Cuadro8 = QFrame()
        self.Cuadro9 = QFrame()
        self.Cuadro10 = QFrame()

        self.Cuadros = {'0':self.Cuadro1, '1':self.Cuadro2, '2':self.Cuadro3, '3':self.Cuadro4, '4':self.Cuadro5, '5':self.Cuadro6, '6':self.Cuadro7, '7':self.Cuadro8, '8':self.Cuadro9, '9':self.Cuadro10}
        
        for indice in range(0, len(self.Cuadros)):
            self.Cuadros[str(indice)].setFrameShape(QFrame.StyledPanel)
            self.Cuadros[str(indice)].setFrameShadow(QFrame.Raised)
            self.Cuadros[str(indice)].setStyleSheet("color: rgb(11, 61, 98); background-color: rgb(246, 247, 247)")
            self.Cuadros[str(indice)].setMinimumSize(QSize(1110, 300))

        verticalLayout_6 = QVBoxLayout()
        verticalLayout_7 = QVBoxLayout()
        verticalLayout_8 = QVBoxLayout()
        verticalLayout_9 = QVBoxLayout()
        verticalLayout_10 = QVBoxLayout()
        verticalLayout_11 = QVBoxLayout()
        verticalLayout_12 = QVBoxLayout()
        verticalLayout_13 = QVBoxLayout()
        verticalLayout_14 = QVBoxLayout()
        verticalLayout_15 = QVBoxLayout()

        verticalLayouts = {'0':verticalLayout_6, '1':verticalLayout_7, '2':verticalLayout_8, '3':verticalLayout_9, '4':verticalLayout_10, '5':verticalLayout_11, '6':verticalLayout_12, '7':verticalLayout_13, '8':verticalLayout_14, '9':verticalLayout_15}

        for indice in range(0, len(verticalLayouts)):
            verticalLayouts[str(indice)].setSpacing(0)
            verticalLayouts[str(indice)].setContentsMargins(10, 0, 10, 0)
            verticalLayouts[str(indice)].setStretch(0, 20)
            verticalLayouts[str(indice)].setStretch(1, 10)
            verticalLayouts[str(indice)].setStretch(2, 20)
            verticalLayouts[str(indice)].setStretch(3, 10)
            verticalLayouts[str(indice)].setStretch(4, 160)
            self.Cuadros[str(indice)].setLayout(verticalLayouts[str(indice)])

        # Diseño de las etiquetas que indican la subsolución asociada a cada cuadro.
        self.label_19 = QLabel()
        self.label_26 = QLabel()
        self.label_33 = QLabel()
        self.label_40 = QLabel()
        self.label_47 = QLabel()
        self.label_54 = QLabel()
        self.label_61 = QLabel()
        self.label_68 = QLabel()
        self.label_75 = QLabel()
        self.label_82 = QLabel()

        labelssubproblemas = {'0':self.label_19, '1':self.label_26, '2':self.label_33, '3':self.label_40, '4':self.label_47, '5':self.label_54, '6':self.label_61, '7':self.label_68, '8':self.label_75, '9':self.label_82}

        for indice in range(0, len(labelssubproblemas)):
            labelssubproblemas[str(indice)].setFont(fuente2)
            labelssubproblemas[str(indice)].setText("Solución del Subproblema #{}".format(indice+1))
            labelssubproblemas[str(indice)].setMinimumSize(QSize(100, 25))
            labelssubproblemas[str(indice)].setFixedHeight(25)
            labelssubproblemas[str(indice)].setAlignment(Qt.AlignCenter)
            verticalLayouts[str(indice)].addWidget(labelssubproblemas[str(indice)])

        line_9 = QFrame()
        line_10 = QFrame()
        line_11 = QFrame()
        line_12 = QFrame()
        line_13 = QFrame()
        line_14 = QFrame()
        line_15 = QFrame()
        line_16 = QFrame()
        line_17 = QFrame()
        line_18 = QFrame()
        line_19 = QFrame()
        line_20 = QFrame()
        line_21 = QFrame()
        line_22 = QFrame()
        line_23 = QFrame()
        line_24 = QFrame()
        line_25 = QFrame()
        line_26 = QFrame()
        line_27 = QFrame()
        line_28 = QFrame()

        lines = {'0':line_9, '1':line_10, '2':line_11, '3':line_12, '4':line_13, '5':line_14, '6':line_15, '7':line_16, '8':line_17, '9':line_18, '10':line_19, '11':line_20, '12':line_21, '13':line_22, '14':line_23, '15':line_24, '16':line_25, '17':line_26, '18':line_27, '19':line_28}

        for indice in range(0, len(lines)):
            lines[str(indice)].setMinimumSize(QSize(0, 1))
            lines[str(indice)].setFrameShadow(QFrame.Raised)
            lines[str(indice)].setFrameShape(QFrame.HLine)
            if (indice % 2) == 0:
                verticalLayouts[str(indice//2)].addWidget(lines[str(indice)])

        horizontalLayout_12 = QHBoxLayout()
        horizontalLayout_13 = QHBoxLayout()
        horizontalLayout_14 = QHBoxLayout()
        horizontalLayout_15 = QHBoxLayout()
        horizontalLayout_16 = QHBoxLayout()
        horizontalLayout_17 = QHBoxLayout()
        horizontalLayout_18 = QHBoxLayout()
        horizontalLayout_19 = QHBoxLayout()
        horizontalLayout_20 = QHBoxLayout()
        horizontalLayout_21 = QHBoxLayout()

        horizontalLayouts = {'0':horizontalLayout_12, '1':horizontalLayout_13, '2':horizontalLayout_14, '3':horizontalLayout_15, '4':horizontalLayout_16, '5':horizontalLayout_17, '6':horizontalLayout_18, '7':horizontalLayout_19, '8':horizontalLayout_20, '9':horizontalLayout_21}

        for indice in range(0, len(horizontalLayouts)):
            horizontalLayouts[str(indice)].setSpacing(15)
            horizontalLayouts[str(indice)].setContentsMargins(5, 0, 5, 0)
            horizontalLayouts[str(indice)].setStretch(0, 200)
            horizontalLayouts[str(indice)].setStretch(1, 350)
            horizontalLayouts[str(indice)].setStretch(2, 180)
            horizontalLayouts[str(indice)].setStretch(3, 40)
            horizontalLayouts[str(indice)].setStretch(4, 100)
            horizontalLayouts[str(indice)].setStretch(5, 50)

        self.label_20 = QLabel()
        self.label_21 = QLabel()
        self.label_22 = QLabel()
        self.label_23 = QLabel()
        self.label_24 = QLabel()
        self.label_25 = QLabel()
        self.label_27 = QLabel()
        self.label_28 = QLabel()
        self.label_29 = QLabel()
        self.label_30 = QLabel()
        self.label_31 = QLabel()
        self.label_32 = QLabel()
        self.label_34 = QLabel()
        self.label_35 = QLabel()
        self.label_36 = QLabel()
        self.label_37 = QLabel()
        self.label_38 = QLabel()
        self.label_39 = QLabel()
        self.label_41 = QLabel()
        self.label_42 = QLabel()
        self.label_43 = QLabel()
        self.label_44 = QLabel()
        self.label_45 = QLabel()
        self.label_46 = QLabel()
        self.label_48 = QLabel()
        self.label_49 = QLabel()
        self.label_50 = QLabel()
        self.label_51 = QLabel()
        self.label_52 = QLabel()
        self.label_53 = QLabel()
        self.label_55 = QLabel()
        self.label_56 = QLabel()
        self.label_57 = QLabel()
        self.label_58 = QLabel()
        self.label_59 = QLabel()
        self.label_60 = QLabel()
        self.label_62 = QLabel()
        self.label_63 = QLabel()
        self.label_64 = QLabel()
        self.label_65 = QLabel()
        self.label_66 = QLabel()
        self.label_67 = QLabel()
        self.label_69 = QLabel()
        self.label_70 = QLabel()
        self.label_71 = QLabel()
        self.label_72 = QLabel()
        self.label_73 = QLabel()
        self.label_74 = QLabel()
        self.label_76 = QLabel()
        self.label_77 = QLabel()
        self.label_78 = QLabel()
        self.label_79 = QLabel()
        self.label_80 = QLabel()
        self.label_81 = QLabel()
        self.label_83 = QLabel()
        self.label_84 = QLabel()
        self.label_85 = QLabel()
        self.label_86 = QLabel()
        self.label_87 = QLabel()
        self.label_88 = QLabel()

        labels = {'0':self.label_20, '1':self.label_21, '2':self.label_22, '3':self.label_23, '4':self.label_24, '5':self.label_25, '6':self.label_27, '7':self.label_28, '8':self.label_29, '9':self.label_30, '10':self.label_31, '11':self.label_32, '12':self.label_34, '13':self.label_35, '14':self.label_36, '15':self.label_37, '16':self.label_38, '17':self.label_39, '18':self.label_41, '19':self.label_42, '20':self.label_43, '21':self.label_44, '22':self.label_45, '23':self.label_46, '24':self.label_48, '25':self.label_49, '26':self.label_50, '27':self.label_51, '28':self.label_52, '29':self.label_53, '30':self.label_55, '31':self.label_56, '32':self.label_57, '33':self.label_58, '34':self.label_59, '35':self.label_60, '36':self.label_62, '37':self.label_63, '38':self.label_64, '39':self.label_65, '40':self.label_66, '41':self.label_67, '42':self.label_69, '43':self.label_70, '44':self.label_71, '45':self.label_72, '46':self.label_73, '47':self.label_74, '48':self.label_76, '49':self.label_77, '50':self.label_78, '51':self.label_79, '52':self.label_80, '53':self.label_81, '54':self.label_83, '55':self.label_84, '56':self.label_85, '57':self.label_86, '58':self.label_87, '59':self.label_88}

        # Diseño de la entrada de valores propios para cada subsolución.
        for indice in range(0, len(labels)):
            if (indice % 6) == 0:
                labels[str(indice)].setText("Valores Propios")
                labels[str(indice)].setMinimumSize(QSize(140, 30))
                labels[str(indice)].setAlignment(Qt.AlignCenter)
                horizontalLayouts[str(indice//6)].addWidget(labels[str(indice)])

        self.ValoresPropios1 = QLineEdit()
        self.ValoresPropios2 = QLineEdit()
        self.ValoresPropios3 = QLineEdit()
        self.ValoresPropios4 = QLineEdit()
        self.ValoresPropios5 = QLineEdit()
        self.ValoresPropios6 = QLineEdit()
        self.ValoresPropios7 = QLineEdit()
        self.ValoresPropios8 = QLineEdit()
        self.ValoresPropios9 = QLineEdit()
        self.ValoresPropios10 = QLineEdit()

        self.ValoresPropiosEntrada = {'0':self.ValoresPropios1, '1':self.ValoresPropios2, '2':self.ValoresPropios3 ,'3':self.ValoresPropios4 ,'4':self.ValoresPropios5, '5':self.ValoresPropios6, '6':self.ValoresPropios7 ,'7':self.ValoresPropios8 ,'8':self.ValoresPropios9 ,'9':self.ValoresPropios10}

        for indice in range(0, len(self.ValoresPropiosEntrada)):
            self.ValoresPropiosEntrada[str(indice)].setMinimumSize(QSize(370, 30))
            self.ValoresPropiosEntrada[str(indice)].setStyleSheet("background-color: rgb(255, 255, 255)")
            horizontalLayouts[str(indice)].addWidget(self.ValoresPropiosEntrada[str(indice)])

        # Diseño de la entrada de números de términos a considerar para cada subsolución.
        for indice in range(0, len(labels)):
            if (indice % 6) == 1:
                labels[str(indice)].setText(u"N\u00famero de T\u00e9rminos")
                labels[str(indice)].setMinimumSize(QSize(170, 30))
                labels[str(indice)].setMaximumSize(QSize(170, 30))
                labels[str(indice)].setAlignment(Qt.AlignCenter)
                horizontalLayouts[str((indice-1)//6)].addWidget(labels[str(indice)])

        # Diseño de la entrada de valores propios para cada subsolución.
        self.NumeroTerminos1 = QLineEdit()
        self.NumeroTerminos2 = QLineEdit()
        self.NumeroTerminos3 = QLineEdit()
        self.NumeroTerminos4 = QLineEdit()
        self.NumeroTerminos5 = QLineEdit()
        self.NumeroTerminos6 = QLineEdit()
        self.NumeroTerminos7 = QLineEdit()
        self.NumeroTerminos8 = QLineEdit()
        self.NumeroTerminos9 = QLineEdit()
        self.NumeroTerminos10 = QLineEdit()

        self.NumeroTerminosEntrada = {'0':self.NumeroTerminos1, '1':self.NumeroTerminos2, '2':self.NumeroTerminos3 ,'3':self.NumeroTerminos4 ,'4':self.NumeroTerminos5, '5':self.NumeroTerminos6, '6':self.NumeroTerminos7 ,'7':self.NumeroTerminos8 ,'8':self.NumeroTerminos9 ,'9':self.NumeroTerminos10}

        for indice in range(0, len(self.NumeroTerminosEntrada)):
            self.NumeroTerminosEntrada[str(indice)].setMinimumSize(QSize(130, 30))
            self.NumeroTerminosEntrada[str(indice)].setMaximumSize(QSize(130, 30))
            self.NumeroTerminosEntrada[str(indice)].setStyleSheet("background-color: rgb(255, 255, 255)")
            horizontalLayouts[str(indice)].addWidget(self.NumeroTerminosEntrada[str(indice)])

        # Diseño de la entrada de la función peso para cada subsolución.
        for indice in range(0, len(labels)):
            if (indice % 6) == 2:
                labels[str(indice)].setText("Función Peso")
                labels[str(indice)].setMinimumSize(QSize(100, 30))
                labels[str(indice)].setMaximumSize(QSize(100, 30))
                labels[str(indice)].setAlignment(Qt.AlignCenter)
                horizontalLayouts[str((indice-2)//6)].addWidget(labels[str(indice)])

        self.FuncionPeso1 = QLineEdit()
        self.FuncionPeso2 = QLineEdit()
        self.FuncionPeso3 = QLineEdit()
        self.FuncionPeso4 = QLineEdit()
        self.FuncionPeso5 = QLineEdit()
        self.FuncionPeso6 = QLineEdit()
        self.FuncionPeso7 = QLineEdit()
        self.FuncionPeso8 = QLineEdit()
        self.FuncionPeso9 = QLineEdit()
        self.FuncionPeso10 = QLineEdit()

        self.FuncionesPesoEntrada = {'0':self.FuncionPeso1, '1':self.FuncionPeso2, '2':self.FuncionPeso3 ,'3':self.FuncionPeso4 ,'4':self.FuncionPeso5, '5':self.FuncionPeso6, '6':self.FuncionPeso7 ,'7':self.FuncionPeso8 ,'8':self.FuncionPeso9 ,'9':self.FuncionPeso10}

        for indice in range(0, len(self.FuncionesPesoEntrada)):
            self.FuncionesPesoEntrada[str(indice)].setMinimumSize(QSize(40, 30))
            self.FuncionesPesoEntrada[str(indice)].setStyleSheet("background-color: rgb(255, 255, 255)")
            horizontalLayouts[str(indice)].addWidget(self.FuncionesPesoEntrada[str(indice)])
            verticalLayouts[str(indice)].addLayout(horizontalLayouts[str(indice)])

        for indice in range(0, len(lines)):
            if (indice % 2) != 0:
                verticalLayouts[str((indice-1)//2)].addWidget(lines[str(indice)])

        gridLayout_2 = QGridLayout()
        gridLayout_3 = QGridLayout()
        gridLayout_4 = QGridLayout()
        gridLayout_5 = QGridLayout()
        gridLayout_6 = QGridLayout()
        gridLayout_7 = QGridLayout()
        gridLayout_8 = QGridLayout()
        gridLayout_9 = QGridLayout()
        gridLayout_10 = QGridLayout()
        gridLayout_11 = QGridLayout()

        gridLayouts = {'0':gridLayout_2, '1':gridLayout_3, '2':gridLayout_4 ,'3':gridLayout_5 ,'4':gridLayout_6, '5':gridLayout_7, '6':gridLayout_8 ,'7':gridLayout_9 ,'8':gridLayout_10 ,'9':gridLayout_11}

        for indice in range(0, len(gridLayouts)):
            gridLayouts[str(indice)].setHorizontalSpacing(20)
            gridLayouts[str(indice)].setVerticalSpacing(10)
            gridLayouts[str(indice)].setContentsMargins(10, 0, 10, 0)
            gridLayouts[str(indice)].setRowStretch(0, 50)
            gridLayouts[str(indice)].setRowStretch(1, 50)
            gridLayouts[str(indice)].setRowStretch(2, 50)
            gridLayouts[str(indice)].setColumnStretch(0, 180)
            gridLayouts[str(indice)].setColumnStretch(1, 900)

        # Diseño de la entrada de coeficientes de las subsoluciones para cada subproblema.
        for indice in range(0, len(labels)):
            if (indice % 6) == 3:
                labels[str(indice)].setText("Coeficientes")
                labels[str(indice)].setMinimumSize(QSize(180, 40))
                labels[str(indice)].setMaximumSize(QSize(180, 40))
                labels[str(indice)].setAlignment(Qt.AlignCenter)
                labels[str(indice)].setWordWrap(True)
                gridLayouts[str((indice-3)//6)].addWidget(labels[str(indice)], 0, 0, 1, 1)

        self.Coeficientes1 = QLineEdit()
        self.Coeficientes2 = QLineEdit()
        self.Coeficientes3 = QLineEdit()
        self.Coeficientes4 = QLineEdit()
        self.Coeficientes5 = QLineEdit()
        self.Coeficientes6 = QLineEdit()
        self.Coeficientes7 = QLineEdit()
        self.Coeficientes8 = QLineEdit()
        self.Coeficientes9 = QLineEdit()
        self.Coeficientes10 = QLineEdit()

        self.CoeficientesEntrada = {'0':self.Coeficientes1, '1':self.Coeficientes2, '2':self.Coeficientes3 ,'3':self.Coeficientes4 ,'4':self.Coeficientes5, '5':self.Coeficientes6, '6':self.Coeficientes7 ,'7':self.Coeficientes8 ,'8':self.Coeficientes9 ,'9':self.Coeficientes10}

        for indice in range(0, len(self.CoeficientesEntrada)):
            self.CoeficientesEntrada[str(indice)].setMinimumSize(QSize(870, 40))
            self.CoeficientesEntrada[str(indice)].setStyleSheet("background-color: rgb(255, 255, 255)")
            gridLayouts[str(indice)].addWidget(self.CoeficientesEntrada[str(indice)], 0, 1, 1, 1)

        # Diseño de la entrada de las funciones espaciales de las subsoluciones para cada subproblema.
        for indice in range(0, len(labels)):
            if (indice % 6) == 4:
                labels[str(indice)].setText("Funciones Espaciales")
                labels[str(indice)].setMinimumSize(QSize(180, 40))
                labels[str(indice)].setMaximumSize(QSize(180, 40))
                labels[str(indice)].setAlignment(Qt.AlignCenter)
                labels[str(indice)].setWordWrap(True)
                gridLayouts[str((indice-4)//6)].addWidget(labels[str(indice)], 1, 0, 1, 1)

        self.FuncionEspacial1 = QLineEdit()
        self.FuncionEspacial2 = QLineEdit()
        self.FuncionEspacial3 = QLineEdit()
        self.FuncionEspacial4 = QLineEdit()
        self.FuncionEspacial5 = QLineEdit()
        self.FuncionEspacial6 = QLineEdit()
        self.FuncionEspacial7 = QLineEdit()
        self.FuncionEspacial8 = QLineEdit()
        self.FuncionEspacial9 = QLineEdit()
        self.FuncionEspacial10 = QLineEdit()

        self.FuncionesEspacialesEntrada = {'0':self.FuncionEspacial1, '1':self.FuncionEspacial2, '2':self.FuncionEspacial3 ,'3':self.FuncionEspacial4 ,'4':self.FuncionEspacial5 ,'5':self.FuncionEspacial6 ,'6':self.FuncionEspacial7 ,'7':self.FuncionEspacial8 ,'8':self.FuncionEspacial9 ,'9':self.FuncionEspacial10}

        for indice in range(0, len(self.FuncionesEspacialesEntrada)):
            self.FuncionesEspacialesEntrada[str(indice)].setMinimumSize(QSize(870, 40))
            self.FuncionesEspacialesEntrada[str(indice)].setStyleSheet("background-color: rgb(255, 255, 255)")
            gridLayouts[str(indice)].addWidget(self.FuncionesEspacialesEntrada[str(indice)], 1, 1, 1, 1)

        # Diseño de la entrada de las funciones temporales de las subsoluciones para cada subproblema.
        for indice in range(0, len(labels)):
            if (indice % 6) == 5:
                labels[str(indice)].setText("Funciones Temporales")
                labels[str(indice)].setMinimumSize(QSize(180, 40))
                labels[str(indice)].setMaximumSize(QSize(180, 40))
                labels[str(indice)].setAlignment(Qt.AlignCenter)
                labels[str(indice)].setWordWrap(True)
                labels[str(indice)].setVisible(False)
                gridLayouts[str((indice-5)//6)].addWidget(labels[str(indice)], 2, 0, 1, 1)

        self.FuncionTemporal1 = QLineEdit()
        self.FuncionTemporal2 = QLineEdit()
        self.FuncionTemporal3 = QLineEdit()
        self.FuncionTemporal4 = QLineEdit()
        self.FuncionTemporal5 = QLineEdit()
        self.FuncionTemporal6 = QLineEdit()
        self.FuncionTemporal7 = QLineEdit()
        self.FuncionTemporal8 = QLineEdit()
        self.FuncionTemporal9 = QLineEdit()
        self.FuncionTemporal10 = QLineEdit()

        sizePolicy2 = self.FuncionTemporal1.sizePolicy()
        sizePolicy2.setRetainSizeWhenHidden(True)

        self.FuncionesTemporalesEntrada = {'0':self.FuncionTemporal1 ,'1':self.FuncionTemporal2 ,'2':self.FuncionTemporal3 ,'3':self.FuncionTemporal4 ,'4':self.FuncionTemporal5 ,'5':self.FuncionTemporal6, '6':self.FuncionTemporal7 ,'7':self.FuncionTemporal8 ,'8':self.FuncionTemporal9 ,'9':self.FuncionTemporal10}
        self.FuncionesTemporalesEtiquetas = {'0':self.label_25, '1':self.label_32, '2':self.label_39 ,'3':self.label_46 ,'4':self.label_53, '5':self.label_60, '6':self.label_67 ,'7':self.label_74 ,'8':self.label_81,'9':self.label_88}

        for indice in range(0, len(self.FuncionesTemporalesEntrada)):
            self.FuncionesTemporalesEntrada[str(indice)].setMinimumSize(QSize(870, 40))
            self.FuncionesTemporalesEntrada[str(indice)].setStyleSheet("background-color: rgb(255, 255, 255)")
            self.FuncionesTemporalesEntrada[str(indice)].setVisible(False)
            self.FuncionesTemporalesEntrada[str(indice)].setEnabled(False)
            self.FuncionesTemporalesEntrada[str(indice)].setSizePolicy(sizePolicy2)
            gridLayouts[str(indice)].addWidget(self.FuncionesTemporalesEntrada[str(indice)], 2, 1, 1, 1)
            verticalLayouts[str(indice)].addLayout(gridLayouts[str(indice)])
        
        self.horizontalLayout_11.addWidget(self.Cuadro1)
        self.widget.setLayout(self.horizontalLayout_11)
        self.widget.setFixedHeight(300)
        self.VentanaExpresiones.setWidget(self.widget)
        self.VentanaExpresiones.setWidgetResizable(True)
        self.verticalLayout_5.addWidget(self.VentanaExpresiones)
        horizontalLayout_1.addLayout(self.verticalLayout_5)
        verticalLayout_1.addLayout(horizontalLayout_1)

        # Diseño del cuadro inferior (botones de ejecución)
        line_29 = QFrame(frame_1)
        line_29.setMinimumSize(QSize(0, 1))
        line_29.setFrameShadow(QFrame.Plain)
        line_29.setFrameShape(QFrame.HLine)
        verticalLayout_1.addWidget(line_29)

        horizontalLayout_22 = QHBoxLayout()
        horizontalLayout_22.setSpacing(200)
        horizontalLayout_22.setContentsMargins(130, -1, 130, -1)

        # Diseño y configuración del botón de interpretación.
        self.Interpretar = QPushButton(frame_1)
        self.Interpretar.setText("Interpretar")
        self.Interpretar.setMinimumSize(QSize(200, 35))
        self.Interpretar.setStyleSheet("color: rgb(234, 237, 239); background-color: rgb(11, 61, 98) ")

        # La conectividad para abrir una ventana a partir de otra se basa en Elder, J. [Codemy.com] (05 de agosto de 2021). How To Open A Second Window - PyQt5 GUI Thursdays #24. YouTube. https://www.youtube.com/watch?v=R5N8TA0KFxc
        self.Interpretar.clicked.connect(self.interpretarEntrada)

        self.Interpretar.setShortcut("Ctrl+I")
        horizontalLayout_22.addWidget(self.Interpretar)

        # Diseño y configuración del botón de visualización.
        self.Visualizar = QPushButton(frame_1)
        self.Visualizar.setText("Visualizar")
        self.Visualizar.setMinimumSize(QSize(200, 35))
        self.Visualizar.setStyleSheet("color: rgb(234, 237, 239); background-color: rgb(11, 61, 98) ")

        # La desconexión del botón de visualización para evitar el envío doble de las señales se realizó de acuerdo con ingvar. (14 de octubre de 2017). Respuesta a la pregunta "When a QPushButton is clicked, it fires twice". stackoverflow. https://stackoverflow.com/a/46748321
        # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 3.0 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/3.0/
        try:
            self.Visualizar.clicked.disconnect()
        except:
            pass
        self.Visualizar.clicked.connect(self.visualizarSolucion)

        self.Visualizar.setShortcut("Ctrl+o")
        horizontalLayout_22.addWidget(self.Visualizar)

        # Diseño y configuración del botón de limpieza de datos.
        self.Limpiar = QPushButton(frame_1)
        self.Limpiar.setText("Limpiar")
        self.Limpiar.setMinimumSize(QSize(200, 35))
        self.Limpiar.setStyleSheet("color: rgb(234, 237, 239); background-color: rgb(11, 61, 98) ")
        self.Limpiar.clicked.connect(self.limpiarEntradas)
        self.Limpiar.setShortcut("Ctrl+l")
        horizontalLayout_22.addWidget(self.Limpiar)
        verticalLayout_1.addLayout(horizontalLayout_22)
        verticalLayout_0.addWidget(frame_1)

        # Inicialización de ventanas y variables auxiliares.
        self.entradaresuelta = False
        self.cierretotal = False
        self.MensajeError = QMessageBox()
        self.error = False
        self.ventanaInterpretacion()
        self.ventanaGraficacion()
        # La creación de la lista de letras del abecedario fue tomada de jamylak. (17 de abril de 2013). Respuesta a la pregunta "Alphabet range in Python". stackoverflow. https://stackoverflow.com/a/16060908
        # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 4.0 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/4.0/
        self.variables = list(ascii_uppercase)

        # Borra datos previos en caso de que se haya terminado el programa erróneamente.
        borrardatosaplicacion(self, False) 

        # Scripts en LaTeX para la creación del documento en donde se muestra el resultado de la interpretación.
        self.inicioTex = r'''\documentclass[40pt]{memoir}\usepackage[paperwidth=820mm, paperheight=220mm, left = 50mm, right = 50mm, top = 20mm, bottom = 20mm]{geometry}\usepackage{amsmath, amssymb, amsthm}\usepackage[spanish]{babel}\usepackage[utf8]{inputenc}\usepackage{tabularx} \begin{document}\LARGE\centering\begin{table}[!h]\begin{tabular}{|c|ccccccc|} \hline &\\ [-0.5em]'''
        
        self.Entrada = r'''\textbf{Solución} & \multicolumn{7}{c|}{$\displaystyle u(\mathbf{x}) \approx %(solucion)s $} \\ \hline \textbf{Coeficientes} & \multicolumn{7}{c|}{$\displaystyle %(coeficientes)s$} \\ \hline \textbf{Valores Propios} & \multicolumn{7}{c|}{$\displaystyle %(valores)s$} \\ \hline \textbf{Funciones Peso} & \multicolumn{7}{c|}{$\displaystyle %(funciones)s$} \\ \hline \textbf{Condiciones}  & \multicolumn{7}{c|}{$\quad \displaystyle %(condiciones)s \quad$} \\ \hline \textbf{Dominio}  & \multicolumn{7}{c|}{$\quad \displaystyle %(dominio)s \quad$} \\ '''

        self.finTex = r'''\hline\end{tabular} \end{table}\end{document}'''

        with open('EntradaUsuario.tex','w') as f:
            f.write("Entrada del Usuario")

        # Inicialización de algunas entradas y botones.
        self.PrecisionEntrada.setValue(3)
        self.FuncionPeso1.setText("1")
        self.FuncionPeso2.setText("1")
        self.FuncionPeso3.setText("1")
        self.FuncionPeso4.setText("1")
        self.FuncionPeso5.setText("1")
        self.FuncionPeso6.setText("1")
        self.FuncionPeso7.setText("1")
        self.FuncionPeso8.setText("1")
        self.FuncionPeso9.setText("1")
        self.FuncionPeso10.setText("1")
        self.Visualizar.setDisabled(True)
        self.Visualizar.setStyleSheet("background-color : rgb(127,146,151); color: rgb(234,237,239);")

        QMetaObject.connectSlotsByName(ventana)

    def actualizarVentanaEmergente(self, string):
        """
        Actualiza la ventana de carga.
        
        Parámetros
        ----------
        string: string
            Frase a colocar en la ventana de carga.
        """

        self.Ui_Carga.label.setText(string)
        QCoreApplication.processEvents()
    
    def mostrarError(self, mensaje):
        """Muestra la ventana de error cuando se detecte un error durante la ejecución.
        
        Parámetros
        ----------
        **mensaje** : tupla
            Contiene el tipo de error y la posible causa del error.
        """

        QtCore.QThread.msleep(500)
        self.error = True
        self.MensajeError.close()
        self.VentanaCarga.close()
        self.Ui_Interpretacion.ready = False

        # Cambia los botones de interpretar y visualizar a su configuración inicial.
        if self.VentanaGrafica.isHidden():
            self.Interpretar.setEnabled(True)
            self.Interpretar.setStyleSheet("color: rgb(234, 237, 239); background-color: rgb(11, 61, 98);")
            self.Interpretar.setText("Interpretar")
            self.Interpretar.setShortcut("Ctrl+I")
            self.Visualizar.setDisabled(True)
            self.Visualizar.setStyleSheet("background-color : rgb(127,146,151); color: rgb(234,237,239);")

        # Diseño, configuración y ejecución de la ventana de error.
        # La creación de la ventana de error se basa en NShiell. (08 de enero de 2019). Respuesta a la pregunta "Python PyQt5: How to show an error message with PyQt5". stackoverflow. https://stackoverflow.com/a/54094498
        # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 4.0 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/4.0/
        self.MensajeError = QMessageBox()
        self.MensajeError.setWindowIcon(self.icono)
        self.MensajeError.setStyleSheet("color: rgb(246, 246, 247) ; background-color: rgb(11, 68, 98)")
        self.MensajeError.setIcon(QMessageBox.Critical)
        self.MensajeError.setText("<b>Hay un error en la entrada</b><br><br> \nDescripción del error:<br> <i>{}</i>".format(mensaje[1]))
        self.MensajeError.setWindowModality(Qt.WindowModal)
        self.MensajeError.setInformativeText("Por favor revisa tu entrada.")
        self.MensajeError.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowType.Dialog)
        self.MensajeError.setWindowTitle(mensaje[0])
        self.MensajeError.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.MensajeError.button(QtWidgets.QMessageBox.Ok).setStyleSheet("background-color: rgb(246, 246, 247) ; color: rgb(11, 68, 98)")
        self.MensajeError.exec_()

        self.error = False

    def interpretarEntrada(self):
        """Realiza la interpretación de la entrada del usuario."""

        # Diseño de la ventana de carga.
        self.Ui_Carga.label.setText("Iniciando Interpretación")
        self.Ui_Carga.animacion = QMovie(os.path.join(directorio_base, "Carga", "InterpretacionCarga.gif"))
        self.Ui_Carga.animacion.setScaledSize(QSize(400,121))
        self.Ui_Carga.icono.setMovie(self.Ui_Carga.animacion)
        self.Ui_Carga.animacion.start()
        QCoreApplication.processEvents()
        
        # Configuración y ejecución del trabajo de interpretación.
        trabajo = TrabajoInterpretacion(self, self.centralwidget)
        trabajo.signals.finalizar_signal.connect(self.finalizarInterpretacion)
        trabajo.signals.avanzar_signal.connect(self.actualizarVentanaEmergente)
        trabajo.signals.error_signal.connect(self.mostrarError)
        trabajo.autoDelete()
        self.VentanaCarga.show()
        self.threadpool.start(trabajo)

    def limpiarEntradas(self):
        """Borra toda la información introducida en los campos de entrada y restablece la ventana principal a su estado inicial."""

        self.DominioEspacial1Entrada.clear()
        self.DominioEspacial2Entrada.clear()
        self.DominioEspacial3Entrada.clear()
        self.DominioTemporalEntrada.clear()
        self.CondicionesEntrada.clear()
        self.PrecisionEntrada.setValue(3)
        self.ValoresPropios1.clear() 
        self.ValoresPropios2.clear()
        self.ValoresPropios3.clear()
        self.ValoresPropios4.clear()
        self.ValoresPropios5.clear()
        self.ValoresPropios6.clear()
        self.ValoresPropios7.clear()
        self.ValoresPropios8.clear()
        self.ValoresPropios9.clear()
        self.ValoresPropios10.clear()
        self.NumeroTerminos1.clear()
        self.NumeroTerminos2.clear()
        self.NumeroTerminos3.clear()
        self.NumeroTerminos4.clear()
        self.NumeroTerminos5.clear()
        self.NumeroTerminos6.clear()
        self.NumeroTerminos7.clear()
        self.NumeroTerminos8.clear()
        self.NumeroTerminos9.clear()
        self.NumeroTerminos10.clear()
        self.FuncionPeso1.setText("1")
        self.FuncionPeso2.setText("1")
        self.FuncionPeso3.setText("1")
        self.FuncionPeso4.setText("1")
        self.FuncionPeso5.setText("1")
        self.FuncionPeso6.setText("1")
        self.FuncionPeso7.setText("1")
        self.FuncionPeso8.setText("1")
        self.FuncionPeso9.setText("1")
        self.FuncionPeso10.setText("1")
        self.FuncionEspacial1.clear()
        self.FuncionEspacial2.clear()
        self.FuncionEspacial3.clear()
        self.FuncionEspacial4.clear()
        self.FuncionEspacial5.clear()
        self.FuncionEspacial6.clear()
        self.FuncionEspacial7.clear()
        self.FuncionEspacial8.clear()
        self.FuncionEspacial9.clear()
        self.FuncionEspacial10.clear()
        self.FuncionTemporal1.clear()
        self.FuncionTemporal2.clear()
        self.FuncionTemporal3.clear()
        self.FuncionTemporal4.clear()
        self.FuncionTemporal5.clear()
        self.FuncionTemporal6.clear()
        self.FuncionTemporal7.clear()
        self.FuncionTemporal8.clear()
        self.FuncionTemporal9.clear()
        self.FuncionTemporal10.clear()
        self.Coeficientes1.clear()
        self.Coeficientes2.clear()
        self.Coeficientes3.clear()
        self.Coeficientes4.clear()
        self.Coeficientes5.clear()
        self.Coeficientes6.clear()
        self.Coeficientes7.clear()
        self.Coeficientes8.clear()
        self.Coeficientes9.clear()
        self.Coeficientes10.clear()
        self.DimensionTemporalEntrada.setChecked(False)
        self.DimensionEspacialEntrada.setMinimum(1)
        self.DimensionEspacialEntrada.setValue(1)
        self.SistemaCoordenadas1.setChecked(True)
        self.SistemaCoordenadas1.click()
        self.NumeroEntradasS.setValue(1)
        self.Interpretar.setText("Interpretar")
        self.Interpretar.setShortcut("Ctrl+I")
        self.Visualizar.setDisabled(True)
        self.Visualizar.setStyleSheet("background-color : rgb(127,146,151); color: rgb(234,237,239);")

    def restriccionDimension(self):
        """Habilita o deshabilita opciones de dimensión de acuerdo al valor de la QSpinBox DimensionEspacialEntrada para no superar el límite de tres coordenadas (tres espaciales o dos espaciales y una temporal)."""

        if self.DimensionEspacialEntrada.value() == 1:
            # Deshabilita las coordenadas esféricas/polares y las coordenadas esféricas, bajo esta opción solo se permiten soluciones en coordenadas cartesianas con dependencia temporal.
            self.SistemaCoordenadasEntrada.button(2).setEnabled(False)
            self.SistemaCoordenadasEntrada.button(2).setStyleSheet("QPushButton::checked{\n border-radius: 5px;\n background-color: rgb(208, 208, 208);\n }")
            self.SistemaCoordenadasEntrada.button(3).setEnabled(False)
            self.SistemaCoordenadasEntrada.button(3).setStyleSheet("QPushButton::checked{\n border-radius: 5px;\n background-color: rgb(208, 208, 208);\n }")
            self.DimensionTemporalEntrada.setEnabled(True)
            self.label_8.setEnabled(False)
            self.label_9.setEnabled(False)
            self.DominioEspacial2Entrada.setEnabled(False)
            self.DominioEspacial3Entrada.setEnabled(False)
            self.DominioEspacial2Entrada.setText("")
            self.DominioEspacial3Entrada.setText("")
        elif self.DimensionEspacialEntrada.value() == 2:
            # Deshabilita el sistema de coordenadas esférico, esto permite problemas en coordenadas cartesianas o polares con o sin dependencia temporal.
            self.SistemaCoordenadasEntrada.button(2).setEnabled(True)
            self.SistemaCoordenadasEntrada.button(2).setStyleSheet("QPushButton::checked{\n border-radius: 5px;\n background-color: rgb(208, 208, 208);\n }")
            self.SistemaCoordenadasEntrada.button(3).setEnabled(False)
            self.SistemaCoordenadasEntrada.button(3).setStyleSheet("QPushButton::checked{\n border-radius: 5px;\n background-color: rgb(208, 208, 208);\n }")
            self.DimensionTemporalEntrada.setEnabled(True)
            self.label_8.setEnabled(True)
            self.DominioEspacial2Entrada.setEnabled(True)
            self.label_9.setEnabled(False)
            self.DominioEspacial3Entrada.setEnabled(False)
            self.DominioEspacial3Entrada.setText("")
        elif self.DimensionEspacialEntrada.value() == 3:
            # Deshabilita la coordenada temporal y habilita los tres sistemas de coordenadas.
            self.SistemaCoordenadasEntrada.button(2).setEnabled(True)
            self.SistemaCoordenadasEntrada.button(2).setStyleSheet("QPushButton::checked{\n border-radius: 5px;\n background-color: rgb(208, 208, 208);\n }")
            self.SistemaCoordenadasEntrada.button(3).setEnabled(True)
            self.SistemaCoordenadasEntrada.button(3).setStyleSheet("QPushButton::checked{\n border-radius: 5px;\n background-color: rgb(208, 208, 208);\n }")
            self.DimensionTemporalEntrada.setEnabled(False)
            self.DimensionTemporalEntrada.setChecked(False)
            self.label_8.setEnabled(True)
            self.DominioEspacial2Entrada.setEnabled(True)
            self.label_9.setEnabled(True)
            self.DominioEspacial3Entrada.setEnabled(True)
            self.DominioTemporalEntrada.setText("")

    def restriccionDimensionSistema(self, button):
        """Habilita o deshabilita opciones de dimensión de acuerdo al sistema de coordenadas elegido para no superar el límite de tres coordenadas (tres espaciales o dos espaciales y una temporal), además cambia los iconos de las entradas de dominio."""
        
        if button.objectName() == "Cartesianas":
            # Establece las coordenadas (x, y, z) y establece el mínimo de dimensiones espaciales en uno.
            self.label_7.setPixmap(self.x_label)
            self.label_8.setPixmap(self.y_label)
            self.label_9.setPixmap(self.z_label)
            self.DimensionEspacialEntrada.setMinimum(1)
        elif button.objectName() == "Cilíndricas / Polares":
            # Establece las coordenadas (r, phi, z) y establece el mínimo de dimensiones espaciales en dos.
            self.label_7.setPixmap(self.r_label)
            self.label_8.setPixmap(self.phi_label)
            self.label_9.setPixmap(self.z_label)
            if self.DimensionEspacialEntrada.value() < 2:
                self.DimensionEspacialEntrada.setValue(2)
            self.DimensionEspacialEntrada.setMinimum(2)
        elif button.objectName() == "Esféricas":
            # Establece las coordenadas (r, theta, phi) y establece el mínimo de dimensiones espaciales en tres.
            self.label_7.setPixmap(self.r_label)
            self.label_8.setPixmap(self.theta_label)
            self.label_9.setPixmap(self.phi_label)
            if self.DimensionEspacialEntrada.value() < 3:
                self.DimensionEspacialEntrada.setValue(3)
            self.DimensionEspacialEntrada.setMinimum(3)
    
    def numeroSubproblemas(self, valor):
        """Muestra o oculta los cuadros de entrada de subsoluciones dependiendo de la cantidad de subproblemas a ingresar.
        
        Parámetros
        ----------
        **valor : entero
            Cantidad de subproblemas a ingresar.
        """

        if valor < int(self.NumeroEntradas.text()):
            # Oculta los cuadros no necesarios si el valor del deslizador es menor que el valor anterior.
            for i in range(valor, int(self.NumeroEntradas.text())):
                self.horizontalLayout_11.removeWidget(self.Cuadros['{}'.format(i)])
                self.ValoresPropiosEntrada['{}'.format(i)].clear()
                self.NumeroTerminosEntrada['{}'.format(i)].clear()
                self.FuncionesPesoEntrada['{}'.format(i)].setText("1")
                self.CoeficientesEntrada['{}'.format(i)].clear()
                self.FuncionesEspacialesEntrada['{}'.format(i)].clear()
                self.FuncionesTemporalesEntrada['{}'.format(i)].clear()
            self.NumeroEntradas.setText("{}".format(valor))
        else:
            # Muestra los cuadros necesarios si el valor del deslizador es mayor que el valor anterior.
            for i in range(int(self.NumeroEntradas.text()), valor):
                self.horizontalLayout_11.addWidget(self.Cuadros['{}'.format(i)])
            self.NumeroEntradas.setText("{}".format(valor))

        # Modifica el deslizador de la ventana de entrada de soluciones.
        deslizador = self.VentanaExpresiones.horizontalScrollBar()
        deslizador.setMaximum(valor*1120)

    def dependenciaTemporal(self):
        """Habilita o deshabilita opciones de dimensión y campos de entrada de funciones temporales de acuerdo al estado del QChekBox DimensionTemporalEntrada."""

        if self.DimensionTemporalEntrada.isChecked():
            # Habilita el campo de entrada de dominio temporal y establece el máximo de dimensiones espaciales en dos.
            self.label_10.setEnabled(True)
            self.DominioTemporalEntrada.setEnabled(True)
            self.DimensionEspacialEntrada.setMaximum(2)
        else:
            # Deshabilita el campo de entrada de dominio temporal y esestablece el máximo de dimensiones espaciales en tres.
            self.label_10.setEnabled(False)
            self.DominioTemporalEntrada.setEnabled(False)
            self.DominioTemporalEntrada.setText("")
            self.DimensionEspacialEntrada.setMaximum(3)
        for i in range(0, 10):
            if self.DimensionTemporalEntrada.isChecked():
                # Habilita los campos de entrada de funciones temporales de las subsoluciones.
                self.FuncionesTemporalesEntrada[str(i)].setEnabled(True)
                self.FuncionesTemporalesEntrada[str(i)].setVisible(True)
                self.FuncionesTemporalesEtiquetas[str(i)].setVisible(True)
            else:
                # Deshabilita los campos de entrada de funciones temporales de las subsoluciones.
                self.FuncionesTemporalesEntrada[str(i)].setEnabled(False)
                self.FuncionesTemporalesEntrada[str(i)].setVisible(False)
                self.FuncionesTemporalesEtiquetas[str(i)].setVisible(False)
                self.FuncionesTemporalesEntrada[str(i)].setText("")

    def decisionVentanaInterpretacion(self, string):
        """Ejecuta el trabajo de resolución de la entrada del usuario si el usuario confirma su entrada en la ventana de interpretación, o cierra la ventana de interpretacion para que el usuario realice modificaciones a su entrada."""

        self.ventanaVisualizacionInterpretacion.close()
        QCoreApplication.processEvents()

        if string == "Resolver":
            # Si el usuario confirma su entrada se procede a resolverla.

            # Diseño de la ventana de carga.
            QtCore.QThread.msleep(500)
            self.Ui_Carga.label.setText("Iniciando Proceso")
            self.Ui_Carga.animacion = QMovie(os.path.join(directorio_base, "Carga", "SolucionCarga.gif"))
            self.Ui_Carga.animacion.setScaledSize(QSize(206,150))
            self.Ui_Carga.icono.setMovie(self.Ui_Carga.animacion)
            self.Ui_Carga.animacion.start()
            QCoreApplication.processEvents()

            # Configuración y ejecución del trabajo de resolución.
            trabajo = TrabajoResolucion(self, self.centralwidget)
            trabajo.signals.finalizar_signal.connect(self.finalizarResolucion)
            trabajo.signals.avanzar_signal.connect(self.actualizarVentanaEmergente)
            trabajo.signals.error_signal.connect(self.mostrarError)
            trabajo.autoDelete()
            self.VentanaCarga.show()
            self.threadpool.start(trabajo)
        else:
            try:
                self.Visualizar.clicked.disconnect()
            except:
                pass
            self.Visualizar.clicked.connect(self.visualizarSolucion)

    def finalizarResolucion(self, mensaje):
        """
        Actualiza la pantalla de carga tras la finalización de la resolución.

        Parámetros
        ----------
        **mensaje : string
            Mensaje a desplegar en la pantalla de carga.
        """

        # Actualiza la pantalla de carga y la cierra posteriormente después de un periodo de medio segundo.
        self.actualizarVentanaEmergente(mensaje)
        QtCore.QThread.msleep(500)
        self.VentanaCarga.close()
        self.Interpretar.setShortcut("Ctrl+I")
        try:
            self.Visualizar.clicked.disconnect()
        except:
            pass
        self.Visualizar.clicked.connect(self.visualizarSolucion)
 
    def finalizarInterpretacion(self, mensaje):
        """
        Esta función tiene dos finalidades:
        
        - Actualiza la pantalla de carga tras la finalización de la interpretación y la carga de la página web, posteriormente muestra la ventana de visualización de la interpretación.

        - Envía la página web a la ventana de visualización de interpretación.

        Parámetros
        ----------
        **mensaje** : string
            Mensaje a desplegar en la pantalla de carga.
        """

        self.Interpretar.setShortcut("Ctrl+I")

        if mensaje == "Cargado":
            # Cierra la ventana de carga cuando se ha finalizado la carga de la página web con la interpretación de la entrada.
            QtCore.QThread.msleep(500)
            self.VentanaCarga.close()
            self.ventanaVisualizacionInterpretacion.show()
        else:
            # Envia el archivo html de la página web donde se muestra la interpretación de la entrada del usuario a la pantalla de visualización de la interpretación.
            self.Ui_Interpretacion.ready = True

            # La visualización de la página html creada se basa en Dhimal, R. (01 de noviembre de 2020). How to add(render) HTML file in PyQT5 Dialog Box. Medium. https://rojandhimal.medium.com/how-to-add-render-html-file-in-pyqt5-dialog-box-4fc259a8f5a
            self.Ui_Interpretacion.VisualizacionInterpretacion.load(QUrl.fromLocalFile(os.path.abspath('Entrada.html')))

            self.actualizarVentanaEmergente(mensaje)
            QtCore.QThread.msleep(500)
            
    def ventanaInterpretacion(self):
        """Crea la ventana de visualización de la interpretación de la entrada del usuario. Así mismo conecta sus señales con las funciones de la ventana principal."""

        # La conectividad para abrir la ventana de interpretación a partir de la ventana principal fue tomada de Elder, J. [Codemy.com] (05 de agosto de 2021). How To Open A Second Window - PyQt5 GUI Thursdays #24. YouTube. https://www.youtube.com/watch?v=R5N8TA0KFxc
        self.ventanaVisualizacionInterpretacion = QMainWindow()
        self.Ui_Interpretacion = Ui_InterpretacionEDP()
        self.Ui_Interpretacion.setupUi(self.ventanaVisualizacionInterpretacion)

        self.Ui_Interpretacion.resolver_signal.connect(self.decisionVentanaInterpretacion)
        self.Ui_Interpretacion.modificar_signal.connect(self.decisionVentanaInterpretacion)
        self.Ui_Interpretacion.carga_signal.connect(self.finalizarInterpretacion)
        self.ventanaVisualizacionInterpretacion.setWindowFlags(Qt.WindowType.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

    def ventanaGraficacion(self):
        """Crea la ventana de visualización de gráfica calculada a partir de la entrada del usuario. Así mismo conecta sus señales con las funciones de la ventana principal."""

        # La conectividad para abrir la ventana de graficación a partir de la ventana principal fue tomada de Elder, J. [Codemy.com] (05 de agosto de 2021). How To Open A Second Window - PyQt5 GUI Thursdays #24. YouTube. https://www.youtube.com/watch?v=R5N8TA0KFxc
        self.VentanaGrafica = PantallaGraficacion(self)
        self.Ui_Grafica = Ui_Graficacion(self.VentanaGrafica)

        # La desconexión del botón de guardado para evitar el envío doble de las señales se realizó de acuerdo con ingvar. (14 de octubre de 2017). Respuesta a la pregunta "When a QPushButton is clicked, it fires twice". stackoverflow. https://stackoverflow.com/a/46748321
        # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 3.0 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/3.0/
        try:
            self.Ui_Grafica.GuardarAnimacion.clicked.disconnect()
            self.Ui_Grafica.GraficarCoordenadaFija.clicked.disconnect()
            self.Ui_Grafica.CoordenadaFija_Casilla.buttonClicked.disconnect()
            self.Ui_Grafica.Grupo.buttonClicked.disconnect()
            self.Ui_Grafica.ProyeccionEntrada.stateChanged.disconnect()
            self.Ui_Grafica.GraficarCurvasFija.clicked.disconnect()
        except:
            pass
        self.Ui_Grafica.GuardarAnimacion.clicked.connect(self.guardarAnimacion)
        self.Ui_Grafica.GraficarCoordenadaFija.clicked.connect(self.graficarCorte)
        self.Ui_Grafica.CoordenadaFija_Casilla.buttonClicked.connect(self.cambiarCoordenadaFija)
        self.Ui_Grafica.Grupo.buttonClicked.connect(self.visualizarCurvasNivel)
        self.Ui_Grafica.ProyeccionEntrada.stateChanged.connect(self.cambiarProyeccion)
        self.Ui_Grafica.GraficarCurvasFija.clicked.connect(self.visualizarCurvasNivel)

        # La conectividad para abrir la ventana de etiquetas a partir de la ventana de graficación fue tomada de Elder, J. [Codemy.com] (05 de agosto de 2021). How To Open A Second Window - PyQt5 GUI Thursdays #24. YouTube. https://www.youtube.com/watch?v=R5N8TA0KFxc
        self.Ui_Grafica.Ui_Etiquetas = Ui_VentanaEtiquetas()
        self.Ui_Grafica.VentanaEtiquetas = QMainWindow()
        self.Ui_Grafica.Ui_Etiquetas.setupUi(self.Ui_Grafica.VentanaEtiquetas)

    def cambiarCoordenadaFija(self):
        """Ejecuta el trabajo de cambio de coordenada fija en la visualización gráfica para problemas con tres dimensiones espaciales."""

        if not (self.DimensionTemporalEntrada.isChecked() and self.DimensionEspacialEntrada.value() == 1):
            # Diseño de la ventana de carga.
            self.Ui_Carga.label.setText("Iniciando Proceso")
            self.Ui_Carga.animacion = QMovie(os.path.join(directorio_base, "Carga", "CoordenadaCarga.gif"))
            self.Ui_Carga.animacion.setScaledSize(QSize(227,150))
            self.Ui_Carga.icono.setMovie(self.Ui_Carga.animacion)
            self.Ui_Carga.animacion.start()
            QCoreApplication.processEvents()
            
            # Fija el valor de la nueva coordenada fija en el valor mínimo del dominio correspondiente.
            if self.Ui_Grafica.CoordenadaFija_1.isChecked():
                self.Ui_Grafica.CoordenadaFija.setText("{}".format(self.Ui_Grafica.dominio[0]))
            elif self.Ui_Grafica.CoordenadaFija_2.isChecked():
                self.Ui_Grafica.CoordenadaFija.setText("{}".format(self.Ui_Grafica.dominio[2]))
            elif self.Ui_Grafica.CoordenadaFija_3.isChecked():
                self.Ui_Grafica.CoordenadaFija.setText("{}".format(self.Ui_Grafica.dominio[4]))

            # Configuración y ejecución del trabajo de cambio de coordenada fija.
            trabajo = TrabajoCambiarCoordenada(self.Ui_Grafica)
            trabajo.signals.finalizar_signal.connect(self.finalizarCambio)
            trabajo.signals.avanzar_signal.connect(self.actualizarVentanaEmergente)
            trabajo.signals.error_signal.connect(self.mostrarError)  
            trabajo.autoDelete()
            self.VentanaCarga.show()
            self.threadpool.start(trabajo, 0)

    def finalizarCambio(self, mensaje):
        """
        Actualiza la ventana de carga y después inicia la animación de entrada de la gráfica con la nueva coordenada fija.

        Parámetros
        ----------
        **mensaje** : string
            Mensaje a desplegar en la pantalla de carga.
        """

        # Actualiza la ventana de carga e inicia la animación.
        self.Interpretar.setShortcut("Ctrl+I")
        self.Ui_Grafica.GuardarAnimacion.setShortcut("Ctrl+S")
        self.Ui_Grafica.CurvasNivelAuto.setShortcut("Ctrl+A")
        self.Ui_Grafica.CurvasNivelEspecificas.setShortcut("Ctrl+E")
        self.Ui_Carga.label.setText(mensaje)
        QCoreApplication.processEvents()
        QtCore.QThread.msleep(500)
        self.VentanaCarga.close()
        if self.DimensionTemporalEntrada.isChecked() or (self.DimensionEspacialEntrada.value() == 3):
            # La desconexión de los botones de reproducción para evitar el envío doble de las señales se realizó de acuerdo con ingvar. (14 de octubre de 2017). Respuesta a la pregunta "When a QPushButton is clicked, it fires twice". stackoverflow. https://stackoverflow.com/a/46748321
            # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 3.0 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/3.0/
            try:
                self.Ui_Grafica.BotonPasoAtras.clicked.disconnect()
                self.Ui_Grafica.BotonReproduccionAtras.clicked.disconnect()
                self.Ui_Grafica.BotonReproduccionAdelante.clicked.disconnect()
                self.Ui_Grafica.BotonPausa.clicked.disconnect()
                self.Ui_Grafica.BotonPasoAdelante.clicked.disconnect()
                self.Ui_Grafica.deslizador.valueChanged.disconnect()
                self.Ui_Grafica.GuardarAnimacion.clicked.disconnect()
                self.Ui_Grafica.GraficarCurvasFija.clicked.disconnect()
            except:
                pass

            self.Ui_Grafica.BotonPasoAtras.clicked.connect(self.Ui_Grafica.Animacion.pasoAtras)
            self.Ui_Grafica.BotonReproduccionAtras.clicked.connect(self.Ui_Grafica.Animacion.reproduccionAtras)
            self.Ui_Grafica.BotonReproduccionAdelante.clicked.connect(self.Ui_Grafica.Animacion.reproduccionAdelante)
            self.Ui_Grafica.BotonPausa.clicked.connect(self.Ui_Grafica.Animacion.detener)
            self.Ui_Grafica.BotonPasoAdelante.clicked.connect(self.Ui_Grafica.Animacion.pasoAdelante)
            self.Ui_Grafica.deslizador.setMaximum(self.Ui_Grafica.Animacion.maximo-self.Ui_Grafica.Animacion.argumentos[0])
            self.Ui_Grafica.deslizador.valueChanged.connect(self.Ui_Grafica.Animacion.actualizarGrafica)
            self.Ui_Grafica.GuardarAnimacion.clicked.connect(self.guardarAnimacion)
            self.Ui_Grafica.GraficarCurvasFija.clicked.connect(self.visualizarCurvasNivel)
        self.Ui_Grafica.Animacion.iniciar()
        self.Ui_Grafica.MostrarSolucion.figura.canvas.draw_idle()

    def graficarCorte(self):
        """Ejecuta el trabajo de cambio de corte, es decir, realiza el trabajo de graficación en problemas de tres dimensiones espaciales para el valor especificado por el usuario para la coordenada fija actual."""

        # Diseño de la ventana de carga.
        self.Ui_Carga.label.setText("Iniciando Proceso")
        self.Ui_Carga.animacion = QMovie(os.path.join(directorio_base, "Carga", "CorteCarga.gif"))
        self.Ui_Carga.animacion.setScaledSize(QSize(227,150))
        self.Ui_Carga.icono.setMovie(self.Ui_Carga.animacion)
        self.Ui_Carga.animacion.start()
        QCoreApplication.processEvents()
    
        # Configuración y ejecución del trabajo de graficación de corte específico.
        trabajo = TrabajoCorteEspecifico(self.Ui_Grafica)
        trabajo.signals.finalizar_signal.connect(self.finalizarGraficacionCorte)
        trabajo.signals.avanzar_signal.connect(self.actualizarVentanaEmergente)
        trabajo.signals.error_signal.connect(self.mostrarError)  
        trabajo.autoDelete()
        self.VentanaCarga.show()
        self.threadpool.start(trabajo, 0)

    def finalizarGraficacionCorte(self, mensaje):
        """
        Actualiza la ventana de carga y después la cierra para permitir la visualización de la gráfica con el nuevo corte.

        Parámetros
        ----------
        **mensaje : string
            Mensaje a desplegar en la pantalla de carga.
        """

        # Actualiza la ventana de carga e inicia la animación.
        self.Interpretar.setShortcut("Ctrl+I")
        self.Ui_Grafica.GuardarAnimacion.setShortcut("Ctrl+S")
        self.Ui_Grafica.CurvasNivelAuto.setShortcut("Ctrl+A")
        self.Ui_Grafica.CurvasNivelEspecificas.setShortcut("Ctrl+E")
        self.Ui_Carga.label.setText(mensaje)
        self.Ui_Grafica.MostrarSolucion.figura.canvas.draw_idle()
        QCoreApplication.processEvents()
        QtCore.QThread.msleep(500)
        self.VentanaCarga.close()

    def visualizarCurvasNivel(self):
        """Ejecuta el trabajo de visualización de curvas de nivel para problemas de dos dimensiones espaciales o para problemas de tres dimensiones espaciales en donde se proyectan los cortes."""

        if (not self.VentanaGrafica.isHidden()) and (self.Ui_Grafica.CurvasEspecificasEntrada.text() != ""):
            # Si la ventana de graficación se encuentra abierta procede mostrar u ocultar las curvas de nivel de acuerdo a lo especificado por el usuario.

            # Diseño de la ventana de carga.
            self.Ui_Carga.label.setText("Iniciando Proceso")
            if self.Ui_Grafica.CurvasNivelAuto.isChecked():
                self.Ui_Carga.animacion = QMovie(os.path.join(directorio_base, "Carga", "CurvasAutoCarga.gif"))
            else:
                self.Ui_Carga.animacion = QMovie(os.path.join(directorio_base, "Carga", "CurvasEspecificasCarga.gif"))
            self.Ui_Carga.animacion.setScaledSize(QSize(227,150))
            self.Ui_Carga.icono.setMovie(self.Ui_Carga.animacion)
            self.Ui_Carga.animacion.start()
            QCoreApplication.processEvents()

            # Creación y presentación de la leyenda asociada a las curvas de nivel graficadas.
            if not self.Ui_Grafica.etiquetas:
                # Crea la leyenda de la gráfica con curvas de nivel la primera vez que el usuario solicita visualizar las curvas de nivel.
                self.Ui_Grafica.Ui_Etiquetas.MostrarEtiqueta.axes = self.Ui_Grafica.Ui_Etiquetas.MostrarEtiqueta.figura.add_subplot()
                self.Ui_Grafica.Ui_Etiquetas.MostrarEtiqueta.axes.set_position([0, 0, 1, 1])
                self.Ui_Grafica.Ui_Etiquetas.MostrarEtiqueta.axes.set_facecolor((0.52, 0.50, 0.49, 1.0))
                self.Ui_Grafica.Ui_Etiquetas.MostrarEtiqueta.figura.set_facecolor((0.52, 0.50, 0.49, 1.0))
                self.Ui_Grafica.Ui_Etiquetas.MostrarEtiqueta.axes.set_visible(True)
                #self.Ui_Grafica.Ui_Etiquetas.MostrarEtiqueta.axes.axis('off')
                self.Ui_Grafica.Ui_Etiquetas.MostrarEtiqueta.axes.set_title("")
                self.Ui_Grafica.Ui_Etiquetas.MostrarEtiqueta.figura.set_visible(True)
                self.Ui_Grafica.Ui_Etiquetas.MostrarEtiqueta.figura.canvas.draw_idle()
                self.Ui_Grafica.etiquetas = True

            # Configuración y ejecución del trabajo de visualización de curvas de nivel.
            trabajo = TrabajoCurvasNivel(self.Ui_Grafica)
            trabajo.signals.finalizar_signal.connect(self.finalizarActualizacionCurvas)
            trabajo.signals.avanzar_signal.connect(self.actualizarVentanaEmergente)
            trabajo.signals.error_signal.connect(self.mostrarError)  
            trabajo.autoDelete()
            self.VentanaCarga.show()
            self.threadpool.start(trabajo, 0)

    def finalizarActualizacionCurvas(self, mensaje):
        """
        Actualiza la ventana de carga y después la cierra para permitir la visualización de la gráfica con las curvas de nivel (o sin ellas si el usuario decidió removerlas). Si la leyenda está oculta y el usuario solicito visualizar curvas de también la muestra; en caso de que el usuario elimine las curvas de nivel se oculta la leyenda.

        Parámetros
        ----------
        **mensaje** : string
            Mensaje a desplegar en la pantalla de carga.
        """

        # Actualiza la ventana de carga.
        self.Interpretar.setShortcut("Ctrl+I")
        self.Ui_Grafica.GuardarAnimacion.setShortcut("Ctrl+S")
        self.Ui_Grafica.CurvasNivelAuto.setShortcut("Ctrl+A")
        self.Ui_Grafica.CurvasNivelEspecificas.setShortcut("Ctrl+E")
        self.Ui_Carga.label.setText(mensaje)
        self.Ui_Grafica.MostrarSolucion.figura.canvas.draw_idle()
        QCoreApplication.processEvents()
        QtCore.QThread.msleep(500)
        self.VentanaCarga.close()
        if ((not self.Ui_Grafica.VentanaEtiquetas.isHidden()) or self.Ui_Grafica.curvasdibujadas) and (self.Ui_Grafica.CurvasNivelAuto.isChecked() or self.Ui_Grafica.CurvasNivelEspecificas.isChecked()):
            # Si la leyenda se encuentra oculta, la muestra.
            self.Ui_Grafica.VentanaEtiquetas.show()
        else:
            self.Ui_Grafica.MostrarSolucion.axes.grid(True)
            if len(self.Ui_Grafica.MostrarSolucion.figura.axes) > 8:
                self.Ui_Grafica.MostrarSolucion.axes2.grid(True)
            # Oculta la leyenda si el usuario solicita no mostrar las curvas de nivel.
            self.Ui_Grafica.VentanaEtiquetas.setHidden(True)

    def cambiarProyeccion(self):
        """Ejecuta el trabajo de cambio de proyeccion entre visualizacion tridimensional y bidimensional o entre visualizacion unidimensional y bidimensional."""


        if not self.VentanaGrafica.isHidden():
            # Si la ventana de graficación se encuentra abierta procede a realizar el cambio entre proyecciones.

            # Diseño de la ventana de carga.
            self.Ui_Carga.label.setText("Iniciando Proceso")
            self.Ui_Carga.animacion = QMovie(os.path.join(directorio_base, "Carga", "ProyeccionCarga.gif"))
            self.Ui_Carga.animacion.setScaledSize(QSize(227,150))
            self.Ui_Carga.icono.setMovie(self.Ui_Carga.animacion)
            self.Ui_Carga.animacion.start()
            QCoreApplication.processEvents()

            if self.Ui_Grafica.etiquetas and (len(self.Ui_Grafica.dominio) == 6):
                # Oculta la leyenda de las curvas de nivel en problemas de tres dimensiones espaciales. 
                self.Ui_Grafica.VentanaEtiquetas.close()

            # Configuración y ejecución del trabajo de cambio de proyección.
            trabajo = TrabajoCambioProyeccion(self.Ui_Grafica)
            trabajo.signals.finalizar_signal.connect(self.finalizarCambioProyeccion)
            trabajo.signals.avanzar_signal.connect(self.actualizarVentanaEmergente)
            trabajo.signals.error_signal.connect(self.mostrarError)  
            trabajo.autoDelete()
            self.VentanaCarga.show()
            self.threadpool.start(trabajo, 0)

    def finalizarCambioProyeccion(self, mensaje):
        """
        Actualiza la ventana de carga y después inicia la animación de entrada de la gráfica con la nueva proyección.

        Parámetros
        ----------
        **mensaje** : string
            Mensaje a desplegar en la pantalla de carga.
        """

        # Inicia la animación y actualiza la ventana de carga.
        self.Interpretar.setShortcut("Ctrl+I")
        self.Ui_Grafica.GuardarAnimacion.setShortcut("Ctrl+S")
        self.Ui_Grafica.CurvasNivelAuto.setShortcut("Ctrl+A")
        self.Ui_Grafica.CurvasNivelEspecificas.setShortcut("Ctrl+E")
        self.Ui_Carga.label.setText(mensaje)
        QCoreApplication.processEvents()
        QtCore.QThread.msleep(500)
        self.VentanaCarga.close()
        if self.DimensionTemporalEntrada.isChecked() or (self.DimensionEspacialEntrada.value() == 3):
            # La desconexión de los botones de reproducción para evitar el envío doble de las señales se realizó de acuerdo con ingvar. (14 de octubre de 2017). Respuesta a la pregunta "When a QPushButton is clicked, it fires twice". stackoverflow. https://stackoverflow.com/a/46748321
            # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 3.0 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/3.0/
            try:
                self.Ui_Grafica.BotonPasoAtras.clicked.disconnect()
                self.Ui_Grafica.BotonReproduccionAtras.clicked.disconnect()
                self.Ui_Grafica.BotonReproduccionAdelante.clicked.disconnect()
                self.Ui_Grafica.BotonPausa.clicked.disconnect()
                self.Ui_Grafica.BotonPasoAdelante.clicked.disconnect()
                self.Ui_Grafica.deslizador.valueChanged.disconnect()
                self.Ui_Grafica.GuardarAnimacion.clicked.disconnect()
                self.Ui_Grafica.GraficarCurvasFija.clicked.disconnect()
            except:
                pass

            self.Ui_Grafica.BotonPasoAtras.clicked.connect(self.Ui_Grafica.Animacion.pasoAtras)
            self.Ui_Grafica.BotonReproduccionAtras.clicked.connect(self.Ui_Grafica.Animacion.reproduccionAtras)
            self.Ui_Grafica.BotonReproduccionAdelante.clicked.connect(self.Ui_Grafica.Animacion.reproduccionAdelante)
            self.Ui_Grafica.BotonPausa.clicked.connect(self.Ui_Grafica.Animacion.detener)
            self.Ui_Grafica.BotonPasoAdelante.clicked.connect(self.Ui_Grafica.Animacion.pasoAdelante)
            self.Ui_Grafica.deslizador.setMaximum(self.Ui_Grafica.Animacion.maximo-self.Ui_Grafica.Animacion.argumentos[0])
            self.Ui_Grafica.deslizador.valueChanged.connect(self.Ui_Grafica.Animacion.actualizarGrafica)
            self.Ui_Grafica.GuardarAnimacion.clicked.connect(self.guardarAnimacion)
            self.Ui_Grafica.GraficarCurvasFija.clicked.connect(self.visualizarCurvasNivel)
        self.Ui_Grafica.Animacion.iniciar()
        self.Ui_Grafica.MostrarSolucion.figura.canvas.draw_idle()


    def guardarAnimacion(self):
        """Ejecuta el trabajo de cambio de proyeccion entre visualizacion tridimensional y bidimensional o entre visualizacion unidimensional y bidimensional."""

        # Diseño de la ventana de carga.
        self.Ui_Carga.label.setText("Iniciando Guardado")
        self.Ui_Carga.animacion = QMovie(os.path.join(directorio_base, "Carga", "Guardando.gif"))
        self.Ui_Carga.animacion.setScaledSize(QSize(227,150))
        self.Ui_Carga.icono.setMovie(self.Ui_Carga.animacion)
        self.Ui_Carga.animacion.start()
        QCoreApplication.processEvents()

        # Deshabilita el botón de guardado.
        self.Ui_Grafica.GuardarAnimacion.setDisabled(True)
        self.Ui_Grafica.GuardarAnimacion.setStyleSheet("background-color : rgb(127,146,151); color: rgb(234,237,239);")
        self.Ui_Grafica.GuardarAnimacion.setText("Procesando")

        # Crea el lienzo sobre el que se graficaran los cuadros de la animación.
        self.Ui_Grafica.MostrarSolucion2 = Lienzo(self, ancho= 854, alto=480, dpi = 72)
        self.Ui_Grafica.MostrarSolucion2.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.Ui_Grafica.MostrarSolucion2.figura.set_visible(True)
        
        # Configuración y ejecución del trabajo de guardado de animaciones.
        trabajo = TrabajoGuardado(self.Ui_Grafica)
        trabajo.signals.finalizar_signal.connect(self.finalizarGuardado)
        trabajo.signals.avanzar_signal.connect(self.actualizarVentanaEmergente)
        trabajo.signals.error_signal.connect(self.mostrarError)  
        trabajo.autoDelete()
        self.VentanaCarga.show()
        self.threadpool.start(trabajo, 0)

    def finalizarGuardado(self, mensaje):
        """
        Actualiza la ventana de carga y después la cierra para indicar la finalización del guardado de la animación.

        Parámetros
        ----------
        **mensaje : string
            Mensaje a desplegar en la pantalla de carga.
        """

        self.Ui_Grafica.GuardarAnimacion.setDisabled(True)
        self.Ui_Grafica.GuardarAnimacion.setStyleSheet("background-color : rgb(127,146,151); color: rgb(234,237,239);")
        self.Ui_Grafica.GuardarAnimacion.setText("Iniciando guardado")
        QCoreApplication.processEvents()
        QtCore.QThread.msleep(500)
        
        self.Interpretar.setShortcut("Ctrl+I")
        self.Ui_Grafica.GuardarAnimacion.setShortcut("Ctrl+S")
        self.Ui_Grafica.CurvasNivelAuto.setShortcut("Ctrl+A")
        self.Ui_Grafica.CurvasNivelEspecificas.setShortcut("Ctrl+E")
        self.Ui_Carga.label.setText(mensaje)
        QCoreApplication.processEvents()
        QtCore.QThread.msleep(500)
        self.VentanaCarga.close()

        self.Ui_Grafica.GuardarAnimacion.setText("Guardando")
        QCoreApplication.processEvents()
        QtCore.QThread.msleep(500)

        self.Ui_Grafica.animacionGuardado.save("Solucion_{}.mov".format(self.Ui_Grafica.nombreArchivo), writer=self.Ui_Grafica.writer, dpi=72)
        QCoreApplication.processEvents()
        QtCore.QThread.msleep(500)

        # Finalización
        self.Ui_Grafica.animacionGuardado.pause()

        self.Ui_Grafica.GuardarAnimacion.setText("Guardado Finalizado")
        QCoreApplication.processEvents()
        QtCore.QThread.msleep(500)
        del self.Ui_Grafica.animacionGuardado

        # Graficación de las curvas de nivel para evitar su desaparación después del proceso de guardado
        self.Ui_Grafica.interpretacionCurvasNivel()

        # Habilita el botón de guardado.
        self.Ui_Grafica.centralwidget.setEnabled(True)
        self.Ui_Grafica.GuardarAnimacion.setEnabled(True)
        self.Ui_Grafica.GuardarAnimacion.setStyleSheet("background-color : rgb(11, 61, 98); color: rgb(246,247,247)")
        self.Ui_Grafica.GuardarAnimacion.setText(u"Guardar Animaci\u00f3n")
        QCoreApplication.processEvents()

    def visualizarSolucion(self):
        """Ejecuta el trabajo de visualización de la gráfica."""

        # Diseño de la ventana de carga.
        self.Ui_Carga.label.setText("Iniciando Graficacion")
        self.Ui_Carga.animacion = QMovie(os.path.join(directorio_base, "Carga", "GraficacionCarga.gif"))
        self.Ui_Carga.animacion.setScaledSize(QSize(227,150))
        self.Ui_Carga.icono.setMovie(self.Ui_Carga.animacion)
        QCoreApplication.processEvents()
        self.Ui_Carga.animacion.start()

        # Asignación de mapa de colores dependiendo del problema.
        if self.DimensionTemporalEntrada.isChecked():
            # La creación de mapas de colores personalizados se basa en matplotlib. (s. f.). Creating a colormap from a list of colors. matplotlib. https://matplotlib.org/stable/gallery/color/custom_cmap.html
            if len(self.Condiciones[-1]) == 2:
                # Si el problema es de segundo orden en el tiempo utilizamos un mapa de colores oscuro.
                self.Colormap = mpl.colormaps['cividis']
            else:
                # Si el problema es de primer orden en el tiempo utilizamos un mapa de colores que simule temperaturas.
                self.Colormap = LinearSegmentedColormap.from_list("", ["tab:blue", "cornflowerblue", "lightcoral", "red"], N=2**10)
        else:
            # Para cualquier otro problema utilizamos un mapa de colores predefinido.
            self.Colormap = mpl.colormaps['Spectral_r']
        
        # Configuración y ejecución del trabajo de visualización de la gráfica.
        trabajo = TrabajoVisualizacion(self.Ui_Grafica)
        trabajo.signals.finalizar_signal.connect(self.finalizarGraficacion)
        trabajo.signals.avanzar_signal.connect(self.actualizarVentanaEmergente)
        trabajo.signals.error_signal.connect(self.mostrarError)  
        trabajo.autoDelete()
        self.Ui_Grafica.transferirDatos(self.Solucion_funcion, self.Soluciones, self.NumeroTerminos, self.MatrizResultados, self.Dominios, self.Simbolos, self.Colormap, self.ProyeccionEntrada.isChecked(), self.SistemaCoordenadasEntrada.checkedButton().objectName(), self.NumeroEntradas.text(), self.Precision, self.CalidadEntrada.isChecked(), self.ParticionesDominios, self.dependencia, self.bidependencia, self.indicesdependencia, self.invertir, self.ValoresPropios)

        self.Ui_Grafica.CoordenadaFija.setText("{}".format(float(self.Dominios[0][0])))

        self.Ui_Grafica.pagina.loadFinished.connect(lambda: self.Ui_Grafica.despliegueCoeficiente_CambioExpresion(self.Ui_Grafica.Subproblema.value()))
        self.Ui_Grafica.Subproblema.valueChanged.connect(lambda: self.Ui_Grafica.despliegueCoeficiente_CambioExpresion(self.Ui_Grafica.Subproblema.value()))
        self.Ui_Grafica.ValorPropio1.valueChanged.connect(lambda: self.Ui_Grafica.despliegueCoeficiente_CambioValorPropio(self.Ui_Grafica.ValorPropio1.value(), self.Ui_Grafica.ValorPropio2.value(), self.Ui_Grafica.ValorPropio3.value()))
        self.Ui_Grafica.ValorPropio2.valueChanged.connect(lambda: self.Ui_Grafica.despliegueCoeficiente_CambioValorPropio(self.Ui_Grafica.ValorPropio1.value(), self.Ui_Grafica.ValorPropio2.value(), self.Ui_Grafica.ValorPropio3.value()))
        self.Ui_Grafica.ValorPropio3.valueChanged.connect(lambda: self.Ui_Grafica.despliegueCoeficiente_CambioValorPropio(self.Ui_Grafica.ValorPropio1.value(), self.Ui_Grafica.ValorPropio2.value(), self.Ui_Grafica.ValorPropio3.value()))

        self.VentanaCarga.show()
        self.threadpool.start(trabajo)

    def finalizarGraficacion(self, mensaje):
        """
        Actualiza la ventana de carga y abre la ventana de graficación para permitir la visualización de la gráfica.

        Parámetros
        ----------
        **mensaje** : string
            Mensaje a desplegar en la pantalla de carga.
        """

        self.Ui_Grafica.Animacion.iniciar()
        self.Ui_Grafica.MostrarSolucion.figura.canvas.draw_idle()
        self.Ui_Carga.label.setText(mensaje)
        QCoreApplication.processEvents()
        QtCore.QThread.msleep(500)
        self.Interpretar.setShortcut("Ctrl+I")
        if not ((self.DimensionEspacialEntrada.value() == 3 and (not self.ProyeccionEntrada.isChecked())) or (self.DimensionEspacialEntrada.value() == 1)):
            # Permite la visualización de curvas de nivel excepto en problemas de tres dimensiones espaciales y que no se encuentran proyectados bidimensionalmente.
            self.Ui_Grafica.CurvasNivelAuto.setCheckable(True)
            self.Ui_Grafica.CurvasNivelEspecificas.setCheckable(True)
        self.VentanaCarga.close()
        self.VentanaGrafica.show()
        self.Ui_Grafica.GuardarAnimacion.setShortcut("Ctrl+S")
        self.Ui_Grafica.CurvasNivelAuto.setShortcut("Ctrl+A")
        self.Ui_Grafica.CurvasNivelEspecificas.setShortcut("Ctrl+E")
        if self.DimensionTemporalEntrada.isChecked() or (self.DimensionEspacialEntrada.value() == 3):
            # La desconexión de los botones de reproducción para evitar el envío doble de las señales se realizó de acuerdo con ingvar. (14 de octubre de 2017). Respuesta a la pregunta "When a QPushButton is clicked, it fires twice". stackoverflow. https://stackoverflow.com/a/46748321
            # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 3.0 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/3.0/
            try:
                self.Ui_Grafica.BotonPasoAtras.clicked.disconnect()
                self.Ui_Grafica.BotonReproduccionAtras.clicked.disconnect()
                self.Ui_Grafica.BotonReproduccionAdelante.clicked.disconnect()
                self.Ui_Grafica.BotonPausa.clicked.disconnect()
                self.Ui_Grafica.BotonPasoAdelante.clicked.disconnect()
                self.Ui_Grafica.deslizador.valueChanged.disconnect()
                self.Ui_Grafica.GuardarAnimacion.clicked.disconnect()
                self.Ui_Grafica.GraficarCurvasFija.clicked.disconnect()
            except:
                pass
            
            self.Ui_Grafica.BotonPasoAtras.clicked.connect(self.Ui_Grafica.Animacion.pasoAtras)
            self.Ui_Grafica.BotonReproduccionAtras.clicked.connect(self.Ui_Grafica.Animacion.reproduccionAtras)
            self.Ui_Grafica.BotonReproduccionAdelante.clicked.connect(self.Ui_Grafica.Animacion.reproduccionAdelante)
            self.Ui_Grafica.BotonPausa.clicked.connect(self.Ui_Grafica.Animacion.detener)
            self.Ui_Grafica.BotonPasoAdelante.clicked.connect(self.Ui_Grafica.Animacion.pasoAdelante)
            self.Ui_Grafica.deslizador.setMaximum(self.Ui_Grafica.Animacion.maximo-self.Ui_Grafica.Animacion.argumentos[0])
            self.Ui_Grafica.deslizador.valueChanged.connect(self.Ui_Grafica.Animacion.actualizarGrafica)
            self.Ui_Grafica.GuardarAnimacion.clicked.connect(self.guardarAnimacion)
            self.Ui_Grafica.GraficarCurvasFija.clicked.connect(self.visualizarCurvasNivel)

class PantallaPrincipal(QMainWindow):
    """
    Clase utilizada para redefinir los procesos a seguir cuando se intente cerrar la ventana principal.
    """

    # La creación de esta clase para redefinir los eventos necesarios para cerrar la ventana principal se basa en BoshWash. (17 de marzo de 2014). Respuesta a la pregunta "PyQt's QMainWindow closeEvent is never called". stackoverflow. https://stackoverflow.com/a/22460392
    # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 4.0 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/4.0/

    def __init__(self):
        super(self.__class__, self).__init__()

    def closeEvent(self, event):
        """
        Muestra una ventana emergente para confirmar el cierre de la aplicación. 
        En caso afirmativo, procede a hacer limpieza de los archivos creados para la interpretación y cierra todas las ventanas; en caso contrario, cierra la ventana emergente para continuar con la ejecución de la aplicación.
        """
        
        icono = QIcon()
        icono.addPixmap(QPixmap(os.path.join(directorio_base, "Iconos", "IconoGraPhEr.png")), QIcon.Normal, QIcon.Off)

        EmergenteVentanaPrincipal = QtWidgets.QMessageBox()
        # Diseño de la ventana emergente
        # El diseño está basado en lo expuesto en Pantaleone, D. (09 de marzo de 2016). Respuesta a la pregunta "QMessageBox change text of standard button". stackoverflow. https://stackoverflow.com/a/35889474
        # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 4.0 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/4.0/
        EmergenteVentanaPrincipal.setStyleSheet("color: rgb(246, 246, 247) ; background-color: rgb(11, 68, 98)")
        EmergenteVentanaPrincipal.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        boton1 = EmergenteVentanaPrincipal.button(QtWidgets.QMessageBox.Yes)
        boton1.setText("Sí")
        boton1.setStyleSheet("background-color: rgb(246, 246, 247) ; color: rgb(11, 68, 98)")
        boton2 = EmergenteVentanaPrincipal.button(QtWidgets.QMessageBox.No)
        boton2.setStyleSheet("background-color: rgb(246, 246, 247) ; color: rgb(11, 68, 98)")
        EmergenteVentanaPrincipal.setWindowIcon(icono)
        EmergenteVentanaPrincipal.setWindowModality(Qt.WindowModal)
        EmergenteVentanaPrincipal.setWindowTitle("¡Atención!")
        EmergenteVentanaPrincipal.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowType.Dialog)
        EmergenteVentanaPrincipal.setIcon(QMessageBox.Question)
        EmergenteVentanaPrincipal.setText("<b>¿Desea cerrar la aplicación?</b><br><br> Toda la información calculada será eliminada.")
        EmergenteVentanaPrincipal.exec_()
        event.ignore()

        if EmergenteVentanaPrincipal.clickedButton() == boton1:
            borrardatosaplicacion(ui, True)
            event.accept()

class PantallaGraficacion(QMainWindow):
    """
    Clase utilizada para redefinir los procesos a seguir cuando se intente cerrar la ventana de graficación.
    """

    # La creación de esta clase para redefinir los eventos necesarios para cerrar la ventana de graficación se basa en BoshWash. (17 de marzo de 2014). Respuesta a la pregunta "PyQt's QMainWindow closeEvent is never called". stackoverflow. https://stackoverflow.com/a/22460392
    # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 4.0 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/4.0/

    def __init__(self, ui_informacion):
        super(self.__class__, self).__init__()
        self.ui = ui_informacion
        self.EmergenteVentanaGraficacion = QtWidgets.QMessageBox()

    def closeEvent(self, event):
        """
        Muestra una ventana emergente para confirmar el cierre de la ventana de graficación. 
        En caso afirmativo, procede a cerrar la ventana y ventanas asociadas (etiquetas y errores); en caso contrario, cierra la ventana emergente para continuar con la visualización de la gráfica.

        
        """

        if not self.ui.cierretotal:
            icono = QIcon()
            icono.addPixmap(QPixmap(os.path.join(directorio_base, "Iconos", "IconoGraPhEr.png")), QIcon.Normal, QIcon.Off)

            self.EmergenteVentanaGraficacion = QtWidgets.QMessageBox()
            # Diseño de la ventana emergente
            # El diseño está basado en lo expuesto en Pantaleone, D. (09 de marzo de 2016). Respuesta a la pregunta "QMessageBox change text of standard button". stackoverflow. https://stackoverflow.com/a/35889474
            # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 4.0 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/4.0/
            self.EmergenteVentanaGraficacion.setStyleSheet("color: rgb(246, 246, 247) ; background-color: rgb(11, 68, 98)")
            self.EmergenteVentanaGraficacion.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            boton1 = self.EmergenteVentanaGraficacion.button(QtWidgets.QMessageBox.Yes)
            boton1.setText("Sí")
            boton1.setStyleSheet("background-color: rgb(246, 246, 247) ; color: rgb(11, 68, 98)")
            boton2 = self.EmergenteVentanaGraficacion.button(QtWidgets.QMessageBox.No)
            boton2.setStyleSheet("background-color: rgb(246, 246, 247) ; color: rgb(11, 68, 98)")
            self.EmergenteVentanaGraficacion.setWindowIcon(icono)
            self.EmergenteVentanaGraficacion.setWindowModality(Qt.WindowModal)
            self.EmergenteVentanaGraficacion.setWindowTitle("¡Atención!")
            self.EmergenteVentanaGraficacion.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowType.Dialog)
            self.EmergenteVentanaGraficacion.setIcon(QMessageBox.Question)
            self.EmergenteVentanaGraficacion.setText("<b>¿Desea cerrar la ventana de graficación? </b><br><br> Se restaurará la gráfica a su versión inicial.")
            self.EmergenteVentanaGraficacion.exec_()
            event.ignore()

            if self.EmergenteVentanaGraficacion.clickedButton() == boton1:
                # Configuración de la ventana de graficación a su estado inicial.
                self.ui.VentanaGrafica.setHidden(True)
                self.ui.Ui_Grafica.ProyeccionEntrada.setChecked(False)
                self.ui.Ui_Grafica.CurvasNivelAuto.setCheckable(False)
                self.ui.Ui_Grafica.CurvasNivelEspecificas.setCheckable(False)

                # Cierre de ventana de leyendas y/o ventanas de errores.
                if self.ui.Ui_Grafica.etiquetas:
                    self.ui.Ui_Grafica.VentanaEtiquetas.close()
                if self.ui.error:
                    self.ui.MensajeError.close()
                event.accept()

def borrardatosaplicacion(ui_informacion, cierretotal):
    """Elimina archivos creados para la visualización de la interpretación y cierra todas las ventanas de la aplicación."""

    if os.path.exists('Entrada.html'):
        os.remove('Entrada.html')
    if os.path.exists('js'):
        shutil.rmtree('js')
    if os.path.exists('.paux'):
        os.remove('.paux')
    if os.path.exists('symbol-defs.svg'):
        os.remove('symbol-defs.svg')

    if cierretotal:
        # Cierre de todas las ventanas.
        if ui_informacion.error:
            ui_informacion.MensajeError.close()
        ui_informacion.Ui_Grafica.VentanaEtiquetas.close()
        ui_informacion.ventanaVisualizacionInterpretacion.close()
        if ui_informacion.VentanaGrafica.isHidden() != True:
            ui_informacion.cierretotal = True
            ui_informacion.VentanaGrafica.setHidden(True)
            ui_informacion.VentanaGrafica.EmergenteVentanaGraficacion.close()
        print("Thank you for using this app. Share it if you liked it.")

# Ejecución de la aplicación
if __name__ == "__main__":
    import sys

    print("GraPhEr - Ecuaciones Diferenciales Parciales Separables  Copyright (C) 2024  Luis Enrique Nava Garcia \n This program comes with ABSOLUTELY NO WARRANTY; for details see the COPYING file. \n This is free software, and you are welcome to redistribute it \n under certain conditions; see the COPYING file for details.")

    app = QApplication(sys.argv)
    VentanaInicial = PantallaPrincipal()
    ui = Ui_GraficadoraVentanaPrincipal(VentanaInicial)
    ret = app.exec_()

    # Limpieza archivos creados para la interpretaccion y cierre de ventanas secundarias 
    # en caso de un cierre inesperado de la aplicación.
    atexit.register(lambda: borrardatosaplicacion(ui, True))
    
    sys.exit(ret) 
