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
