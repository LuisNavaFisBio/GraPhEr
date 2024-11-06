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

from fractions import Fraction
from matplotlib import cm
from matplotlib.animation import FuncAnimation, FFMpegFileWriter, FFMpegWriter, PillowWriter
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from plasTeX.TeX import TeX
from plasTeX.Renderers.HTML5 import Renderer
from PyQt5.QtCore import QCoreApplication, QMetaObject, QSize, Qt, QUrl, pyqtSignal, QObject, QThreadPool
from PyQt5.QtGui import QFont, QPixmap, QIcon, QMovie
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from sympy import integrate, latex, parsing, pi, preview, symbols, core
from sympy.abc import j, m, n, r, s, x, y, z, t, rho, theta, phi, lamda
import atexit, os, shutil, matplotlib.widgets, mpl_toolkits.axes_grid1
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipy as sc
import sympy as sp
import sys
matplotlib.use('Qt5Agg')

# Todas y cada una de las clases de este archivo fueron tomadas y modificadas de ImportanceOfBeingErnest. (02 de abril de 2020). Respuesta a la pregunta "Animated interactive plot using matplotlib". stackoverflow. https://stackoverflow.com/a/46327978
# La reproducción de dicho código está licenciada bajo la licencia CC BY-SA 4.0 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/4.0/
# La modificación consiste en la modificación de algunas de las funciones de la clase y/o la apariencia, además de reemplazar los botónes de reproducción y el slider por widgets de PyQt5.

class ReproductorGeneral(FuncAnimation):
    """
    Clase que contiene las instrucciones para el proceso de reproducción de las animaciones para problemas que no sean proyecciones de una dimensión espacial y dependencia temporal o problemas con dos dimensiones espaciales sin dependencia temporal.
    """

    def __init__(self, canva, func, fargs, interval, maximo = 10, curvas_nivel = False, funcion_curvas = None, sistema_coordenadas = "", deslizador_navegacion = None):
        """
        Inicializa la animación y sus herramientas.
        
        Parámetros
        ----------
        **Nota: los parámetros func, fargs e interval son los mismos que se especifican en la documentación de la clase FuncAnimation de Matplotlib.**

        canva: Matplotlib.figure
            Figura de Matplotlib que contiene la gráfica.

        maximo: entero
            Número de cuadros totales de la animación.

        curvas_nivel: bool
            Determina si se está guardando la visualización con curvas de nivel.

        funcion_curvas: función de Python
            Función que grafica las curvas de nivel.

        sistema_coordenadas: string
            Sistema de coordenadas del problema.
        """

        # Configuración de las variables necesarias.
        self.cuadro = -2
        self.canva = canva
        self.funcionActualizadora = func
        self.argumentos = fargs
        self.fps = 1000/interval
        self.curvas_nivel = curvas_nivel
        self.funcion_curvas = funcion_curvas
        self.interval = interval
        self.maximo = maximo
        self.coordenadas = sistema_coordenadas
        self.deslizador = deslizador_navegacion
        self.barracolor = False

    def iniciar(self):
        """Inicia la creación e interacción de la animación."""

        self.cuadro = -2
        self.proceso = True
        self.adelante = True 
        FuncAnimation.__init__(self, self.canva.figura, self.actualizar, frames = self.contador(), interval = self.interval, repeat = False, save_count = self.maximo) 

    def contador(self):
        """Proporciona el número del siguiente cuadro."""

        while self.proceso:
            # Aumentar o disminuir el número de acuerdo con la manera de reproducción (normal o hacia atrás).
            self.cuadro = self.cuadro + self.adelante - (not self.adelante)
            if self.adelante:
                if self.cuadro > self.maximo-1:
                    # Detener en el último cuadro.
                    self.detener()
                    yield self.cuadro
                elif self.cuadro >= -1 and self.cuadro <= self.maximo:
                    yield self.cuadro
            else:
                if self.cuadro <= self.argumentos[0]:
                    # Detener en el primer cuadro del deslizador.
                    self.detener()
                    yield self.cuadro
                elif self.cuadro > self.argumentos[0] and self.cuadro <= self.maximo:
                    yield self.cuadro


    def empezar(self):
        """Comienza la reproducción."""

        self.proceso = True
        self.event_source.start()

    def detener(self, event=None):
        """Detiene la reproducción."""

        self.proceso = False
        self.event_source.stop()

    def reproduccionAdelante(self, event=None):
        """Inicia la reproducción de la animación de manera normal (inicio-fin)."""

        self.adelante = True
        self.empezar()     

    def reproduccionAtras(self, event=None):
        """Inicia la reproducción de la animación en reversa (fin-inicio)."""

        if not (self.cuadro < self.argumentos[0]+1):
            # Inicio de la reproducción siempre y cuando el cuadro actual no sea el primer cuadro de la reproducción.
            self.adelante = False
            self.empezar()
            

    def pasoAdelante(self, event=None):
        """Avanza la animación al siguiente cuadro."""

        self.adelante = True
        self.cuadroPorCuadro()

    def pasoAtras(self, event=None):
        """Retrocede la animación al cuadro previo."""

        self.adelante = False
        self.cuadroPorCuadro()

    def cuadroPorCuadro(self):
        """Actualiza la animación para mostrar el siguiente cuadro o el cuadro previo según sea el caso."""

        if self.argumentos[0] < self.cuadro <= self.maximo and not self.adelante:
            # Disminuir el número de cuadro si se quiere el cuadro previo.
            self.cuadro -= 1
        elif self.argumentos[0] <= self.cuadro < self.maximo and self.adelante:
            # Aumentar el número de cuadro si se quiere el siguiente cuadro.
            self.cuadro += 1
        print(self.cuadro)
        # Actualizar el valor del deslizador.
        self.deslizador.setValue(self.cuadro-self.argumentos[0])
        self.canva.figura.canvas.draw_idle()

    def actualizarGrafica(self, cuadro):
        """
        Actualiza la gráfica para mostrar el cuadro requerido dentro de la animación (excepto los cuadros de entrada de gráfica).
        
        Parámetros
        ----------
        cuadro: entero
            Número del cuadro requerido, coincide con el valor actual del deslizador.
        """
        
        # Actualización del número de cuadro.
        self.cuadro = int(cuadro)+self.argumentos[0]
        # Actualización de la gráfica.
        self.funcionActualizadora(self.cuadro, *self.argumentos[0:-2])
        if self.curvas_nivel == True:
            # Graficación de curvas de nivel.
            self.funcion_curvas()
        self.canva.figura.canvas.draw_idle()    

    def actualizar(self, indice):
        """
        Actualiza la gráfica o el valor del deslizador para actualizar la gráfica.
        
        Parámetros
        ----------
        indice: entero
            Determina el número del cuadro requerido.
        """

        print(indice)
        if (indice > self.argumentos[0]) and (indice <= self.maximo):
            # Actualización de la gráfica.
            self.deslizador.setValue(indice-self.argumentos[0])
        elif indice == self.argumentos[0]:
            # Último cuadro de la introducción de la gráfica.
            if self.deslizador.value() != 0:
                self.deslizador.setValue(0)
            else:
                self.actualizarGrafica(0)
            self.detener()

            if not self.barracolor:

                # Visualización de la barra de color.
                colorbarax = self.canva.figura.add_axes([0.85, 0.15, 0.04, 0.8])

                # La creación de la barra de color se basa en mfitzp. (26 de febrero de 2015). Respuesta a la pregunta "Map values to colors in matplotlib". stackoverflow. https://stackoverflow.com/a/28752903
                # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 3.0 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/3.0/
                plt.colorbar(cm.ScalarMappable(norm=plt.Normalize(-self.argumentos[-3], self.argumentos[-3]), cmap=self.argumentos[-2]), colorbarax)

                # Activación del botón de guardado.
                self.argumentos[-1].setEnabled(True)
                self.argumentos[-1].setStyleSheet(u"color: rgb(246, 247, 247); background-color: rgb(11, 61, 98);")

                self.barracolor = True

        else:
            # Introducción de la gráfica.
            self.funcionActualizadora(indice, *self.argumentos[0:-2])

            # Eliminación de cualquier gráfica en el lienzo.
            try:
                if self.proyeccion:
                    self.canva.axes.proyeccion.remove()
                    if len(self.canva.figura.axes) > 2:
                        self.canva.axes2.proyeccion.remove()
                else:
                    self.canva.axes.superficie.remove()
            except:
                pass
        
        
        # Graficación de la cuadrícula.
        if len(self.canva.figura.axes) > 2:
            self.canva.axes.grid(True, lw = 0.2)
            self.canva.axes2.grid(True, lw = 0.2)
        else:
            self.canva.axes.grid(True, lw = 0.2)

class Graficacion2D_NoTemporal(FuncAnimation):
    """
    Clase que contiene las instrucciones para el proceso de reproducción de las animaciones para problemas con dos dimensiones espaciales sin dependencia temporal.
    """

    def __init__(self, canva, func, fargs, maximo, interval, curvas_nivel = False, funcion_curvas = None):
        """
        Inicializa la animación y sus herramientas.
        
        Parámetros
        ----------
        **Nota: los parámetros func, fargs e interval son los mismos que se especifican en la documentación de la clase FuncAnimation de Matplotlib.**

        canva: Matplotlib.figure
            Figura de Matplotlib que contiene la gráfica.

        maximo: entero
            Número de cuadros totales de la animación.

        curvas_nivel: bool
            Determina si se está guardando la visualización con curvas de nivel.

        funcion_curvas: función de Python
            Función que grafica las curvas de nivel.
        """

        self.cuadro = -2        
        self.canva = canva
        self.funcionActualizadora = func
        self.argumentos = fargs
        self.fps = 1000/interval
        self.curvas_nivel = curvas_nivel
        self.funcion_curvas = funcion_curvas
        self.interval = interval
        self.maximo = maximo

    def iniciar(self):
        """Inicia la creación e interacción de la animación."""

        self.proceso = True
        self.adelante = True 
        FuncAnimation.__init__(self, self.canva.figura, self.actualizar, frames=self.contador(), interval=self.interval, repeat=False, save_count=self.maximo) 

    def contador(self):
        """Proporciona el número del siguiente cuadro."""

        while self.proceso:
            # Aumentar o disminuir el número de acuerdo con la manera de reproducción (normal o hacia atrás).
            self.cuadro = self.cuadro+self.adelante-(not self.adelante)
            if self.adelante:
                if self.cuadro > self.maximo-1:
                    # Detener en el último cuadro.
                    self.detener()
                    yield self.cuadro
                elif self.cuadro >= -1 and self.cuadro <= self.maximo:
                    yield self.cuadro
            else:
                if self.cuadro < self.argumentos[0]+1:
                    # Detener en el primer cuadro del deslizador.
                    self.detener()
                    yield self.cuadro
                elif self.cuadro >= self.argumentos[0]+1 and self.cuadro <= self.maximo:
                    yield self.cuadro

    def empezar(self):
        """Comienza la reproducción."""

        self.proceso = True
        self.event_source.start()

    def detener(self, event=None):
        """Detiene la reproducción."""
        
        self.proceso = False
        self.event_source.stop()

    def actualizar(self, indice):
        """
        Actualiza la gráfica o el valor del deslizador para actualizar la gráfica.
        
        Parámetros
        ----------
        indice: entero
            Determina el número del cuadro requerido.
        """

        print(indice)

        if indice == self.argumentos[0]+1:
            # Último cuadro de la introducción de la gráfica.
            self.funcionActualizadora(self.cuadro, *self.argumentos[0:-2])
            self.detener()

            # Visualización de la barra de color.
            colorbarax = self.canva.figura.add_axes([0.85, 0.15, 0.04, 0.8])
            # La creación de la barra de color se basa en mfitzp. (26 de febrero de 2015). Respuesta a la pregunta "Map values to colors in matplotlib". stackoverflow. https://stackoverflow.com/a/28752903
            # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 3.0 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/3.0/
            plt.colorbar(cm.ScalarMappable(norm=plt.Normalize(-self.argumentos[-3], self.argumentos[-3]), cmap = self.argumentos[-2]), colorbarax)

            # Activación del botón de guardado.
            self.argumentos[-1].setEnabled(True)
            self.argumentos[-1].setStyleSheet(u"color: rgb(246, 247, 247); background-color: rgb(11, 61, 98);")

            # Graficación de las curvas de nivel.
            if self.curvas_nivel:
                self.funcion_curvas()

            # Graficación de la cuadrícula.
            self.canva.axes.grid(True, lw = 0.2)
        else:
            # Introducción de la gráfica.
            self.funcionActualizadora(self.cuadro, *self.argumentos[0:-2])
