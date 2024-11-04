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

from fractions import Fraction
from matplotlib.animation import FuncAnimation, FFMpegFileWriter
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.collections import LineCollection
from plasTeX.TeX import TeX
from plasTeX.Renderers.HTML5 import Renderer
from PyQt5.QtCore import QCoreApplication, QMetaObject, QSize, Qt, QUrl, QRect, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QGuiApplication, QIcon, QMovie
from PyQt5.QtWidgets import *
from PyQt5 import QtWebEngineWidgets, QtCore, QtGui, QtWidgets
from string import ascii_uppercase, ascii_lowercase
from sympy import integrate, latex, parsing, pi, preview, symbols, Symbol, simplify, I, cos
from sympy.abc import j, l, m, n, r, s, x, y, z, t, rho, theta, phi
from sympy.functions.special import *
from threading import Timer
import atexit, matplotlib, os, shutil, matplotlib.widgets, mpl_toolkits.axes_grid1, sys, time, traceback
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipy as sc
import sympy as sp
matplotlib.use('Qt5Agg')

# La configuracion de las clases de los trabajos y la configuración de las señales de comunicación fue tomada y modificada de S. Nick. (13 de agosto de 2020). Respuesta a la pregunta "How to display a loading animated gif while a code is executing in backend of my Python Qt5 UI?". stackoverflow. https://stackoverflow.com/a/63395218
# El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 4.0 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/4.0/

class Inicializacion(QtCore.QRunnable):
    """Ejecutable para realizar un tiempo de carga de la aplicación al iniciarse."""

    def __init__(self):
        """Definicion de la información a utilizar y las señales necesarias para la comunicación."""

        super(self.__class__, self).__init__()
        self.signals = Indicadores()

    @QtCore.pyqtSlot()    
    def run(self):
        QtCore.QThread.msleep(5000)
        self.signals.finalizar_signal.emit("Aplicación Lista")

class TrabajoInterpretacion(QtCore.QRunnable):
    """Ejecutable para realizar el procesamiento en paralelo de la interpretación de la entrada del usuario. 
    
    *Nota: Varias líneas de esta clase solo cumplen la función de crear la tabla para desplegar la información introducida por el usuario en una página HTML, por lo que se puede prescindir de ellas, en caso de alguna modificación del código, sin afectar su funcionamiento. Todas estás líneas tendrán el comentario # Tabla.*"""

    def __init__(self, ui_informacion, widget):
        """Definicion de la información a utilizar y las señales necesarias para la comunicación."""
        super(self.__class__, self).__init__()
        self.ui = ui_informacion
        self.widget = widget
        self.signals = Indicadores()

    def envioActualizacion(self, mensaje):
        """
        Envía el mensaje a la ventana de carga para informar el punto del trabajo que se está realizando.
        
        Parámetros
        ----------
        mensaje : string
            Mensaje a colocar en la ventana de carga.
        """

        self.signals.avanzar_signal.emit(mensaje)
        QCoreApplication.processEvents()
        QtCore.QThread.msleep(500)

    @QtCore.pyqtSlot()
    def run(self):
        # Deshabilitacion de la pantalla principal mientras se realiza la interpretación.
        self.ui.centralwidget.setDisabled(True)
        self.ui.Interpretar.setDisabled(True)
        self.ui.Interpretar.setStyleSheet("background-color : rgb(127,146,151); color: rgb(234,237,239);")
        self.ui.Visualizar.setDisabled(True)
        self.ui.Visualizar.setStyleSheet("background-color : rgb(127,146,151); color: rgb(234,237,239);")
        self.ui.Limpiar.setDisabled(True)
        self.ui.Limpiar.setStyleSheet("background-color : rgb(127,146,151); color: rgb(234,237,239);")
        try: 
            # Actualiza el botón de interpretar para informar que sea realizado una interpretación previa con éxito.
            self.ui.Interpretar.setText("Actualizar")
            self.ui.Interpretar.setShortcut("Ctrl + I")

            if self.ui.entradaresuelta == True:
                # En caso de necesitar actualizar la entrada se elimina la información anterior.
                self.ui.entradaresuelta = False
                self.ui.borrardatosaplicacion(self.ui, False)

            self.envioActualizacion("Leyendo Entrada")

            if (not self.ui.DimensionTemporalEntrada.isChecked()) and (self.ui.DimensionEspacialEntrada.value() == 1):
                # Si el problema solo tiene una dimensión, se genera el error de Dimension puesto que en tal caso no es un problema de ecuaciones diferenciales parciales.
                raise DimensionError
            
            # Lectura de entradas de dominio y condiciones de frontera o iniciales.
            DE1 = self.ui.DominioEspacial1Entrada.text().replace(" ","").replace("PI","pi")
            DE2 = self.ui.DominioEspacial2Entrada.text().replace(" ","").replace("PI","pi")
            DE3 = self.ui.DominioEspacial3Entrada.text().replace(" ","").replace("PI","pi")
            DT = self.ui.DominioTemporalEntrada.text().replace(" ","").replace("PI","pi")
            CE = self.ui.CondicionesEntrada.text().replace(" ","").replace("PI","pi")
            
            if (DE1 == "") or ((self.ui.DimensionEspacialEntrada.value() > 1) and (DE2 == "")) or ((self.ui.DimensionEspacialEntrada.value() > 2) and (DE3 == "")) or ((self.ui.DimensionTemporalEntrada.isChecked()) and (DT == "")) or (self.ui.PrecisionEntrada.text() == ""):
                # Si alguna de las entradas de campo de dominio, condiciones o precisión está vacía se crea el error EntradaVacia
                raise EntradaVaciaError

            VPE, NTE, FPE, FEE, FTE, CoefE = {}, {}, {}, {}, {}, {}
            for indice in range(int(self.ui.NumeroEntradas.text())):
                if (self.ui.ValoresPropiosEntrada['{}'.format(indice)].text() == "") or (self.ui.NumeroTerminosEntrada['{}'.format(indice)].text() == "")  or (self.ui.FuncionesPesoEntrada['{}'.format(indice)].text() == "")  or (self.ui.FuncionesEspacialesEntrada['{}'.format(indice)].text() == "")  or (self.ui.DimensionTemporalEntrada.isChecked() and (self.ui.FuncionesTemporalesEntrada['{}'.format(indice)].text() == ""))  or (self.ui.CoeficientesEntrada['{}'.format(indice)].text() == ""):
                    # Si alguna de las entradas de campo visibles en el cuadro de subproblemas está vacía se crea el error EntradaVacia.
                    raise EntradaVaciaError
                else:
                    # Lectura de la entrada y remoción de espacios de más e intercambio de PI por pi (esto último asegura que el usuario pueda ingresar PI o pi de manera indistinta).
                    VPE['{}'.format(indice)] = self.ui.ValoresPropiosEntrada['{}'.format(indice)].text().replace(" ","").replace("PI","pi")
                    NTE['{}'.format(indice)] = self.ui.NumeroTerminosEntrada['{}'.format(indice)].text().replace(" ","").replace("PI","pi")
                    FPE['{}'.format(indice)] = self.ui.FuncionesPesoEntrada['{}'.format(indice)].text().replace(" ","").replace("PI","pi")
                    FEE['{}'.format(indice)] = self.ui.FuncionesEspacialesEntrada['{}'.format(indice)].text().replace(" ","").replace("PI","pi")
                    FTE['{}'.format(indice)] = self.ui.FuncionesTemporalesEntrada['{}'.format(indice)].text().replace(" ","").replace("PI","pi")
                    CoefE['{}'.format(indice)] = self.ui.CoeficientesEntrada['{}'.format(indice)].text().replace(" ","").replace("PI","pi")

                if ((";" in VPE['{}'.format(indice)]) and (not ";" in NTE['{}'.format(indice)])) or ((not ";" in VPE['{}'.format(indice)]) and (";" in NTE['{}'.format(indice)])):
                    # Si se especifican dos ecuaciones o expresiones para valores propios y solo se especifica un número de términos para una de ellas, o viceversa, se produce el error ExcesoEntrada.
                    raise ExcesoEntradaError
            
            if self.ui.DimensionTemporalEntrada.isChecked(): # Tabla.
                self.ui.Entrada = self.ui.Entrada.replace("u(\\mathbf{x})", "u(\\mathbf{x},\\hspace{0.1cm} t)") # Tabla.

            # Creación de listas bidimensionales para guardar las interpretaciones de las entradas de cada subproblema.
            self.ui.ValoresPropios = [[] for x in range(int(self.ui.NumeroEntradas.text()))]
            self.ui.NumeroTerminos = [NTE["{}".format(x)].split(";") for x in range(int(self.ui.NumeroEntradas.text()))]
            self.ui.FuncionesPeso = [parsing.parse_expr(FPE["{}".format(x)]) for x in range(int(self.ui.NumeroEntradas.text()))]
            self.ui.Coeficientes = [[] for x in range(int(self.ui.NumeroEntradas.text()))]      
            self.ui.FuncionesEspaciales = [[] for x in range(int(self.ui.NumeroEntradas.text()))]
            if self.ui.DimensionTemporalEntrada.isChecked():
                # Cuando el problema tenga dependencia temporal.
                self.ui.FuncionesTemporales = [[] for x in range(int(self.ui.NumeroEntradas.text()))]      
            
            solucion_string = "" # Tabla.
            valorespropios_string = "\\quad \\left\\lvert \\quad " # Tabla.
            coeficientes_string = "\\quad \\left\\lvert \\quad " # Tabla.
            funcionespeso_string = "\\quad \\left\\lvert \\quad " # Tabla.
            for indice in range(int(self.ui.NumeroEntradas.text())):
                funcionespeso_string = funcionespeso_string + "w_{}=".format(indice + 1) + latex(self.ui.FuncionesPeso[indice])  + "\\quad \\right\\rvert \\left. \\quad " # Tabla.

            self.envioActualizacion("Interpretando Dominio")

            # Interpretación de las entradas de campo de los dominios.
            self.ui.Dominios = []
            for dominio in [DE1, DE2, DE3]:
                if dominio != "":
                    if ":" in dominio:
                        self.ui.Dominios.append(dominio)
                    else:
                        # En caso de que alguna de las coordenadas espaciales no tenga definido alguno de los extremos se crea el error ExtremoFaltante.
                        raise ExtremoFaltanteError
            if self.ui.DimensionTemporalEntrada.isChecked():
                if not ":" in DT:
                    self.ui.Dominios.append(DT)
                else:
                    raise ExcesoEntradaError
            for indice1 in range(len(self.ui.Dominios)):
                self.ui.Dominios[indice1] = [parsing.parse_expr(expresion) for expresion in self.ui.Dominios[indice1].split(":")]   

            for indice in range(int(self.ui.NumeroEntradas.text())):             

                self.envioActualizacion("Interpretando Coeficientes ({0}/{1})".format(indice + 1, int(self.ui.NumeroEntradas.text())))

                # Interpretación de los coeficientes de cada subsolución.
                integral_string_i = ""
                if self.ui.FuncionesPeso[indice] != "1":
                    integral_string_f = "*" + str(self.ui.FuncionesPeso[indice])
                else:
                    integral_string_f = ""
                indice_ayuda = 0
                # En caso de que los coeficientes estén descritos en términos de integrales de las funciones propias de cada coordenada se crean las expresiones completas.
                if self.ui.SistemaCoordenadasEntrada.checkedButton().objectName() == "Cartesianas":
                    for simbolo in [",x", ",y", ",z"]:
                        if simbolo in CoefE["{}".format(indice)]:
                            CoefE["{}".format(indice)] = CoefE["{}".format(indice)].replace(simbolo,"")
                            integral_string_i = integral_string_i + "Integral("
                            integral_string_f = integral_string_f + ", ({0}, {1}, {2}))".format(simbolo.replace(",",""), self.ui.Dominios[indice_ayuda][0], self.ui.Dominios[indice_ayuda][1])
                        indice_ayuda += 1
                elif self.ui.SistemaCoordenadasEntrada.checkedButton().objectName() == "Cilíndricas / Polares":
                    for simbolo in [",", ",phi", ",z"]:
                        if simbolo in CoefE["{}".format(indice)]:
                            CoefE["{}".format(indice)] = CoefE["{}".format(indice)].replace(simbolo,"")
                            integral_string_i = integral_string_i + "Integral("
                            integral_string_f = integral_string_f + ", ({0}, {1}, {2}))".format(simbolo.replace(",",""), self.ui.Dominios[indice_ayuda][0], self.ui.Dominios[indice_ayuda][1])
                        indice_ayuda += 1
                elif self.ui.SistemaCoordenadasEntrada.checkedButton().objectName() == "Esféricas":
                    for simbolo in [",", [",theta", ",ct"], ",phi",]:
                        if type(simbolo) == list:
                            if simbolo[0] in CoefE["{}".format(indice)]:
                                # En caso de que la integral sea respecto a theta.
                                CoefE["{}".format(indice)] = CoefE["{}".format(indice)].replace(simbolo[0],"")
                                integral_string_i = integral_string_i + "Integral("
                                integral_string_f = integral_string_f + ", ({0}, {1}, {2}))".format(simbolo[0].replace(",",""), self.ui.Dominios[indice_ayuda][0], self.ui.Dominios[indice_ayuda][1])
                            elif simbolo[1] in CoefE["{}".format(indice)]:
                                # En caso de que la integral sea respecto a s=cos(theta)
                                CoefE["{}".format(indice)] = CoefE["{}".format(indice)].replace(simbolo[1],"")
                                integral_string_i = integral_string_i + "Integral("
                                if Fraction(np.cos(float(self.ui.Dominios[indice_ayuda][1]))).limit_denominator().denominator == 1:
                                    limite_inferior = int(np.cos(float(self.ui.Dominios[indice_ayuda][1])))
                                else:
                                    limite_inferior = np.cos(float(self.ui.Dominios[indice_ayuda][1]))
                                if Fraction(np.cos(float(self.ui.Dominios[indice_ayuda][0]))).limit_denominator().denominator == 1:
                                    limite_superior = int(np.cos(float(self.ui.Dominios[indice_ayuda][0])))
                                else:
                                    limite_superior= np.cos(float(self.ui.Dominios[indice_ayuda][0]))
                                
                                integral_string_f = integral_string_f +", ({0}, {1}, {2}))".format("s", limite_inferior, limite_superior)
                        else:
                            if simbolo in CoefE["{}".format(indice)]:
                                # Se elimina el simbolo para posteriormente intercambiarlo por la expresión completa de la integral.
                                CoefE["{}".format(indice)] = CoefE["{}".format(indice)].replace(simbolo,"")
                                integral_string_i = integral_string_i + "Integral("
                                integral_string_f = integral_string_f + ", ({0}, {1}, {2}))".format(simbolo.replace(",",""), self.ui.Dominios[indice_ayuda][0], self.ui.Dominios[indice_ayuda][1])
                                    
                        indice_ayuda += 1    
                coeficientes = CoefE["{}".format(indice)].split(";")
                coeficientes = [expresion.replace("Int[", integral_string_i).replace("]", integral_string_f).replace("conjugate(Ynm(lamda_n,lamda_m))", "conjugate(Ynm(lamda_n,lamda_m,theta,phi)).expand(func=True)").replace("Ynm(lamda_n,lamda_m)", "Ynm(lamda_n,lamda_m,theta,phi).expand(func=True)").replace("conjugate(Ynm(lamda_n,lamda_l))", "conjugate(Ynm(lamda_n,lamda_l,theta,phi)).expand(func=True)").replace("Ynm(lamda_n,lamda_l)", "Ynm(lamda_n,lamda_l,theta,phi).expand(func=True)").replace("theta","acos(s)") for expresion in coeficientes]
                print(coeficientes)

                # Interpretación de las condiciones de frontera o iniciales.
                condiciones_string = "" # Tabla.
                self.ui.Condiciones = [expresion for expresion in CE.split(":")]
                for indice1 in range(len(self.ui.Condiciones)):
                    self.ui.Condiciones[indice1] = self.ui.Condiciones[indice1].split(";")
                    for indice2 in range(len(self.ui.Condiciones[indice1])):
                        if ((not self.ui.DimensionTemporalEntrada.isChecked()) or (len(self.ui.Condiciones) > 1)) and (indice1 != 1):
                            # En caso de que el problema considere solo condiciones espaciales o de ambos tipos.
                            condiciones_string = condiciones_string  + ", \\quad f_{%(subindice)s}(\\mathbf{x})" % {"subindice":indice2 + 1} +  "= " + latex(parsing.parse_expr(self.ui.Condiciones[indice1][indice2]))  # Tabla.
                            coeficientes = [expresion.replace("f_{}".format(indice2 + 1), "(" + self.ui.Condiciones[indice1][indice2] + ")").replace("theta", "s") for expresion in coeficientes]
                        else:
                            if indice2 == 0:
                                # Cuando el problema tiene primera derivada temporal.
                                condiciones_string = condiciones_string + ", \\quad u(\\mathbf{x},\\hspace{0.1cm} 0) = " + latex(parsing.parse_expr(self.ui.Condiciones[indice1][indice2])) # Tabla.
                                coeficientes = [expresion.replace("g_1", "(" + self.ui.Condiciones[indice1][indice2] + ")").replace("theta", "s") for expresion in coeficientes]
                            else:
                                # Cuando el problema tiene segunda derivada temporal.
                                condiciones_string = condiciones_string + ", \\quad \\frac{\\partial u(\\mathbf{x},\\hspace{0.1cm} t)}{\\partial t}|_{t=0}=" + latex(parsing.parse_expr(self.ui.Condiciones[indice1][indice2]))  # Tabla.
                                coeficientes = [expresion.replace("g_2", "(" + self.ui.Condiciones[indice1][indice2] + ")").replace("theta", "s") for expresion in coeficientes]    

                if self.ui.DimensionTemporalEntrada.isChecked():
                    # Modificación de la entrada temporal para su posterior interpretación.
                    self.ui.FuncionesTemporales[indice] = [expresion.replace("C_1", coeficientes[0]).replace("C_2", coeficientes[-1]).replace("Int[",integral_string_i).replace("]", integral_string_f).replace("Int{", "Integral(").replace("}", ",(s, 0, t))") for expresion in FTE["{}".format(indice)].split(";")]
                    for indice2 in range(len(self.ui.Condiciones[indice1])):
                        # Modificación de la expresión para sustituir las condiciones iniciales
                        if indice2 == 0:
                            # Cuando el problema tiene primera derivada temporal.
                            self.ui.FuncionesTemporales[indice] = [expresion.replace("g_1", "(" + self.ui.Condiciones[-1][indice2] + ")") for expresion in self.ui.FuncionesTemporales[indice]]
                        else:
                            # Cuando el problema tiene segunda derivada temporal.
                            self.ui.FuncionesTemporales[indice] = [expresion.replace("g_2", "(" + self.ui.Condiciones[-1][indice2] + ")") for expresion in self.ui.FuncionesTemporales[indice]]    

                print(coeficientes)

                self.ui.Coeficientes[indice] = [parsing.parse_expr(expresion) for expresion in coeficientes]

                print(self.ui.Coeficientes[indice])

                self.envioActualizacion("Interpretando Funciones y Valores Propios ({0}/{1})".format(indice + 1, int(self.ui.NumeroEntradas.text())))

                # Interpretación de las funciones espaciales y temporales.
                self.ui.FuncionesEspaciales[indice] = [parsing.parse_expr(expresion.replace("Ynm(lamda_n,lamda_m)", "Ynm(lamda_n,lamda_m,theta,phi).expand(func=True)").replace("Ynm(lamda_n,lamda_l)", "Ynm(lamda_n,lamda_l,theta,phi).expand(func=True)")) for expresion in FEE["{}".format(indice)].split(";")]
                if self.ui.DimensionTemporalEntrada.isChecked():
                    self.ui.FuncionesTemporales[indice] = [parsing.parse_expr(expresion) for expresion in self.ui.FuncionesTemporales[indice]]

                # Interpretación de los valores propios.
                self.ui.ValoresPropios[indice] = VPE["{}".format(indice)].split(";")
                indice_ayuda = 1
                if indice != 0:
                    # Desplazamiento del indice de ayuda para considerar los subíndices de los valores propios de los subproblemas anteriores.
                    indice_ayuda = indice_ayuda + len(range(0, indice))
                indices = ["n", "m", "l"]
                suma = "" # Tabla.
                for indice1 in range(len(self.ui.ValoresPropios[indice])):
                    if indice1 == 0:
                        # Para la primera expresión en la entrada de valores propios del subproblema. Se sustituyen las palabras clave por aquellas con subíndice para la enumeración de todas las expresiones de valores propios.
                        self.ui.ValoresPropios[indice][indice1] = self.ui.ValoresPropios[indice][indice1].replace("lamda_n", "lamda_{}n".format(indice_ayuda)).replace("lamda_m", "lamda_{}m".format(indice_ayuda)).replace("lamda_l", "lamda_{}l".format(indice_ayuda))
                        self.ui.FuncionesEspaciales[indice] = [funcion.subs(parsing.parse_expr("lamda_n"), parsing.parse_expr("lamda_{}n".format(indice_ayuda))) for funcion in self.ui.FuncionesEspaciales[indice]]
                        if self.ui.DimensionTemporalEntrada.isChecked():
                            self.ui.FuncionesTemporales[indice] = [funcion.subs(parsing.parse_expr("lamda_n"), parsing.parse_expr("lamda_{}n".format(indice_ayuda))) for funcion in self.ui.FuncionesTemporales[indice]]
                        self.ui.Coeficientes[indice] = [coeficiente.subs(parsing.parse_expr("lamda_n"), parsing.parse_expr("lamda_{}n".format(indice_ayuda))) for coeficiente in self.ui.Coeficientes[indice]]
                    elif indice1 == 1:
                        # En el caso de que exista una segunda expresión en la entrada de valores propios del subproblema. Se sustituyen las palabras clave por aquellas con subíndice para la enumeración de todas las expresiones de valores propios.
                        self.ui.ValoresPropios[indice][indice1] = self.ui.ValoresPropios[indice][indice1].replace("lamda_m", "lamda_{}m".format(indice_ayuda)).replace("lamda_n", "lamda_{}n".format(indice_ayuda)).replace("lamda_l", "lamda_{}l".format(indice_ayuda))
                        self.ui.FuncionesEspaciales[indice] = [funcion.subs(parsing.parse_expr("lamda_m"), parsing.parse_expr("lamda_{}m".format(indice_ayuda))) for funcion in self.ui.FuncionesEspaciales[indice]]
                        if self.ui.DimensionTemporalEntrada.isChecked():
                            self.ui.FuncionesTemporales[indice] = [funcion.subs(parsing.parse_expr("lamda_m"), parsing.parse_expr("lamda_{}m".format(indice_ayuda))) for funcion in self.ui.FuncionesTemporales[indice]]
                        self.ui.Coeficientes[indice] = [coeficiente.subs(parsing.parse_expr("lamda_m"), parsing.parse_expr("lamda_{}m".format(indice_ayuda))) for coeficiente in self.ui.Coeficientes[indice]]
                    else:
                        # En el caso de que exista una tercera expresión en la entrada de valores propios del subproblema. Se sustituyen las palabras clave por aquellas con subíndice para la enumeración de todas las expresiones de valores propios.
                        self.ui.ValoresPropios[indice][indice1] = self.ui.ValoresPropios[indice][indice1].replace("lamda_l", "lamda_{}l".format(indice_ayuda)).replace("lamda_n", "lamda_{}n".format(indice_ayuda)).replace("lamda_m", "lamda_{}m".format(indice_ayuda))
                        self.ui.FuncionesEspaciales[indice] = [funcion.subs(parsing.parse_expr("lamda_l"), parsing.parse_expr("lamda_{}l".format(indice_ayuda))) for funcion in self.ui.FuncionesEspaciales[indice]]
                        if self.ui.DimensionTemporalEntrada.isChecked():
                            self.ui.FuncionesTemporales[indice] = [funcion.subs(parsing.parse_expr("lamda_l"), parsing.parse_expr("lamda_{}l".format(indice_ayuda))) for funcion in self.ui.FuncionesTemporales[indice]]
                        self.ui.Coeficientes[indice] = [coeficiente.subs(parsing.parse_expr("lamda_l"), parsing.parse_expr("lamda_{}l".format(indice_ayuda))) for coeficiente in self.ui.Coeficientes[indice]]


                    signo = ""
                    if (":<" in self.ui.ValoresPropios[indice][indice1]) or (":>" in self.ui.ValoresPropios[indice][indice1]):
                        # Este caso aplica cuando se buscan valores propios menores o mayores a un determinado número.
                        if (":<" in self.ui.ValoresPropios[indice][indice1]):
                            self.ui.ValoresPropios[indice][indice1] = self.ui.ValoresPropios[indice][indice1].split(":<")
                            signo = "<"
                        else:
                            self.ui.ValoresPropios[indice][indice1] = self.ui.ValoresPropios[indice][indice1].split(":>")
                            signo = ">"
                        self.ui.ValoresPropios[indice][indice1].append(signo)

                        if "=" not in self.ui.ValoresPropios[indice][indice1][0]:
                            # Cuando se introduce la forma general de los valores propios.
                            self.ui.ValoresPropios[indice][indice1][0]= parsing.parse_expr(self.ui.ValoresPropios[indice][indice1][0])
                        else:
                            # Cuando se introduce una ecuación.
                            partes = self.ui.ValoresPropios[indice][indice1][0].split("=")
                            self.ui.ValoresPropios[indice][indice1][0] = sp.Eq(parsing.parse_expr(partes[0]),parsing.parse_expr(partes[1]))

                        valorespropios_string = valorespropios_string + "\\lambda_{%(subindice)s} \\rightarrow "% {"subindice":indice_ayuda} + latex(self.ui.ValoresPropios[indice][indice1][0]) + ",\\quad \\lambda_{%(subindice)s} \\rightarrow "% {"subindice":indice_ayuda} + signo + "{}".format(latex(parsing.parse_expr(self.ui.ValoresPropios[indice][indice1][1]))) + "\\quad \\right\\rvert\\left.\\quad " # Tabla.
                    else: 
                        # Cuando se buscan los k primeros valores propios.
                        if "=" not in self.ui.ValoresPropios[indice][indice1]:
                            # Cuando se introduce la forma general de los valores propios.
                            self.ui.ValoresPropios[indice][indice1] = parsing.parse_expr(self.ui.ValoresPropios[indice][indice1])
                        elif "<=" in self.ui.ValoresPropios[indice][indice1]:
                            # Cuando se introduce una desigualdad.
                            self.ui.ValoresPropios[indice][indice1] = parsing.parse_expr(self.ui.ValoresPropios[indice][indice1])
                        else:
                            # Cuando se introduce una ecuación.
                            partes = self.ui.ValoresPropios[indice][indice1].split("=")
                            self.ui.ValoresPropios[indice][indice1] = sp.Eq(parsing.parse_expr(partes[0]),parsing.parse_expr(partes[1]))
                        
                        if parsing.parse_expr("lamda_{}n".format(indice_ayuda)) in self.ui.ValoresPropios[indice][indice1].free_symbols and indice1 == 0:
                            valorespropios_string = valorespropios_string + "\\lambda_{%(subindice)s n} \\rightarrow "% {"subindice":indice_ayuda} + latex(self.ui.ValoresPropios[indice][indice1]) + "\\quad \\right\\rvert\\left.\\quad " # Tabla.
                        elif parsing.parse_expr("lamda_{}m".format(indice_ayuda)) in self.ui.ValoresPropios[indice][indice1].free_symbols and indice1 == 1:
                            valorespropios_string = valorespropios_string + "\\lambda_{%(subindice)s m} \\rightarrow "% {"subindice":indice_ayuda} + latex(self.ui.ValoresPropios[indice][indice1]) + "\\quad \\right\\rvert\\left.\\quad " # Tabla.
                        elif parsing.parse_expr("lamda_{}l".format(indice_ayuda)) in self.ui.ValoresPropios[indice][indice1].free_symbols and indice1 == 2:
                            valorespropios_string = valorespropios_string + "\\lambda_{%(subindice)s l} \\rightarrow "% {"subindice":indice_ayuda} + latex(self.ui.ValoresPropios[indice][indice1]) + "\\quad \\right\\rvert\\left.\\quad " # Tabla.
                        else:
                            if indice1 == 0:
                                valorespropios_string = valorespropios_string + "\\lambda_{%(subindice)s n} \\rightarrow "% {"subindice":indice_ayuda} + latex(self.ui.ValoresPropios[indice][indice1]) + "\\quad \\right\\rvert\\left.\\quad " # Tabla.
                            elif indice1 == 1:
                                valorespropios_string = valorespropios_string + "\\lambda_{%(subindice)s m} \\rightarrow "% {"subindice":indice_ayuda} + latex(self.ui.ValoresPropios[indice][indice1]) + "\\quad \\right\\rvert\\left.\\quad " # Tabla.
                            else:
                                valorespropios_string = valorespropios_string + "\\lambda_{%(subindice)s l} \\rightarrow "% {"subindice":indice_ayuda} + latex(self.ui.ValoresPropios[indice][indice1]) + "\\quad \\right\\rvert\\left.\\quad " # Tabla.

                    if signo == "":
                        print((parsing.parse_expr("lamda_{}n".format(indice_ayuda)) or parsing.parse_expr("lamda_{}m".format(indice_ayuda)) or parsing.parse_expr("lamda_{}l".format(indice_ayuda))) in list(self.ui.ValoresPropios[indice][indice1].free_symbols))
                        if len(list(self.ui.ValoresPropios[indice][indice1].free_symbols)) > 1:
                            if not ((parsing.parse_expr("lamda_{}n".format(indice_ayuda)) or parsing.parse_expr("lamda_{}m".format(indice_ayuda)) or parsing.parse_expr("lamda_{}l".format(indice_ayuda))) in list(self.ui.ValoresPropios[indice][indice1].free_symbols)):
                                # Cuando las expresiones o ecuaciones de valores propios tienen más de una incógnita cuando queremos los primeros n valores propios. 
                                raise ExcesoIncognitasError
                    else:
                        if len(list(self.ui.ValoresPropios[indice][indice1][0].free_symbols)) > 1:
                            if not ((parsing.parse_expr("lamda_{}n".format(indice_ayuda)) or parsing.parse_expr("lamda_{}m".format(indice_ayuda)) or parsing.parse_expr("lamda_{}l".format(indice_ayuda))) in list(self.ui.ValoresPropios[indice][indice1][0].free_symbols)):
                                # Cuando las expresiones o ecuaciones de valores propios tienen más de una incógnita cuando queremos valores propios mayores o menores a un determinado valor. 
                                raise ExcesoIncognitasError
                    
                    # Interpretación del número de términos deseados en cada subproblema.
                    if ("auto" in self.ui.NumeroTerminos[indice][indice1]) and (signo != "<"):
                        # Si el subproblema no requiere calcular valores propios menores a un determinado número no se puede ocupar el comando "auto".
                        raise ComandoInvalidoError
                    if (len(self.ui.NumeroTerminos[indice][indice1].split(":")) == 1) and (self.ui.NumeroTerminos[indice][indice1] != "auto"):
                        if self.ui.NumeroTerminos[indice][indice1] == "":
                            self.ui.NumeroTerminos[indice][indice1] = ["1", "10"]
                        elif self.ui.NumeroTerminos[indice][indice1] == "absoluto":
                            self.ui.NumeroTerminos[indice][indice1] = ["-n", "n"]
                        else:
                            try:
                                int(parsing.parse_expr(self.ui.NumeroTerminos[indice][indice1]))
                                self.ui.NumeroTerminos[indice][indice1] = ["1", self.ui.NumeroTerminos[indice][indice1]]
                            except: 
                                raise NoNumeroError
                    elif (len(self.ui.NumeroTerminos[indice][indice1].split(":")) > 1):
                        try:
                            int(parsing.parse_expr(self.ui.NumeroTerminos[indice][indice1].split(":")[0]))
                            int(parsing.parse_expr(self.ui.NumeroTerminos[indice][indice1].split(":")[-1]))
                            self.ui.NumeroTerminos[indice][indice1] = [self.ui.NumeroTerminos[indice][indice1].split(":")[0], self.ui.NumeroTerminos[indice][indice1].split(":")[-1]]
                        except: 
                            raise NoNumeroError
                    elif self.ui.NumeroTerminos[indice][indice1] == "auto":
                        self.ui.NumeroTerminos[indice][indice1] = ["auto"]
                    else:
                        raise NoNumeroError
                    
                    if self.ui.NumeroTerminos[indice][indice1][0] == "auto":
                        # En caso de tener una suma con valores propios menores a un número determinado.
                        suma = suma + "\\sum_{\\lambda_{" + "{0}{1}".format(indice_ayuda, indices[indice1]) + "}" + signo + latex(parsing.parse_expr(self.ui.ValoresPropios[indice][indice1][1])) + "}" # Tabla.
                    elif (self.ui.NumeroTerminos[indice][indice1][0] != "auto") and (type(self.ui.ValoresPropios[indice][indice1]) == list):
                        # En caso de tener una suma con valores propios mayores a un número determinado.
                        suma = suma + "\\sum_{\\lambda_{" + "{0}{1}".format(indice_ayuda, indices[indice1]) + "}" + signo + latex(parsing.parse_expr(self.ui.ValoresPropios[indice][indice1][1])) + ", {0}".format(indices[indice1]) + "= {0}".format(self.ui.NumeroTerminos[indice][indice1][0]) + "}^{" + "{}".format(self.ui.NumeroTerminos[indice][indice1][1]) + "}" # Tabla.
                    elif self.ui.NumeroTerminos[indice][indice1][0] != self.ui.NumeroTerminos[indice][indice1][1]:
                        # En caso de tener una suma con ambos límites.
                        suma = suma + "\\sum_{" + "{0}".format(indices[indice1]) + "= {0}".format(self.ui.NumeroTerminos[indice][indice1][0]) + "}^{" + "{}".format(self.ui.NumeroTerminos[indice][indice1][1]) + "}" # Tabla.
                    else:
                        # En caso de tener un solo sumando.
                        suma = suma + "" # Tabla.

                self.envioActualizacion("Interpretando Solución ({0}/{1})".format(indice + 1, int(self.ui.NumeroEntradas.text())))

                # Interpretación de la solución
                solucion = 0
                indice_ayuda1 = 0
                indice_ayuda2 = 0
                if indice != 0:
                    # Desplazamiento del indice de ayuda 1 para considerar todas las subsoluciones de los subproblemas anteriores.
                    for indice1 in range(indice):
                        if self.ui.DimensionTemporalEntrada.isChecked():
                            indice_ayuda1 = indice_ayuda1 + len(self.ui.FuncionesEspaciales[indice1])*len(self.ui.FuncionesTemporales[indice1])
                        else:
                            indice_ayuda1 = indice_ayuda1 + len(self.ui.FuncionesEspaciales[indice1])
                print(coeficientes, indice_ayuda1, indice_ayuda2)
                # El siguiente ciclo for es parte del diseño de la tabla para mostrar la interpretación. Se encarga de asignarle un símbolo a cada coeficiente y escribir la solución total con estos coeficientes multiplicando a sus respectivas funciones espaciales y temporales.
                for funproesp in self.ui.FuncionesEspaciales[indice]:
                    if self.ui.DimensionTemporalEntrada.isChecked():
                        for funprotem in self.ui.FuncionesTemporales[indice]:
                            if suma == "":
                                indices = ""  # Tabla.
                            else: 
                                indices = "n"  # Tabla.
                            if len(self.ui.ValoresPropios[indice]) == 2:
                                if suma == "":
                                    indices = indices + ""  # Tabla.
                                else:
                                    indices = indices + "m"  # Tabla.
                            coeficientes_string = coeficientes_string + "%(letra)s_{"%{'letra':list(ascii_uppercase)[indice_ayuda1]} + indices + "} =" + latex(self.ui.Coeficientes[indice][indice_ayuda2]) + "\\quad \\right\\rvert\\left.\\quad " # Tabla.
                            solucion = solucion + parsing.parse_expr("{0}_{1}".format(list(ascii_uppercase)[indice_ayuda1],indices))*funproesp*funprotem # Tabla. 

                            indice_ayuda1 += 1
                            indice_ayuda2 += 1

                    else:
                        if suma == "":
                            indices = "0" # Tabla.
                        else: 
                            indices = "n" # Tabla.
                        if len(self.ui.ValoresPropios[indice]) >= 2:
                            if suma == "":
                                indices = indices + "0" # Tabla.
                            else:
                                indices = indices + "m" # Tabla.
                            if len(self.ui.ValoresPropios[indice]) == 3:
                                if suma == "":
                                    indices = indices + "0" # Tabla.
                                else:
                                    indices = indices + "l" # Tabla.
                        coeficientes_string = coeficientes_string + "%(letra)s_{"%{'letra':list(ascii_uppercase)[indice_ayuda1]} + indices + "} =" + latex(self.ui.Coeficientes[indice][indice_ayuda2]) + "\\quad \\right\\rvert\\left.\\quad " # Tabla.
                        solucion = solucion + parsing.parse_expr("{0}_{1}".format(list(ascii_uppercase)[indice_ayuda1],indices))*funproesp # Tabla.

                        indice_ayuda1 += 1
                        indice_ayuda2 += 1

                if indice != 0:
                    if suma != "":
                        solucion_string = solucion_string + " + " + suma + "\\left[" + latex(solucion) + "\\right]" # Tabla.
                    else:
                        solucion_string = solucion_string + " + " + latex(solucion) # Tabla.
                else:
                    if suma != "":
                        solucion_string = solucion_string + suma + "\\left[" + latex(solucion) + "\\right]" # Tabla.
                    else:
                        solucion_string = solucion_string + latex(solucion) # Tabla.

            self.envioActualizacion("Interpretando Otras Características")

            # Esta parte se encarga de diseñar la interpretación del dominio, así como de obtener las coordenadas presentes en la solución.
            if self.ui.SistemaCoordenadasEntrada.checkedButton().objectName() == "Cartesianas":
                dominio_string = "x=\\left[%(limiteinferior)s,\\hspace{0.1cm} %(limitesuperior)s\\right]"%{'limiteinferior':latex(self.ui.Dominios[0][0]), 'limitesuperior':latex(self.ui.Dominios[0][1])} # Tabla.
                self.ui.Simbolos = [x]
                if self.ui.DimensionEspacialEntrada.value() > 1:
                    dominio_string = dominio_string + ", \\quad " + "y=\\left[%(limiteinferior)s,\\hspace{0.1cm} %(limitesuperior)s\\right]"%{'limiteinferior':latex(self.ui.Dominios[1][0]), 'limitesuperior':latex(self.ui.Dominios[1][1])} # Tabla.
                    self.ui.Simbolos.append(y)
                if self.ui.DimensionEspacialEntrada.value() > 2:
                    dominio_string = dominio_string + ", \\quad " + "z=\\left[%(limiteinferior)s,\\hspace{0.1cm} %(limitesuperior)s\\right]"%{'limiteinferior':latex(self.ui.Dominios[2][0]), 'limitesuperior':latex(self.ui.Dominios[2][1])} # Tabla.
                    self.ui.Simbolos.append(z)
            elif self.ui.SistemaCoordenadasEntrada.checkedButton().objectName() == "Cilíndricas / Polares":
                dominio_string = "r=\\left[%(limiteinferior)s,\\hspace{0.1cm} %(limitesuperior)s\\right]"%{'limiteinferior':latex(self.ui.Dominios[0][0]), 'limitesuperior':latex(self.ui.Dominios[0][1])} + ", \\quad " + "\\phi=\\left[%(limiteinferior)s,\\hspace{0.1cm} %(limitesuperior)s\\right]"%{'limiteinferior':latex(self.ui.Dominios[1][0]), 'limitesuperior':latex(self.ui.Dominios[1][1])} # Tabla.
                self.ui.Simbolos = [r, phi]
                if self.ui.DimensionEspacialEntrada.value() > 2:
                    dominio_string = dominio_string + ", \\quad " + "z=\\left[%(limiteinferior)s,\\hspace{0.1cm} %(limitesuperior)s\\right]"%{'limiteinferior':latex(self.ui.Dominios[2][0]), 'limitesuperior':latex(self.ui.Dominios[2][1])} # Tabla.
                    self.ui.Simbolos.append(z)
            elif self.ui.SistemaCoordenadasEntrada.checkedButton().objectName() == "Esféricas":
                dominio_string = "r=\\left[%(limiteinferior)s,\\hspace{0.1cm} %(limitesuperior)s\\right]"%{'limiteinferior':latex(self.ui.Dominios[0][0]), 'limitesuperior':latex(self.ui.Dominios[0][1])} + ", \\quad " + "\\theta=\\left[%(limiteinferior)s,\\hspace{0.1cm} %(limitesuperior)s\\right]"%{'limiteinferior':latex(self.ui.Dominios[1][0]), 'limitesuperior':latex(self.ui.Dominios[1][1])} + ", \\quad " + "\\phi\\left[%(limiteinferior)s,\\hspace{0.1cm} %(limitesuperior)s\\right]"%{'limiteinferior':latex(self.ui.Dominios[2][0]), 'limitesuperior':latex(self.ui.Dominios[2][1])} # Tabla.
                self.ui.Simbolos = [r, theta, phi]
            if self.ui.DimensionTemporalEntrada.isChecked():
                dominio_string = dominio_string + ", \\quad " + "t=\\left[0,\\hspace{0.1cm} %(limitesuperior)s\\right]"%{'limitesuperior':latex(self.ui.Dominios[-1][0])} # Tabla.
                self.ui.Simbolos.append(t)

            coeficientes_string = coeficientes_string+"\\right. "  # Tabla
            valorespropios_string = valorespropios_string+"\\right. " # Tabla
            funcionespeso_string = funcionespeso_string+"\\right. " # Tabla

            # Creación de un diccionario con la entrada interpretada y escrita en LaTeX.
            entrada = {'solucion':solucion_string}
            entrada['coeficientes'] = coeficientes_string
            entrada['valores'] = valorespropios_string
            entrada['funciones'] = funcionespeso_string
            entrada['condiciones'] = condiciones_string[1:]
            entrada['dominio'] = dominio_string


            # Creación del texto con la interpretación.
            self.ui.Entrada = self.ui.Entrada % entrada
            self.ui.Entrada = self.ui.inicioTex + self.ui.Entrada + self.ui.finTex
            self.ui.Entrada = self.ui.Entrada.replace("for", "para").replace("otherwise", "en otro caso")
            with open('EntradaUsuario.tex','w') as texto_LaTeX:
                texto_LaTeX.write(self.ui.Entrada)

            # Creación del archivo TeX con la interpretación.
            # La creación de esta parte del código se basó en la documentación de la libería plasTeX, en particular fue tomada de plasTeX. (s. f.). 5.1 Simple Renderer Example. plasTeX 3.0 — A Python Framework for Processing LaTeX Documents. https://plastex.github.io/plastex/plastex/sec-simple-renderer-ex.html
            with open('EntradaUsuario.tex') as archivotex:
                tex = TeX(file=archivotex)
                # Creación de la página HTML.
                tex.ownerDocument.config['files']['filename'] = 'Entrada.html'
                Renderer().render(tex.parse())

            # Reinicio del string de interpretación.
            self.ui.Entrada = r'''\textbf{Solución} & \multicolumn{7}{c|}{$\displaystyle u(\mathbf{x}) \approx %(solucion)s $} \\ \hline \textbf{Coeficientes} & \multicolumn{7}{c|}{$\displaystyle %(coeficientes)s$} \\ \hline \textbf{Valores Propios} & \multicolumn{7}{c|}{$\displaystyle %(valores)s$} \\ \hline\textbf{Funciones Peso} & \multicolumn{7}{c|}{$\displaystyle %(funciones)s$} \\ \hline \textbf{Condiciones} & \multicolumn{7}{c|}{$\quad \displaystyle %(condiciones)s \quad$} \\ \hline \textbf{Dominio}& \multicolumn{7}{c|}{$\quad \displaystyle %(dominio)s \quad$} \\'''

            # Lectura de la precisión y calidad deseada.
            self.ui.Precision = int(self.ui.PrecisionEntrada.value())
            self.ui.Calidad = self.ui.CalidadEntrada.isChecked()

            self.signals.finalizar_signal.emit("Interpretación Finalizada")
        except:
            # Interpretación del error ocurrido.
            tipoError, explicacion, linea = sys.exc_info()[:3]
            print(tipoError, explicacion, linea.tb_lineno)
            Error = ""
            typeError = ""
            if tipoError == SyntaxError:
                Error = "Las expresiones introducidas son erróneas. Posibles errores: hace falta un signo de multiplicación, hay paréntesis sin cerrar, las funciones especiales fueron introducidas erróneamente, etc."
                typeError = "Error -- Sintaxis"
            elif tipoError == EntradaVaciaError:
                Error = "Faltan entradas por introducir."
                typeError = "Error -- Entradas en Blanco"
            elif tipoError == ExcesoEntradaError:
                Error = "Se especificaron dos valores propios pero solo un número de términos para las sumas o viceversa."
                typeError = "Error -- Incongruencia entre Valores Propios y Números de Términos"
            elif tipoError == DimensionError:
                Error = "El problema no puede tener una sola dimensión espacial sin tener una dimensión temporal."
                typeError = "Error -- Dimensión"
            elif tipoError == NoNumeroError or tipoError == NameError or tipoError == ExcesoIncognitasError:
                Error = "Hace falta asignar un valor numérico a algunas de las variables de entrada."
                typeError = "Error -- Variables sin Valor Definido"
            elif tipoError == ExtremoFaltanteError or tipoError == TypeError:
                Error = "Coeficientes, condiciones iniciales o extremos del dominio faltantes."
                typeError = "Error -- Pocas Condiciones o  Dominio Incompleto"
            elif tipoError == AttributeError:
                Error = "El sistema de coordenadas no coincide con la información."
                typeError = "Error -- Sistema de Coordenadas Erróneo."
            elif tipoError == UnboundLocalError:
                Error = "No se puede ocupar una clave especial en este tipo de problema."
                typeError = "Error -- Clave Especial Inválida"

            self.ui.Interpretar.setText("Interpretar")

            self.signals.error_signal.emit((typeError, Error))
        finally:
            # Habilitación de los botones de interpretación y limpieza, así como de la ventana principal.
            self.ui.Interpretar.setEnabled(True)
            self.ui.Interpretar.setStyleSheet("color: rgb(234, 237, 239); background-color: rgb(11, 61, 98);")
            self.ui.Interpretar.setShortcut("Ctrl+I")
            self.ui.Limpiar.setEnabled(True)
            self.ui.Limpiar.setStyleSheet("color: rgb(234, 237, 239); background-color: rgb(11, 61, 98);")
            self.ui.centralwidget.setEnabled(True)

class TrabajoResolucion(QtCore.QRunnable):
    """Ejecutable para realizar el procesamiento en paralelo del cálculo de la solución parcial ingresada por el usuario."""

    def __init__(self, ui_informacion, widget):
        """Definicion de la información a utilizar y las señales necesarias para la comunicación."""

        super(self.__class__, self).__init__()
        self.ui = ui_informacion
        self.widget = widget
        self.signals = Indicadores()

    def envioActualizacion(self, mensaje):
        """
        Envía el mensaje a la ventana de carga para informar el punto del trabajo que se está realizando.
        
        Parámetros
        ----------
        mensaje : string
            Mensaje a colocar en la ventana de carga.
        """

        self.signals.avanzar_signal.emit(mensaje)
        QCoreApplication.processEvents()
        QtCore.QThread.msleep(500)

    def obtenerValoresPropios(self, entrada, valorpropio_numero, precision, numeros):
        """
        Obtiene los valores propios necesarios a partir de la entrada con la precisión indicada. 

        Parámetros
        ----------
        **entrada** : ecuación o expresión en Sympy
            Ecuación de eigenvalores o expresión explícita en Sympy.

        **valorpropio_numero** : entero
            Indice para determinar el valor propio que se quiere encontrar (para distinguir entre valores propios cuando la solución se compone de más de un subproblema).

        **precision** : entero
            Determina la precisión decimal de los valores propios.

        **numeros** : arreglo entero de longitud 2
            Determina la cantidad de valores propios a calcular.

        Salida
        ----------
        **ValoresObtenidos** : arreglo de números flotantes
            Lista de números flotantes con los valores propios obtenidos. 
        """

        try: 
            print(entrada)
            if type(entrada) != list:
                if parsing.parse_expr("lamda_{}n".format(valorpropio_numero)) in entrada.free_symbols:
                    variable = parsing.parse_expr("lamda_{}n".format(valorpropio_numero))
                elif parsing.parse_expr("lamda_{}m".format(valorpropio_numero)) in entrada.free_symbols:
                    variable = parsing.parse_expr("lamda_{}m".format(valorpropio_numero))
                elif parsing.parse_expr("lamda_{}l".format(valorpropio_numero)) in entrada.free_symbols:
                    variable = parsing.parse_expr("lamda_{}l".format(valorpropio_numero))
                if entrada.free_symbols == set():
                    # Cuando el usuario introduce un número en específico, esto sucede cuando la solución es un único término. Regresa dicho número redondeado con la precisión deseada.
                    if Fraction(np.round(float(entrada), precision)).limit_denominator().denominator == 1:
                        ValoresObtenidos = [int(entrada)]
                    else:
                        ValoresObtenidos = [np.round(float(entrada), precision)] 
                else:
                    if type(entrada) == sp.core.relational.Equality:
                        # Cuando el usuario introduce una ecuación. 
                        ValoresObtenidos = [None for indice_nulo in range(int(numeros[0]), int(numeros[1])+1)]
                        funcion_valorespropios = sp.lambdify(variable, entrada.lhs-entrada.rhs)
                        valores = self.buscadorRaices(int(numeros[1])+1-int(numeros[0]), funcion_valorespropios, 0, 5, precision)
                        for indice in range(0, len(valores)):
                            if Fraction(valores[indice]).limit_denominator().denominator == 1:
                                ValoresObtenidos[indice] = int(valores[indice])
                            else:
                                ValoresObtenidos[indice] = valores[indice]

                    elif "\\leq" in latex(entrada):
                        entrada = entrada.subs(parsing.parse_expr("lamda_{}m".format(valorpropio_numero)), n).subs(parsing.parse_expr("lamda_{}l".format(valorpropio_numero)), n)
                        ValoresObtenidos = [None for indice_nulo in range(int(-float(entrada.args[1])),  int(float(entrada.args[1]))+1)]
                        numero = int(-float(entrada.args[1]))
                        for indice in range(0, len(ValoresObtenidos)):
                            ValoresObtenidos[indice] = int(np.sign(numero)*entrada.args[0].subs(n, numero))
                            numero += 1
                    else:
                        # Cuando el usuario introduce la solución a la ecuación en términos de un índice entero.
                        ValoresObtenidos = [None for indice_nulo in range(int(numeros[0]), int(numeros[1])+1)]
                        entrada = entrada.subs(m, n).subs(l, n)
                        numero = int(numeros[0])
                        for indice in range(0, len(ValoresObtenidos)):
                            if Fraction(float(entrada.subs(n, numero))).limit_denominator().denominator == 1:
                                ValoresObtenidos[indice] = int(entrada.subs(n, numero))
                            else:
                                # Redondeo a la precisión necesaria.
                                ValoresObtenidos[indice] = np.round(float(entrada.subs(n, numero)), precision)
                            numero += 1
                        
            else:
                if parsing.parse_expr("lamda_{}n".format(valorpropio_numero)) in entrada[0].free_symbols:
                    variable = parsing.parse_expr("lamda_{}n".format(valorpropio_numero))
                elif parsing.parse_expr("lamda_{}m".format(valorpropio_numero)) in entrada[0].free_symbols:
                    variable = parsing.parse_expr("lamda_{}m".format(valorpropio_numero))
                elif parsing.parse_expr("lamda_{}l".format(valorpropio_numero)) in entrada[0].free_symbols:
                    variable = parsing.parse_expr("lamda_{}l".format(valorpropio_numero))
                if numeros[0] == "auto":
                    # Cuando se necesitan encontrar todos los valores propios menores a un determinado número.
                    ValoresObtenidos = []
                    if type(entrada[0]) == sp.core.relational.Equality:
                        # Interpretación de la ecuación.
                        funcion_valorespropios = sp.lambdify(variable, entrada[0].lhs-entrada[0].rhs)
                        entrada[1] = float(parsing.parse_expr(entrada[1]))
                        # Búsqueda de la primera raíz.
                        raiz = self.buscadorRaices(1, funcion_valorespropios, 0, entrada[1], precision, entrada[2])
                        if raiz[0] < np.round(entrada[1], precision):
                            if Fraction(raiz[0]).limit_denominator().denominator == 1:
                                ValoresObtenidos.append(int(raiz[0]))
                            else:
                                ValoresObtenidos.append(float(raiz[0]))
                        else:
                            # En caso de que la primera raíz encontrada no sea menor que el número determinado, existe un error en la entrada o no existen subsoluciones.
                            raise NoExistenciaError
                        valor = ValoresObtenidos[-1]
                        while valor < np.round(entrada[1], precision):
                            # Búsqueda de todas las raíces menores al número especificado por entrada[1].
                            raiz = self.buscadorRaices(1, funcion_valorespropios, ValoresObtenidos[-1]+10**(-precision), entrada[1], precision, entrada[2])
                            print(raiz)
                            if raiz != []:
                                if 0 < raiz[0] < np.round(entrada[1], precision) and valor != raiz[0]:
                                    if Fraction(raiz[0]).limit_denominator().denominator == 1:
                                        ValoresObtenidos.append(int(raiz[0]))
                                    else:
                                        ValoresObtenidos.append(float(raiz[0]))
                            else:
                                break
                    else:
                        # Cuando la entrada es la expresión general de los valores propios, primero se modifica la entrada.
                        entrada[0] = entrada[0].subs(m, n).subs(l, n)
                        entrada[1] = float(parsing.parse_expr(entrada[1]))
                        indice = 1
                        # Obtención de la primera raíz.
                        if float(entrada[0].subs(n, indice)) < np.round(entrada[1], precision):
                            if Fraction(float(entrada[0].subs(n, indice))).limit_denominator().denominator == 1:
                                ValoresObtenidos.append(int(entrada[0].subs(n, indice)))
                            else:
                                ValoresObtenidos.append(float(entrada[0].subs(n, indice)))
                        else:
                            # En caso de que la primera raíz encontrada no sea menor que el número determinado, existe un error en la entrada o no existen subsoluciones no nulas.
                            raise NoExistenciaError
                        valor = ValoresObtenidos[-1]
                        while valor < np.round(entrada[1], precision):
                            # Búsqueda de todas las raíces menores al número especificado por entrada[1].
                            valorpropio = entrada[0].subs(n, indice + 1)
                            if  valorpropio < np.round(entrada[1], precision):
                                if Fraction(valorpropio).limit_denominator().denominator == 1:
                                    ValoresObtenidos.append(int(valorpropio))
                                else:
                                    ValoresObtenidos.append(float(valorpropio))
                            else:
                                break
                            indice += 1
                else:
                    # En caso de que se busquen valores propios mayores o menores a un número determinado.
                    if entrada[-1] == "<":
                        # Cuando se buscan números menores se establece el intervalo [0, número determinado].
                        extremo_izq = 0
                        extremo_der = float(parsing.parse_expr(entrada[1]))
                    else:
                        # Cuando se buscan números mayores se establece de manera inicial el intervalo [número determinado, número determinado + 5].
                        extremo_izq = float(parsing.parse_expr(entrada[1]))
                        extremo_der = float(parsing.parse_expr(entrada[1]))+5
                    ValoresObtenidos = [None for indice_nulo in range(int(numeros[0]), int(numeros[1])+1)]
                    expresion = entrada[0]
                    if type(expresion) == sp.core.relational.Equality:
                        # Interpretación de la ecuación y obtención de los valores propios requeridos.
                        funcion_valorespropios = sp.lambdify(variable, expresion.lhs-expresion.rhs)
                        valores = self.buscadorRaices(int(numeros[1])+1-int(numeros[0]), funcion_valorespropios, extremo_izq, extremo_der, precision, entrada[2])
                        for indice in range(0, len(valores)):
                            if Fraction(valores[indice]).limit_denominator().denominator == 1:
                                ValoresObtenidos[indice] = int(valores[indice])
                            else:
                                # Redondeo a la precisión necesaria.
                                ValoresObtenidos[indice] = float(np.round(valores[indice], precision))
                    else:
                        # Cuando la entrada es la expresión general de los valores propios, primero se modifica la entrada.

                        # Obtención del índice entero más pequeño que puede hacer que el valor propio sea mayor o igual al valor determinado. 
                        expresion = expresion.subs(m, n).subs(l, n)
                        ecuacion = sp.Eq(expresion, extremo_izq)
                        indice_critico = int(np.ceil(sp.solve(ecuacion, n)[0]))
                        indice_ayuda = 0
                        for indice in range(1, len(ValoresObtenidos)+1):
                            if (entrada[-1] == "<") and (float(expresion.subs(n, indice)) < extremo_der) and (indice < indice_critico):
                                # Agrega a la lista los valores propios que son menores que el valor determinado.
                                if Fraction(float(expresion.subs(n, indice))).limit_denominator().denominator == 1:
                                    ValoresObtenidos[indice_ayuda] = int(expresion.subs(n, indice))
                                else:
                                    # Redondeo a la precisión necesaria.
                                    ValoresObtenidos[indice_ayuda] = float(expresion.subs(n, indice))
                                indice_ayuda += 1
                            elif (entrada[-1] == ">") and (float(expresion.subs(n, indice + indice_critico)) >= extremo_izq):
                                # Agrega a la lista los valores propios que son mayores o iguales que el valor determinado.
                                if Fraction(float(expresion.subs(n, indice + indice_critico))).limit_denominator().denominator == 1:
                                    ValoresObtenidos[indice_ayuda] = int(expresion.subs(n, indice + indice_critico))
                                else:
                                    # Redondeo a la precisión necesaria.
                                    ValoresObtenidos[indice_ayuda] = float(expresion.subs(n, indice + indice_critico))
                                indice_ayuda += 1
                # Remoción si no se encontraron tantos valores como esperaba el usuario.
                for indice in range(len(ValoresObtenidos)):
                    indice_ayuda = len(ValoresObtenidos)-indice-1
                    if ValoresObtenidos[indice_ayuda] == None:
                        ValoresObtenidos.pop(indice_ayuda)
                # Redondeo a la precisión necesaria.
                ValoresObtenidos = np.round(ValoresObtenidos, precision)

        except:
            tipoError, explicacion, line = sys.exc_info()[:3]
            print(tipoError)
            print(explicacion)
            print(line.tb_lineno)

        
        print(ValoresObtenidos)
        return ValoresObtenidos
    
    def buscadorRaices(self, cantidad, funcion, extremo_izq, extremo_der, precision, signo = ""):
        """
        Busca las raíces de la función en el intervalo [extremo_izq, extremo_der]  hasta completar la cantidad de raíces necesarias. Estas raíces son buscadas con un grado de precisión tal que funcion(raiz) < 1E-precision.

        Parámetros
        ----------
        **cantidad** : entero
            Número de raíces a buscar.

        **funcion** : funcion obtenida a través del comando de Sympy 'lambdify'
            Ecuación representada como una función de numpy.

        **extremo_izq** : flotante
            Extremo izquierdo del intervalo en donde se buscarán las raíces.

        **extremo_der** : flotante
            Extremo derecho del intervalo en donde se buscarán las raíces.

        **precision** : entero
            Precisión con la que se determinará si un número es una raíz.
        
        **signo** : string
            Símbolo mayor o menor que.

        Salida
        ---------
        raices : lista de números flotantes
            Lista con las raíces encontradas.
        """

        # Esta función se basa en Kiusalaas, J. (2013). Numerical methods in Engineering with Python 3. (1a. ed., pp. 151). Cambridge University Press. 

        def buscadorIntervalos(funcion, extremo_izq, extremo_der, aumento):
            """
            Busca intervalos donde exista un cambio de signo en el valor de la función.            

            Parámetros
            ----------
            **funcion** : funcion obtenida a través del comando de Sympy 'lambdify'
                Ecuación representada como una función de numpy.

            **extremo_izq** : flotante
                Extremo izquierdo del intervalo en donde se buscarán las raíces.

            **extremo_der** : flotante
                Extremo derecho del intervalo en donde se buscarán las raíces.

            **aumento** : flotante
                Valor que determina el tamaño del paso en la búsqueda de intervalos.

            Salida
            ----------
            **x1, x2** : par de números flotantes
                Extremos del intervalo en donde existe un cambio de signo.
            """

            # Esta función fue tomada de Kiusalaas, J. (2013). Numerical methods in Engineering with Python 3. (1a. ed., pp. 147). Cambridge University Press. 

            x1 = extremo_izq
            x2 = extremo_izq + aumento
            f1 = funcion(x1)
            f2 = funcion(x2)
            while np.sign(f1) == np.sign(f2):
                if x1 >= extremo_der:
                    return None, None
                x1 = x2
                f1 = f2
                x2 = x1 + aumento
                f2 = funcion(x2)
            else:
                return x1, x2
        
        def buscadorIntervalos_optimizado(funcion, extremo_izq, extremo_der, precision):
            """
            Buscador optimizado de intervalos que disminuye el número de iteraciones con base en la precisión.

            Parámetros
            ----------
            **funcion** : funcion obtenida a través del comando de Sympy 'lambdify'
                Ecuación representada como una función de numpy.

            **extremo_izq** : flotante
                Extremo izquierdo del intervalo en donde se buscarán las raíces.

            **extremo_der** : flotante
                Extremo derecho del intervalo en donde se buscarán las raíces.

            **precision** : entero
                Precisión deseada en la determinación de raíces.

            Salida
            ----------
            **x1, x2** : par de números flotantes
                Extremos del intervalo en donde existe un cambio de signo.
             """

            # Esta función fue tomada y modificada de Kiusalaas, J. (2013). Numerical methods in Engineering with Python 3. (1a. ed., pp. 148). Cambridge University Press. 
            # La modificación consiste en cambiar el aumento para que sea independiende de x1 y x2 (para evitar problemas en intervalos que no tienen longitud 1).

            x1 = extremo_izq
            x2 = extremo_der
            
            # En cada iteración se aumenta la precisión de la búsqueda. La búsqueda para un determinado intervalo ocupa aproximadamente (longitud del intervalo)*(precision)*10 iteraciones.
            for iteracion in range(precision-1):
                aumento = 1/10**(iteracion + 1)
                x1, x2 = buscadorIntervalos(funcion, x1, x2, aumento)
                if (x1 == None) or (x2 == None):
                    break
            return x1, x2
        
        extremo_izq_old = extremo_izq
        raices = [None]
        if signo != "":
            # En caso de que se busquen raíces mayores a un cierto valor.
            # Se recorre el intervalo para que el extremo izq sea igual al valor determinante.
            while len(raices) < cantidad+1:
                x1, x2 = buscadorIntervalos_optimizado(funcion, extremo_izq, extremo_der, precision)
                if x1 != None:
                    # En caso de que exista un subintervalo de cambio de signo se busca con mayor precision la raiz y se restringe el intervalo inicial a [x2, extremo_der]
                    extremo_izq = x2
                    raiz = sc.optimize.brentq(funcion, x1, x2, maxiter = 1000)
                    if (raiz != None) and (raiz != float(0)) and (np.round(raiz, precision) < extremo_der):
                        if funcion(raiz) < 10**(-precision):
                            # Si la raíz encontrada conlleva la precisión necesaria, entonces se agrega a la lista de raíces.
                            raices.append(np.round(raiz, precision))
                    if (signo == "<") and (x2 > extremo_der):
                        # Cuando el extremo del subintervalo es mayor que el extremo derecho y buscamos valores propios menores al extremo derecho, entonces significa que se han agotado todos los posibles valores menores.
                        break
                    elif (signo == ">") and (x2 > extremo_der):
                        # Si el extremo derecho del intervalo donde hay un cambio de signo es mayor que el extremo derecho del intervalo inicial, este valor se recorre pi unidades. Esto de acuerdo al valor asintótico para las raíces de las funciones base del problema de Sturm-Liouville.
                        extremo_der = extremo_der + np.pi
                else:
                    if signo == ">":
                        # En caso contrario, es decir, cuando no se encuentren subintervalos de cambio de signo en el intervalo inicial, se considera el intervalo de longitud pi que se encuentra justo a la derecha del intervalo inicial, siempre y cuando busquemos valores mayores.
                        extremo_izq = extremo_der
                        extremo_der = extremo_izq + np.pi
                    else:
                        # Si no se encuentra ningún valor propio en el intervalo [0, extremo_der], entonces significa que no existen más valores propios menores al extremo derecho.
                        break
        else:
            # En caso de que se busquen raíces hasta completar la cantidad especificada.
            while len(raices) < cantidad+1:
                x1, x2 = buscadorIntervalos_optimizado(funcion, extremo_izq, extremo_der, precision)
                print(x1,x2)
                if x1 != None:
                    # Si existe el subintervalo donde ocurre un cambio de signo se procede a encontrar la raíz con mayor precisión.
                    raiz = sc.optimize.brentq(funcion, x1, x2, maxiter = 1000)
                    if (raiz != None) and (np.round(raiz, precision) != raices[-1]) and (raiz != 0) and (np.round(raiz, precision) != extremo_izq_old):
                        if funcion(raiz) < 10**(-precision):
                            # Si la raíz encontrada conlleva la precisión necesaria, entonces se agrega a la lista de raíces.
                            raices.append(np.round(raiz, precision))
                    # Después de encontrar una raíz se reduce el intervalo de búsqueda para no volver a considerar el mismo valor. 
                    extremo_izq = x2
                    extremo_izq_old = extremo_izq
                    if x2 > extremo_der:
                        # Si el extremo derecho del intervalo donde hay un cambio de signo es mayor que el extremo derecho del intervalo inicial, este valor se recorre pi unidades. Esto de acuerdo al valor asintótico para las raíces de las funciones base del problema de Sturm-Liouville.
                        extremo_der = extremo_der + np.pi
                else:
                    # En caso contrario, es decir, cuando no se encuentren subintervalos de cambio de signo en el intervalo inicial, se considera el intervalo de longitud pi que se encuentra justo a la derecha del intervalo inicial.
                    extremo_izq = extremo_der
                    extremo_der = extremo_izq + np.pi
            
        return raices[1:]

    @QtCore.pyqtSlot()
    def run(self):
        # Deshabilitacion de la pantalla principal mientras se realiza la resolución.
        self.ui.centralwidget.setDisabled(True)
        self.ui.Interpretar.setDisabled(True)
        self.ui.Interpretar.setStyleSheet("background-color : rgb(127,146,151); color: rgb(234,237,239);")
        self.ui.Limpiar.setDisabled(True)
        self.ui.Limpiar.setStyleSheet("background-color : rgb(127,146,151); color: rgb(234,237,239);")
        try:
            self.envioActualizacion("Recopilando datos")

            # Determinación de la dependencia temporal.
            if self.ui.DimensionTemporalEntrada.isChecked():
                self.ui.dependencia_tiempo = True
            else:
                self.ui.dependencia_tiempo = False

            # Copiado de datos desde la interfaz principal al trabajo para el trabajo en segundo plano.
            numeroentradas = self.ui.NumeroEntradas.text()
            valorespropios_copia = self.ui.ValoresPropios.copy()
            numeroterminos = self.ui.NumeroTerminos.copy()
            precision_copia = self.ui.Precision
            coeficientes_copia = self.ui.Coeficientes.copy()
            funciones_espaciales = self.ui.FuncionesEspaciales.copy()
            if self.ui.dependencia_tiempo:
                funciones_temporales = self.ui.FuncionesTemporales.copy()

            Soluciones = [[] for x in range(0, int(numeroentradas))]
            SolucionesSubproblemas = [None for x in range(0, int(numeroentradas))]
            lamda = symbols("lamda", positive = True, real=True)
            mu = symbols("mu", positive = True, real=True)
            nu = symbols("nu", positive = True, real=True)
            indicesdependencia = []

            # Obtención de las subsoluciones a partir de los datos interpretados.
            for indice in range(int(numeroentradas)):
                self.envioActualizacion("Calculando Valores Propios ({0}/{1})".format(indice+1, int(numeroentradas)))
                
                # Obtención de los valores propios de cada subproblema.
                indice_ayuda = 1
                if indice != 0:
                    # Desplazamiento del indice de ayuda 1 para considerar todas las subsoluciones de los subproblemas anteriores.
                    indice_ayuda = indice_ayuda + len(range(0, indice))
                lamda_n = parsing.parse_expr("lamda_{}n".format(indice_ayuda))
                lamda_m = parsing.parse_expr("lamda_{}m".format(indice_ayuda))
                lamda_l = parsing.parse_expr("lamda_{}l".format(indice_ayuda))
                print(lamda_n, lamda_m, lamda_l)

                invertir = False
                if len(valorespropios_copia[indice]) == 2:
                    if Symbol("lamda_{}n".format(indice_ayuda)) in valorespropios_copia[indice][1].free_symbols:
                        # Cuando la segunda expresión o ecuación depende del primer valor propio.
                        valorespropios = [self.obtenerValoresPropios(valorespropios_copia[indice][0], indice_ayuda, precision_copia, numeroterminos[indice][0]), []]
                        for indice_auxiliar in range(len(valorespropios[0])):
                            valorespropios[1].append(self.obtenerValoresPropios(valorespropios_copia[indice][1].subs(Symbol("lamda_{}n".format(indice_ayuda)), valorespropios[0][indice_auxiliar]), indice_ayuda, precision_copia, numeroterminos[indice][1]))
                        dependencia = True
                        indicesdependencia.append(indice)
                    elif Symbol("lamda_{}m".format(indice_ayuda)) in valorespropios_copia[indice][0].free_symbols:
                        # Cuando la primera expresión o ecuación depende del segundo valor propio.
                        valorespropios = [self.obtenerValoresPropios(valorespropios_copia[indice][1], indice_ayuda, precision_copia, numeroterminos[indice][1]), []]
                        for indice_auxiliar in range(len(valorespropios[0])):
                            valorespropios[1].append(self.obtenerValoresPropios(valorespropios_copia[indice][0].subs(Symbol("lamda_{}m".format(indice_ayuda)), valorespropios[0][indice_auxiliar]), indice_ayuda, precision_copia, numeroterminos[indice][0]))
                        dependencia = True
                        invertir = True
                        indicesdependencia.append(indice)
                    else:
                        # Cuando no hay dependencia entre ambas expresiones o ecuaciones.
                        valorespropios = [self.obtenerValoresPropios(valorespropios_copia[indice][0], indice_ayuda, precision_copia, numeroterminos[indice][0]), np.array([self.obtenerValoresPropios(valorespropios_copia[indice][1], indice_ayuda + 1, precision_copia, numeroterminos[indice][1])]).transpose()]
                        dependencia = False
                    bidependencia = False
                    valorespropios_copia[indice] = valorespropios
                elif len(valorespropios_copia[indice]) == 3:
                    if (Symbol("lamda_{}n".format(indice_ayuda)) in valorespropios_copia[indice][1].free_symbols) and (not (Symbol("lamda_{}n".format(indice_ayuda)) in valorespropios_copia[indice][2].free_symbols)):
                        # Cuando la tercera expresión o ecuación depende del segundo valor propio.
                        valorespropios = [self.obtenerValoresPropios(valorespropios_copia[indice][0], indice_ayuda, precision_copia, numeroterminos[indice][0]), [], self.obtenerValoresPropios(valorespropios_copia[indice][2], indice_ayuda, precision_copia, numeroterminos[indice][2])]
                        for indice_auxiliar in range(len(valorespropios[0])):
                            valorespropios[1].append(self.obtenerValoresPropios(valorespropios_copia[indice][1].subs(Symbol("lamda_{}n".format(indice_ayuda)), valorespropios[0][indice_auxiliar]), indice_ayuda, precision_copia, numeroterminos[indice][1]))
                        dependencia = True
                        bidependencia = False
                        indicesdependencia.append(indice)
                    elif (Symbol("lamda_{}n".format(indice_ayuda)) in valorespropios_copia[indice][1].free_symbols) and (Symbol("lamda_{}n".format(indice_ayuda)) in valorespropios_copia[indice][2].free_symbols):
                        # Cuando la segunda expresión o ecuación depende del tercer valor propio.
                        valorespropios = [self.obtenerValoresPropios(valorespropios_copia[indice][0], indice_ayuda, precision_copia, numeroterminos[indice][0]), [], []]
                        for indice_auxiliar in range(len(valorespropios[0])):
                            valorespropios[1].append(self.obtenerValoresPropios(valorespropios_copia[indice][1].subs(Symbol("lamda_{}n".format(indice_ayuda)), valorespropios[0][indice_auxiliar]), indice_ayuda, precision_copia, numeroterminos[indice][1]))
                            valorespropios[2].append(self.obtenerValoresPropios(valorespropios_copia[indice][2].subs(Symbol("lamda_{}n".format(indice_ayuda)), valorespropios[0][indice_auxiliar]), indice_ayuda, precision_copia, numeroterminos[indice][2]))
                        dependencia = True
                        bidependencia = True
                        indicesdependencia.append(indice)
                    else:
                        # Cuando no hay dependencia entre las expresiones o ecuaciones.
                        valorespropios = [self.obtenerValoresPropios(valorespropios_copia[indice][0], indice_ayuda, precision_copia, numeroterminos[indice][0]), self.obtenerValoresPropios(valorespropios_copia[indice][1], indice_ayuda, precision_copia, numeroterminos[indice][1]), self.obtenerValoresPropios(valorespropios_copia[indice][2], indice_ayuda, precision_copia, numeroterminos[indice][2])]
                        bidependencia = False
                        dependencia = False
                    valorespropios_copia[indice] = valorespropios
                else:
                    # Cuando solo se tiene una expresión (por ende, un único conjunto de valores propios).
                    valorespropios_copia[indice] = [self.obtenerValoresPropios(valorespropios_copia[indice][0], indice_ayuda, precision_copia, numeroterminos[indice][0])]
                    bidependencia = False
                    dependencia = False
                    if len(numeroterminos[indice][0]) < 2:
                        numeroterminos[indice][0][0] = 1
                        numeroterminos[indice][0].append(len(valorespropios_copia[indice][0]))

                if len(valorespropios_copia[indice]) == 1:
                    valorespropios_copia[indice].append(np.array([[1]]).transpose())

                self.envioActualizacion("Calculando Coeficientes y Términos ({0}/{1})".format(indice+1, int(numeroentradas)))
                
                # En caso de que los coeficientes dependan de otras subsoluciones, se sustiuyen estas en dichos coeficientes.
                for indice1 in range(0, indice):
                    for indice2 in range(0, len(coeficientes_copia[indice])):
                        if parsing.parse_expr("u_{}".format(indice1 + 1)) in list(coeficientes_copia[indice][indice2].free_symbols):
                            coeficientes_copia[indice][indice2] = coeficientes_copia[indice][indice2].subs(parsing.parse_expr("u_{}".format(indice1 + 1)), SolucionesSubproblemas[indice1])

                print(valorespropios_copia[indice])
                # Creación de la lista donde se guardarán las subsoluciones.
                if dependencia:
                    if len(valorespropios_copia[indice]) == 2:
                        Soluciones[indice] = [[None for indice_nulo in range(len(valorespropios_copia[indice][1][indice_nulo2]))] for indice_nulo2 in range(len(valorespropios_copia[indice][0]))]
                    else:
                        if bidependencia:
                            Soluciones[indice] = [[[None for indice_nulo in range(len(valorespropios_copia[indice][2][indice_nulo3]))] for indice_nulo2 in range(len(valorespropios_copia[indice][1][indice_nulo3]))] for indice_nulo3 in range(len(valorespropios_copia[indice][0]))]
                        else:
                            Soluciones[indice] = [[[None for indice_nulo in range(len(valorespropios_copia[indice][2]))] for indice_nulo2 in range(len(valorespropios_copia[indice][1][indice_nulo3]))] for indice_nulo3 in range(len(valorespropios_copia[indice][0]))]
                else:
                    if len(valorespropios_copia[indice]) == 2:
                        Soluciones[indice] = [[None for indice_nulo2 in range(len(valorespropios_copia[indice][1]))] for indice_nulo1 in range(len(valorespropios_copia[indice][0]))]
                    else:
                        Soluciones[indice] = [[[None for indice_nulo3 in range(len(valorespropios_copia[indice][2]))] for indice_nulo2 in range(len(valorespropios_copia[indice][1]))] for indice_nulo1 in range(len(valorespropios_copia[indice][0]))]
                
                # Calculo de las subsoluciones.
                if self.ui.dependencia_tiempo:
                    funciones_temporales[indice] = [expresion.subs(lamda_n, lamda).subs(lamda_m, mu).doit() for expresion in funciones_temporales[indice]]
                coeficientes = [expresion.subs(lamda_n, lamda).subs(lamda_m, mu).subs(lamda_l, nu) for expresion in coeficientes_copia[indice]]
                print(coeficientes)
                if dependencia and (len(valorespropios_copia[indice]) == 2):
                    for indice1 in range(len(valorespropios_copia[indice][0])):
                        for indice2 in range(len(valorespropios_copia[indice][1][indice1])):
                            solucion_parcial = 0
                            indice_auxiliar = 0
                            for funcion_espacial in funciones_espaciales[indice]:
                                if self.ui.dependencia_tiempo:
                                    # Cuando hay dependencia temporal en la solución.
                                    for funcion_temporal in funciones_temporales[indice]:
                                        if invertir:
                                            # Cuando el primer valor propio depende del segundo.
                                            coeficiente = np.round(float(coeficientes[indice_auxiliar].subs(lamda, valorespropios_copia[indice][1][indice1][indice2]).subs(mu, valorespropios_copia[indice][0][indice1]).doit()), precision_copia)
                                            solucion_parcial = solucion_parcial + coeficiente*funcion_espacial*funcion_temporal.subs(lamda, valorespropios_copia[indice][1][indice1][indice2]).subs(mu, valorespropios_copia[indice][0][indice1])
                                        else:
                                            # Cuando el segundo valor propio depende del primero.
                                            print(coeficientes[indice_auxiliar].subs(lamda, valorespropios_copia[indice][0][indice1]).subs(mu, valorespropios_copia[indice][1][indice1][indice2]))
                                            coeficiente = np.round(float(coeficientes[indice_auxiliar].subs(lamda, valorespropios_copia[indice][0][indice1]).subs(mu, valorespropios_copia[indice][1][indice1][indice2]).doit()), precision_copia)
                                            solucion_parcial = solucion_parcial + coeficiente*funcion_espacial*funcion_temporal.subs(lamda, valorespropios_copia[indice][0][indice1]).subs(mu, valorespropios_copia[indice][1][indice1][indice2])
                                        indice_auxiliar += 1
                                else:
                                    # Cuando no hay dependencia temporal.
                                    if invertir:
                                        # Cuando el primer valor propio depende del segundo.
                                        coeficiente = np.round(float(coeficientes[indice_auxiliar].subs(lamda, valorespropios_copia[indice][1][indice1][indice2]).subs(mu, valorespropios_copia[indice][0][indice1]).doit()), precision_copia)
                                        solucion_parcial = solucion_parcial + coeficiente*funcion_espacial
                                    else:
                                        # Cuando el segundo valor propio depende del primero.
                                        # Procesamiento para calcular coeficientes que tienen expresiones en el campo de los números complejos. Este proceso se basa en 78g. (02 de noviembre de 2019). integrate throws error for rational functions involving I #17841. Sympy Github. https://github.com/sympy/sympy/issues/17841#issue-516545087
                                        # Variables.
                                        cantidadCompleja = symbols('b', complex = True, zero = False)
                                        valornulo = symbols('a', positive = True)
                                        # Se sustituye la unidad imaginaria por un número real cualquiera distinto de cero y se reexpresa el coeficiente para expandir las exponenciales complejas, después se evalua la integral y en el resultado se sustituye primero el valor nulo y después la unidad imaginaria. Finalmente, se reexpresa la solución para expandir las exponenciales complejasque puedan haber surgido.
                                        valor = simplify(coeficientes[indice_auxiliar].subs(lamda, valorespropios_copia[indice][0][indice1]).subs(mu, valorespropios_copia[indice][1][indice1][indice2]).rewrite(cos).subs(I, cantidadCompleja).doit()).subs(cantidadCompleja, valornulo).subs(valornulo, I).rewrite(cos)

                                        if I in valor.args:
                                            # Cuando el valor es un número imaginario puro se redondea el número real y después se agrega la unidad imaginaria.
                                            coeficiente = I*np.round(float(valor/I), precision_copia)
                                        else:
                                            coeficiente = np.round(float(valor), precision_copia)
                                        
                                        solucion_parcial = solucion_parcial + coeficiente*funcion_espacial
                                    indice_auxiliar += 1
                            if invertir:
                                solucion_parcial = solucion_parcial.subs(lamda_n, valorespropios_copia[indice][1][indice1][indice2]).subs(lamda_m, valorespropios_copia[indice][0][indice1])
                                if solucion_parcial.has(I):
                                    Soluciones[indice][indice1][indice2] = solucion_parcial.rewrite(cos)
                                else:
                                    Soluciones[indice][indice1][indice2] = solucion_parcial
                            else:
                                solucion_parcial = solucion_parcial.subs(lamda_n, valorespropios_copia[indice][0][indice1]).subs(lamda_m, valorespropios_copia[indice][1][indice1][indice2])
                                if solucion_parcial.has(I):
                                    Soluciones[indice][indice1][indice2] = solucion_parcial.subs(lamda_n, valorespropios_copia[indice][0][indice1]).subs(lamda_m, valorespropios_copia[indice][1][indice1][indice2]).rewrite(cos)
                                else:
                                    Soluciones[indice][indice1][indice2] = solucion_parcial
                else:
                    if len(valorespropios_copia[indice]) == 2:
                        # Cuando no hay dependencia entre las dos expresiones de valores propios.
                        for indice1, indice2 in [(x, y) for x in range(len(valorespropios_copia[indice][0])) for y in range(len(valorespropios_copia[indice][1]))]:
                            for indice3 in range(len(valorespropios_copia[indice][1][indice2])):
                                solucion_parcial = 0
                                indice_auxiliar = 0
                                for funcion_espacial in funciones_espaciales[indice]:
                                    if self.ui.dependencia_tiempo:
                                        # Cuando hay dependencia temporal.
                                        for funcion_temporal in funciones_temporales[indice]:
                                            print(coeficientes[indice_auxiliar])
                                            coeficiente = np.round(float(coeficientes[indice_auxiliar].subs(lamda, valorespropios_copia[indice][0][indice1]).subs(mu, valorespropios_copia[indice][1][indice2][indice3]).doit()), precision_copia)
                                            solucion_parcial = solucion_parcial + coeficiente*funcion_espacial*funcion_temporal.subs(lamda, valorespropios_copia[indice][0][indice1]).subs(mu, valorespropios_copia[indice][1][indice2][indice3])
                                            indice_auxiliar += 1
                                    else:
                                        print(indice1, indice2, indice3, coeficientes[indice_auxiliar])
                                        # Cuando no hay dependencia temporal.
                                        coeficiente = np.round(float(coeficientes[indice_auxiliar].subs(lamda, valorespropios_copia[indice][0][indice1]).subs(mu, valorespropios_copia[indice][1][indice2][indice3]).doit()), precision_copia)
                                        solucion_parcial = solucion_parcial + coeficiente*funcion_espacial
                                        indice_auxiliar += 1
                                solucion_parcial = solucion_parcial.subs(lamda_n, valorespropios_copia[indice][0][indice1]).subs(lamda_m, valorespropios_copia[indice][1][indice2][indice3])
                                if solucion_parcial.has(I):
                                    Soluciones[indice][indice1][indice2] = solucion_parcial.rewrite(cos)
                                else:
                                    Soluciones[indice][indice1][indice2] = solucion_parcial
                    else:
                        if dependencia:
                            if bidependencia:
                                # Cuando hay dependencia entre las tres expresiones de valores propios.
                                for indice1 in range(len(valorespropios_copia[indice][0])):
                                    for indice2 in range(len(valorespropios_copia[indice][1][indice1])):
                                        for indice3 in range(len(valorespropios_copia[indice][2][indice1])):
                                            solucion_parcial = 0
                                            indice_auxiliar = 0
                                            for funcion_espacial in funciones_espaciales[indice]:
                                                # Cuando no hay dependencia temporal.
                                                print(coeficientes[indice_auxiliar])
                                                if invertir:
                                                    coeficiente = np.round(float(coeficientes[indice_auxiliar].subs(lamda, valorespropios_copia[indice][0][indice1]).subs(mu, valorespropios_copia[indice][1][indice1][indice2]).subs(nu, valorespropios_copia[indice][2][indice1][indice3]).doit()), precision_copia)
                                                else:
                                                    coeficiente = np.round(float(coeficientes[indice_auxiliar].subs(lamda, valorespropios_copia[indice][0][indice1]).subs(mu, valorespropios_copia[indice][1][indice1][indice2]).subs(nu, valorespropios_copia[indice][2][indice1][indice3]).doit()), precision_copia)
                                                solucion_parcial = solucion_parcial + coeficiente*funcion_espacial
                                                indice_auxiliar += 1

                                            solucion_parcial = solucion_parcial.subs(lamda_n, valorespropios_copia[indice][0][indice1]).subs(lamda_m, valorespropios_copia[indice][1][indice1][indice2]).subs(lamda_l, valorespropios_copia[indice][2][indice1][indice3])

                                            print(solucion_parcial)
                                            if solucion_parcial.has(I):
                                                Soluciones[indice][indice1][indice2][indice3] = solucion_parcial.rewrite(cos)
                                            else:
                                                Soluciones[indice][indice1][indice2][indice3] = solucion_parcial
                            else:
                                # Cuando hay alguna dependencia entre las tres expresiones de valores propios.
                                for indice1 in range(len(valorespropios_copia[indice][0])):
                                    for indice2 in range(len(valorespropios_copia[indice][1][indice1])):
                                        for indice3 in range(len(valorespropios_copia[indice][2])):
                                            solucion_parcial = 0
                                            indice_auxiliar = 0
                                            for funcion_espacial in funciones_espaciales[indice]:
                                                # Cuando no hay dependencia temporal.
                                                print(coeficientes[indice_auxiliar])
                                                coeficiente = np.round(float(coeficientes[indice_auxiliar].subs(lamda, valorespropios_copia[indice][0][indice1]).subs(mu, valorespropios_copia[indice][1][indice1][indice2]).subs(nu, valorespropios_copia[indice][2][indice3]).doit()), precision_copia)
                                                solucion_parcial = solucion_parcial + coeficiente*funcion_espacial
                                                indice_auxiliar += 1
                                            
                                            solucion_parcial = solucion_parcial.subs(lamda_n, valorespropios_copia[indice][0][indice1]).subs(lamda_m, valorespropios_copia[indice][1][indice1][indice2]).subs(lamda_l, valorespropios_copia[indice][2][indice3])
                                            if solucion_parcial.has(I):
                                                Soluciones[indice][indice1][indice2][indice3] = solucion_parcial.rewrite(cos)
                                            else:
                                                Soluciones[indice][indice1][indice2][indice3] = solucion_parcial
                        else: 
                            # Cuando no hay dependencia entre las tres expresiones de valores propios.
                            for indice1, indice2 in [(x, y) for x in range(len(valorespropios_copia[indice][0])) for y in range(len(valorespropios_copia[indice][1]))]:
                                for indice3 in range(len(valorespropios_copia[indice][2])):
                                    solucion_parcial = 0
                                    indice_auxiliar = 0
                                    for funcion_espacial in funciones_espaciales[indice]:
                                        # Cuando no hay dependencia temporal.
                                        print(coeficientes[indice_auxiliar])
                                        coeficiente = np.round(float(coeficientes[indice_auxiliar].subs(lamda, valorespropios_copia[indice][0][indice1]).subs(mu, valorespropios_copia[indice][1][indice2]).subs(nu, valorespropios_copia[indice][2][indice3]).doit()), precision_copia)
                                        solucion_parcial = solucion_parcial + coeficiente*funcion_espacial
                                        indice_auxiliar += 1
                                    
                                    solucion_parcial = solucion_parcial.subs(lamda_n, valorespropios_copia[indice][0][indice1]).subs(lamda_m, valorespropios_copia[indice][1][indice2]).subs(lamda_l, valorespropios_copia[indice][2][indice3])
                                    if solucion_parcial.has(I):
                                        Soluciones[indice][indice1][indice2][indice3] = solucion_parcial.rewrite(cos)
                                    else:
                                        Soluciones[indice][indice1][indice2][indice3] = solucion_parcial

                self.envioActualizacion("Calculando Solución del Subproblema ({0}/{1})".format(indice+1, int(numeroentradas)))
            
                # Suma de TODAS las subsoluciones encontradas para este subproblema.
                SolucionSubproblema = 0 
                for indice1 in range(len(Soluciones[indice])):
                    for indice2 in range(len(Soluciones[indice][indice1])):
                        if len(valorespropios_copia[indice]) == 2:
                            # Cuando solo se tienen dos valores propios.
                            if Soluciones[indice][indice1][indice2].has(I):
                                SolucionSubproblema = SolucionSubproblema + simplify(Soluciones[indice][indice1][indice2].rewrite(cos))
                            else:
                                SolucionSubproblema = SolucionSubproblema + Soluciones[indice][indice1][indice2]
                        else:
                            # Cuando se tienen tres valores propios.
                            for indice3 in range(len(Soluciones[indice][indice1][indice2])):
                                if Soluciones[indice][indice1][indice2][indice3].has(I):
                                    SolucionSubproblema = SolucionSubproblema + simplify(Soluciones[indice][indice1][indice2][indice3].rewrite(cos))
                                else:
                                    SolucionSubproblema = SolucionSubproblema + Soluciones[indice][indice1][indice2][indice3]
                if SolucionSubproblema.has(I):
                    SolucionesSubproblemas[indice] = simplify(SolucionSubproblema.rewrite(cos))
                else:
                    SolucionesSubproblemas[indice] = SolucionSubproblema
            
            self.envioActualizacion("Calculando Solución Completa")

            # Suma de las soluciones de TODOS los subproblemas.
            SolucionEncontrada = 0
            for indice in range(len(SolucionesSubproblemas)):
                SolucionEncontrada = SolucionEncontrada + SolucionesSubproblemas[indice]
            
            print(SolucionEncontrada)

            # Envio de la información encontrada a la pantalla principal.
            # Conversión de la solución a una función de numpy.
            self.ui.Solucion_funcion = sp.lambdify(self.ui.Simbolos, SolucionEncontrada)
            self.ui.Soluciones = Soluciones
            self.ui.SolucionesSubproblemas = SolucionesSubproblemas
            self.ui.Coeficientes = coeficientes_copia
            self.ui.FuncionesEspaciales = funciones_espaciales
            if self.ui.dependencia_tiempo:
                self.ui.FuncionesTemporales = funciones_temporales
            self.ui.ValoresPropios = valorespropios_copia
            self.ui.dependencia = dependencia
            self.ui.bidependencia = bidependencia
            self.ui.indicesdependencia = indicesdependencia
            self.ui.invertir = invertir

            self.envioActualizacion("Evaluando Solución")

            # Determinación de la calidad (puntos por unidad de longitud).
            if self.ui.Calidad:
                aumento = 0.01
            else:
                aumento = 0.03
            
            # Cálculo de las particiones de cada dominio.
            self.ui.ParticionesDominios = []
            estructura = []
            indice = 0 
            for simbolo in self.ui.Simbolos:
                if simbolo != t:
                    particion = np.arange(float(self.ui.Dominios[indice][0])-0.005, float(self.ui.Dominios[indice][1]) + 0.005, step=aumento)
                    if particion[-1] < float(self.ui.Dominios[indice][1]):
                        particion = np.append(particion, float(self.ui.Dominios[indice][1])+0.005)
                    else:
                        particion[-1] = float(self.ui.Dominios[indice][1])+0.005
                    self.ui.ParticionesDominios.append(particion)
                    estructura.append(int(len(self.ui.ParticionesDominios[-1])))
                else:
                    estructura.append(int(float(self.ui.Dominios[indice][0])*25) + 1)
                    self.ui.Ui_Grafica.t_grid = np.arange(0, float(self.ui.Dominios[indice][0]) + 0.04, step=0.04)
                indice += 1

            # Cálculo de los valores de la solución en cada uno de los puntos de la partición del espacio.
            self.ui.MatrizResultados = np.zeros(estructura).T
            if self.ui.dependencia_tiempo:
                for indice1 in range(0, len(self.ui.Ui_Grafica.t_grid)):
                    for indice2 in range(0, len(self.ui.ParticionesDominios[0])):
                        if len(self.ui.ParticionesDominios) == 2:
                            for indice3 in range(0, len(self.ui.ParticionesDominios[1])):
                                self.ui.MatrizResultados[indice1][indice3][indice2] = self.ui.Solucion_funcion(self.ui.ParticionesDominios[0][indice2], self.ui.ParticionesDominios[1][indice3], self.ui.Ui_Grafica.t_grid[indice1])
                        else:
                            self.ui.MatrizResultados[indice1][indice2] = self.ui.Solucion_funcion(self.ui.ParticionesDominios[0][indice2], self.ui.Ui_Grafica.t_grid[indice1])
            else:
                for indice1 in range(0, len(self.ui.ParticionesDominios[0])):
                    for indice2 in range(0, len(self.ui.ParticionesDominios[1])):
                        if len(self.ui.ParticionesDominios) == 3:
                            for indice3 in range(0, len(self.ui.ParticionesDominios[2])):
                                self.ui.MatrizResultados[indice3][indice2][indice1] = self.ui.Solucion_funcion(self.ui.ParticionesDominios[0][indice1], self.ui.ParticionesDominios[1][indice2], self.ui.ParticionesDominios[2][indice3])
                        else:
                            self.ui.MatrizResultados[indice2][indice1] = self.ui.Solucion_funcion(self.ui.ParticionesDominios[0][indice1], self.ui.ParticionesDominios[1][indice2])

            self.signals.finalizar_signal.emit("Solución Calculada")
        except:
            # Interpretación del error ocurrido.
            tipoError, explicacion, line = sys.exc_info()[:3]
            print(tipoError)
            print(explicacion)
            print(line.tb_lineno)

            typeError = "Error -- No calculable"
            Error = "No se pudo obtener un resultado."

            self.signals.error_signal.emit((typeError, Error))
        finally:
            # Habilitación de los botones de interpretación y limpieza, así como de la ventana principal
            self.ui.Interpretar.setEnabled(True)
            self.ui.Interpretar.setStyleSheet("color: rgb(234, 237, 239); background-color: rgb(11, 61, 98);")
            self.ui.Interpretar.setText("Actualizar")
            self.ui.Interpretar.setShortcut("Ctrl + I")
            self.ui.Visualizar.setEnabled(True)
            self.ui.Visualizar.setStyleSheet("color: rgb(234, 237, 239); background-color: rgb(11, 61, 98);")
            self.ui.Limpiar.setEnabled(True)
            self.ui.Limpiar.setStyleSheet("color: rgb(234, 237, 239); background-color: rgb(11, 61, 98);")
            self.ui.centralwidget.setEnabled(True)

class TrabajoVisualizacion(QtCore.QRunnable):
    """Ejecutable para realizar el procesamiento en paralelo de la creación y visualización de la gráfica."""

    def __init__(self, ui_informacion):
        """Definicion de la información a utilizar y las señales necesarias para la comunicación."""

        super(self.__class__, self).__init__()
        self.ui = ui_informacion
        self.signals = Indicadores()
        self.ui.signals.avanzar_signal.connect(self.signals.avanzar_signal)
        self.ui.signals.finalizar_signal.connect(self.signals.finalizar_signal)

    @QtCore.pyqtSlot()    
    def run(self):
        try: 
            QtCore.QThread.msleep(500)
            # Edición de las herramientas de acuerdo a la información del problema.
            self.ui.editarOpciones()

            QtCore.QThread.msleep(500)
            # Creación de la gráfica.
            self.ui.crearGrafica()

            self.ui.ValorPropio1.setValue(self.ui.ValorPropio1.minimum())
            self.ui.ValorPropio2.setValue(self.ui.ValorPropio2.minimum())
            self.ui.ValorPropio3.setValue(self.ui.ValorPropio3.minimum())
            self.ui.despliegueCoeficiente_CambioExpresion(1)
            
            self.signals.finalizar_signal.emit("Gráfica Lista")
        except:
            # Interpretación del tipo de error.
            tipoError, explicacion, line = sys.exc_info()[:3]
            print(tipoError)
            print(explicacion)
            print(line.tb_lineno)

            typeError = "Error -- Graficación Fallida"
            Error = "No se pudo obtener una gráfica."

            self.signals.error_signal.emit((typeError, Error))

class TrabajoGuardado(QtCore.QRunnable):
    """Ejecutable para realizar el procesamiento en paralelo del guardado de animaciones."""

    def __init__(self, ui_informacion):
        """Definicion de la información a utilizar y las señales necesarias para la comunicación."""

        super(self.__class__, self).__init__()
        self.ui = ui_informacion
        self.signals = Indicadores()
        self.ui.signals.avanzar_signal.connect(self.signals.avanzar_signal)
        self.ui.signals.finalizar_signal.connect(self.signals.finalizar_signal)

    @QtCore.pyqtSlot()    
    def run(self):
        try: 
            self.ui.guardarAnimacion()
            QtCore.QThread.msleep(500)
            self.signals.finalizar_signal.emit("Animación Guardada")
        except:
            tipoError, explicacion, line = sys.exc_info()[:3]
            print(tipoError)
            print(explicacion)
            print(line.tb_lineno)

            typeError = "Error -- Animación Fallida"
            Error = "No se pudo obtener una animación."

            self.ui.Animacion.detener()
            self.signals.error_signal.emit((typeError, Error))
        finally:
            self.ui.GuardarAnimacion.setEnabled(True)
            self.ui.GuardarAnimacion.setShortcut("Ctrl+S")
            self.ui.CurvasNivelAuto.setShortcut("Ctrl+A")
            self.ui.CurvasNivelEspecificas.setShortcut("Ctrl+E")
            self.ui.GuardarAnimacion.setStyleSheet(u"color: rgb(246, 247, 247); background-color: rgb(11, 61, 98);")

class TrabajoCambioProyeccion(QtCore.QRunnable):
    """Ejecutable para realizar el procesamiento en paralelo del cambio entre proyecciones."""

    def __init__(self, ui_informacion):
        """Definicion de la información a utilizar y las señales necesarias para la comunicación."""

        super(self.__class__, self).__init__()
        self.ui = ui_informacion
        self.signals = Indicadores()
        self.ui.signals.avanzar_signal.connect(self.signals.avanzar_signal)
        self.ui.signals.finalizar_signal.connect(self.signals.finalizar_signal)

    @QtCore.pyqtSlot()    
    def run(self):
        try: 
            self.ui.intercambiarProyeccion()
            QtCore.QThread.msleep(500)
            self.signals.finalizar_signal.emit("Intercambio de Proyección Finalizado")
        except:
            tipoError, explicacion, line = sys.exc_info()[:3]
            print(tipoError)
            print(explicacion)
            print(line.tb_lineno)

            typeError = "Error -- Intercambio Fallido"
            Error = "No se pudo obtener intercambiar entre proyección y gráfica tridimensional o viceversa."

            self.signals.error_signal.emit((typeError, Error))
        finally:
            self.ui.GuardarAnimacion.setShortcut("Ctrl+S")
            self.ui.CurvasNivelAuto.setShortcut("Ctrl+A")
            self.ui.CurvasNivelEspecificas.setShortcut("Ctrl+E")
        
class TrabajoCurvasNivel(QtCore.QRunnable):
    """Ejecutable para realizar el procesamiento en paralelo para el cálculo y visualización de las curvas de nivel."""

    def __init__(self, ui_informacion):
        """Definicion de la información a utilizar y las señales necesarias para la comunicación."""

        super(self.__class__, self).__init__()
        self.ui = ui_informacion
        self.ui.carga = True
        self.signals = Indicadores()
        self.ui.signals.avanzar_signal.connect(self.signals.avanzar_signal)
        self.ui.signals.finalizar_signal.connect(self.signals.finalizar_signal)

    @QtCore.pyqtSlot()    
    def run(self):
        try: 
            self.ui.interpretacionCurvasNivel()
            QtCore.QThread.msleep(500)
            self.signals.finalizar_signal.emit("Construcción de Curvas de Nivel Finalizada")
            self.ui.carga = False
        except:
            tipoError, explicacion, line = sys.exc_info()[:3]
            print(tipoError)
            print(explicacion)
            print(line.tb_lineno)

            typeError = "Error -- Graficación de Curvas Fallida"
            Error = "No se pudo graficar o eliminar las curvas de nivel."

            self.signals.error_signal.emit((typeError, Error))
        finally:
            self.ui.GuardarAnimacion.setShortcut("Ctrl+S")
            self.ui.CurvasNivelAuto.setShortcut("Ctrl+A")
            self.ui.CurvasNivelEspecificas.setShortcut("Ctrl+E")

class TrabajoCorteEspecifico(QtCore.QRunnable):
    """Ejecutable para realizar el procesamiento en paralelo del cálculo y visualización del corte espacial o temporal requerido."""

    def __init__(self, ui_informacion):
        """Definicion de la información a utilizar y las señales necesarias para la comunicación."""

        super(self.__class__, self).__init__()
        self.ui = ui_informacion
        self.signals = Indicadores()
        self.ui.signals.avanzar_signal.connect(self.signals.avanzar_signal)
        self.ui.signals.finalizar_signal.connect(self.signals.finalizar_signal)

    @QtCore.pyqtSlot()    
    def run(self):
        try: 
            self.ui.cambiarValorCoordenadaFija()
            QtCore.QThread.msleep(500)
            self.signals.finalizar_signal.emit("Graficación Finalizada")
        except:
            tipoError, explicacion, line = sys.exc_info()[:3]
            print(tipoError)
            print(explicacion)
            print(line.tb_lineno)

            if tipoError == NoNumeroError:
                typeError = "Error -- Valor No Real"
                Error = "El valor introducido no es un número real."
            elif tipoError == ValorFueraDominioError:
                typeError = "Error -- Valor Fuera del Dominio"
                Error = "El valor introducido no se encuentra dentro del dominio de la variable."
            else:
                typeError = "Error -- Graficación de Corte Fallida"
                Error = "No se pudo graficar el corte deseado. Revisa la entrada o intenta otra vez."

            self.signals.error_signal.emit((typeError, Error))
        finally:
            self.ui.GuardarAnimacion.setShortcut("Ctrl+S")
            self.ui.CurvasNivelAuto.setShortcut("Ctrl+A")
            self.ui.CurvasNivelEspecificas.setShortcut("Ctrl+E")

class TrabajoCambiarCoordenada(QtCore.QRunnable):
    """Ejecutable para realizar el procesamiento en paralelo del cambio de coordenada fija en la visualización tridimensional."""

    def __init__(self, ui_informacion):
        """Definicion de la información a utilizar y las señales necesarias para la comunicación."""

        super(self.__class__, self).__init__()
        self.ui = ui_informacion
        self.signals = Indicadores()
        self.ui.signals.avanzar_signal.connect(self.signals.avanzar_signal)
        self.ui.signals.finalizar_signal.connect(self.signals.finalizar_signal)

    @QtCore.pyqtSlot()    
    def run(self):
        try: 
            self.ui.cambiarCoordenadaFija()
            QtCore.QThread.msleep(500)
            if self.ui.valorerroneo:
                typeError = "Error -- Valor Fuera del Dominio"
                Error = "El valor introducido no se encuentra dentro del dominio de la variable."
                self.signals.error_signal.emit((typeError, Error))
            else:
                self.signals.finalizar_signal.emit("Graficación Finalizada")
        except:
            tipoError, explicacion, line = sys.exc_info()[:3]

            typeError = "Error -- Graficación de Corte Fallida"
            Error = "No se pudo graficar el corte deseado."

            self.signals.error_signal.emit((typeError, Error))
        finally: 
            self.ui.GuardarAnimacion.setShortcut("Ctrl+S")
            self.ui.CurvasNivelAuto.setShortcut("Ctrl+A")
            self.ui.CurvasNivelEspecificas.setShortcut("Ctrl+E")

class Indicadores(QtCore.QObject):
    """Clase que contiene las señales necesarias para la ejecución de los trabajos."""
    # La definición de esta clase para el envio de señales de comunicación entre las funciones/trabajos de la app fue tomada y modificada de S. Nick. (13 de agosto de 2020). Respuesta a la pregunta "How to display a loading animated gif while a code is executing in backend of my Python Qt5 UI?". stackoverflow. https://stackoverflow.com/a/63395218
    # El uso de esta respuesta está licenciado bajo la licencia CC BY-SA 4.0 la cual puede ser consultada en https://creativecommons.org/licenses/by-sa/4.0/

    finalizar_signal = pyqtSignal(str)
    avanzar_signal = pyqtSignal(str)
    error_signal = pyqtSignal(tuple)
