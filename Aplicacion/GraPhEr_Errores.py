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

# Este archivo contiene las clases de los errores definidos.
# La definición de los errores personalizados se basa en Programiz. (s. f.). Python Custom Exceptions. Programiz. https://www.programiz.com/python-programming/user-defined-exception#google_vignette

class ComandoInvalidoError(Exception):
    """Este error surge cuando en la entrada del usuario se ingresa un comando en un lugar inválido."""
    pass

class DimensionError(Exception):
    """Este error surge cuando no se establece una dependencia temporal cuando solo se tiene una coordenada espacial."""
    pass

class EntradaVaciaError(Exception):
    """Este error surge cuando hay un campo vacio en la entrada del usuario."""
    pass

class ExcesoEntradaError(Exception):
    """Este error surge cuando hay una incoherencia entre el número de conjuntos de valores propios y el número de términos requeridos o cuando en algún campo de entrada se especifican más valores de los necesarios."""
    pass

class ExtremoFaltanteError(Exception):
    """Este error surge cuando hay en algún dominio espacial hace falta alguno de los extremos."""
    pass

class ExcesoIncognitasError(Exception):
    """Este error surge cuando en la entrada del usuario hay alguna expresión que tiene variables distintas a las espaciales y/o la temporal."""
    pass

class NoExistenciaError(Exception):
    """Este error surge cuando no hay valores propios que satisfagan ser menores a un determinado número."""
    pass

class NoNumeroError(Exception):
    """Este error surge cuando, en su caso, la entrada no corresponde a un número."""
    pass

class ValorFueraDominioError(Exception):
    """Este error surge cuando se quiere un corte que no corresponde a un valor dentro del dominio de la coordenada fija."""
    pass
