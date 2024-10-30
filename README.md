<p align="center">
    <a href="https://github.com/LuisNavaFisBio/GraPhEr_Ecuaciones-Diferenciales-Parciales-Separables">
        <img src="https://github.com/LuisNavaFisBio/GraPhEr_Ecuaciones-Diferenciales-Parciales-Separables/blob/main/LogoPrincipal.png">
    </a>
</p>

[![GNU GENERAL PUBLIC LICENSE](https://www.gnu.org/graphics/gplv3-127x51.png?style=flat)](https://www.gnu.org/licenses/gpl-3.0.html#license-text)

GraPhEr es una aplicación de graficación, visualización y exploración de las soluciones de ecuaciones diferenciales parciales que admitan una resolución en variables separadas.

# Requerimientos

GrahPhEr requiere [Python 3](https://www.python.org/downloads/) o superior. 

En Windows es necesario instalar Python con las opciones “Use admin privileges when installing py.exe” y “Add python.exe to PATH”, antes de finalizar elegir la opción “Disable PATH limit”.

---

Adicionalmente, requiere la instalación de [FFMPEG](https://ffmpeg.org/download.html) en el sistema (las instrucciones de instalación para diferentes sistemas se pueden encontrar en 
[ffmpeg-python](https://github.com/kkroening/ffmpeg-python)). Este es un software necesario para crear los videos de las animaciones, si no planea exportar las animaciones no es necesaria su instalación.

El procedimiento en Windows es el siguiente:
1. Descargar el archivo ffmpeg-release-full.7z de [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/) y descomprimirlo.
2. Agregar los archivos ejecutables de la carpeta *bin* en una carpeta que se llame *FFMPEG* y pasar dicha carpeta a *Archivos de Programa* del sistema.
3. Posteriormente añadir la dirección de *FFMPEG* a PATH en las variables de entorno del sistema.

---

Finalmente, requiere la instalación de varias librerías de Python. Para ello es necesario abrir la consola del sistema (dependiendo del sistema operativo y de preferencia en modo administrador) y correr el comando (o equivalente según el sistema operativo; el objetivo es añadir todas estas librerías a Python).

```
pip install matplotlib, PyQt5, plasTeX, sympy, scipy, PySide6, ffmpeg-python
```

# Ejecución de la aplicación

Después de la instalación, abrir el archivo “PantallaInicialInterfaz.py” con el IDLE de Python y correr el archivo en la pestaña “Run”. O correr el archivo a través de la terminal del sistema operativo.

Para tener una ejemplificación del desempeño de la app, se puede copiar y pegar en los respectivos campos de la ventana inicial la información siguiente:

```
Número de Dimensiones Espaciales    2
Dominio x    0:pi        Dominio y    0:pi
Condiciones iniciales y/o de frontera    x*sin(x);x*sin(x);y*(pi-y);y*(y-pi)
Número de subproblemas    4

Solución del Subproblema #1
Valores Propios    n        Número de Términos    1:10
Coeficientes    Int[2*f_1*sin(lamda_n*x)/(pi*sinh(lamda_n*pi)),x]
Funciones Espaciales    sin(lamda_n*x)*sinh(lamda_n*(pi-y))

Solución del Subproblema #2
Valores Propios    n        Número de Términos    1:10
Coeficientes    Int[2*f_2*sin(lamda_n*x)/(pi*sinh(lamda_n*pi)),x]
Funciones Espaciales    sin(lamda_n*x)*sinh(lamda_n*y)

Solución del Subproblema #3
Valores Propios    n        Número de Términos    1:10
Coeficientes    Int[2*f_3*sin(lamda_n*y)/(pi*sinh(lamda_n*pi)),y]
Funciones Espaciales    sin(lamda_n*y)*sinh(lamda_n*(pi-x))

Solución del Subproblema #4
Valores Propios    n        Número de Términos    1:10
Coeficientes    Int[2*f_4*sin(lamda_n*y)/(pi*sinh(lamda_n*pi)),y]
Funciones Espaciales    sin(lamda_n*y)*sinh(lamda_n*x)
```

Posteriormente se debe presionar el botón **Interpretar** y esperar a que se realice la interpretación y se muestre la ventana de visualización de la entrada del usuario. En ella se puede observar la entrada en formato LaTeX como se aprecia en la siguiente imagen

<p align="center">
    <a>
        <img src="https://github.com/LuisNavaFisBio/GraPhEr_Ecuaciones-Diferenciales-Parciales-Separables/blob/main/EjemploInterpretacion.bmp" style="width: 950px; height: 271px;">
    </a>
</p>

Si la interpretación es correcta, se debe presionar el botón **Resolver** en esta ventana de visualización, con esto se procede a la realización de los cálculos necesarios para tener la aproximación numérica de la solución. Una vez finalizados los cálculos se abre la ventana de graficación (la vista inicial se muestra en la siguiente imagen)

<p align="center">
    <a>
        <img src="https://github.com/LuisNavaFisBio/GraPhEr_Ecuaciones-Diferenciales-Parciales-Separables/blob/main/EjemploVentanaGraficacion.png">
    </a>
</p>

En esta ventana se puede obtener el valor de la solución en los distintos puntos del dominio, el valor de los coeficientes de cada uno de los términos considerados, la visualización de las curvas de nivel y, en este caso, también se puede realizar el cambio entre la vista 3D y una vista cenital.

# Documentación

No existe una documentación estrictamente hablando, sin embargo, se puede consultar una explicación del desarrollo de la aplicación, así como ejemplos de utilización en el siguiente documento:


# Contribuciones
Cualquier modificación sugerida es aceptada, por favor explique el motivo del cambio y ejemplos del efecto que tendría en la aplicación. 

# Licencia
Este proyecto se distribuye con la Licencia Pública General de GNU, la cual puede ser consultada en el archivo **COPYING** o en [GNU](https://www.gnu.org/licenses/). 
