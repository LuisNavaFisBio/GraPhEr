<p align="center">
    <a href="https://github.com/LuisNavaFisBio/GraPhEr_Ecuaciones-Diferenciales-Parciales-Separables">
        <img src="https://github.com/LuisNavaFisBio/GraPhEr_Ecuaciones-Diferenciales-Parciales-Separables/blob/main/LogoPrincipal.png">
    </a>
</p>

[![GNU GENERAL PUBLIC LICENSE](https://www.gnu.org/graphics/gplv3-127x51.png?style=flat)](https://www.gnu.org/licenses/gpl-3.0.html#license-text)

GraPhEr es una aplicación de graficación, visualización y exploración de las soluciones de ecuaciones diferenciales parciales que admitan una resolución en variables separadas.

# Última actualización (02 de diciembre de 2024)

- Implementación de algoritmos para visualizar modo por modo o visualizar soluciones parciales de la entrada ingresada.
- Implementación de algoritmos para importar y exportar entradas válidas para la aplicación.

# Documentación

La documentación puede ser consultada en el archivo [**ManualUsuario.pdf**](https://github.com/LuisNavaFisBio/GraPhEr/blob/main/ManualUsuario.pdf) en este repositorio. En ella se encuentran las instrucciones para la instalación/ejecución de la aplicación, la sintaxis requerida en los campos de entrada y la guía de interacción con la interfaz.

# Ejecución

La aplicación puede ser ejecutada desde los archivos *.py* encontrados en la carpeta **Aplicación** o puede ser instalada (esta opción solo se encuentra disponible actualmente en sistemas Windows).

### Requerimientos para la ejecución desde los archivos *.py*.

GrahPhEr requiere [Python 3](https://www.python.org/downloads/) o superior. En sistemas Linux este programa viene preinstalado, mientras que en Windows/MacOs es necesario realizar la descarga del instalador correspondiente. Revisar la documentación para una correcta instalación de Python. 

Adicionalmente, requiere la instalación de varias librerías de Python. Para ello es necesario abrir la consola del sistema (dependiendo del sistema operativo y de preferencia en modo administrador) y correr el comando:

```
# Windows
pip install -U --only-binary :all: matplotlib==3.7.5, PyQt5, plasTeX, sympy, scipy, PySide6, ffmpeg-python, pyqtwebengine

# Linux/MacOs
pip install -U --only-binary :all: matplotlib==3.7.5 PyQt5 plasTeX sympy scipy PySide6 ffmpeg-python pyqtwebengine
```

*Nota: Se necesita una versión inferior o igual a la versión 3.7.5 de la librería MatPlotLib por la existencia de un bug en versiones superiores de dicha librería que impide la graficación de curvas de nivel en la vista tridimensional.*

Adicionalmente, requiere la instalación de [FFMPEG](https://ffmpeg.org/download.html) en el sistema. Este es un software necesario para crear los videos de las animaciones, si no planea exportar las animaciones no es necesaria su instalación.

### Requerimientos para la instalación (actualmente solo disponible en Windows).

Cuando se utiliza el instalador no es necesario ningún programa adicional.

## Ejecución de la aplicación

Consultar el archivo [**ManualUsuario.pdf**](https://github.com/LuisNavaFisBio/GraPhEr/blob/main/ManualUsuario.pdf) para conocer a detalle los pasos para una correcta ejecución de la aplicación. A continuación se presenta un ejemplo sencillo para mostrar el uso de la aplicación:

---
---

### Ejemplo de uso

Para tener una ejemplificación del desempeño de la app, se puede descargar cualquiera de los archivos de texto disponibles en las carpetas **EjemplosRecopilados_Asmar2016**, **EjemplosRecopilados_Haberman2004** o **EjemplosResueltos**. Una vez inicializada la aplicación, importar la entrada contenida en el archivo de texto utilizando el botón **Importar**.

Posteriormente presionar el botón **Interpretar** y esperar a que se realice la interpretación y se muestre la ventana de visualización de la entrada del usuario. En ella se puede observar la entrada en formato LaTeX como se aprecia en la siguiente imagen

<p align="center">
    <a>
        <img src="https://github.com/LuisNavaFisBio/GraPhEr_Ecuaciones-Diferenciales-Parciales-Separables/blob/main/EjemploInterpretacion.bmp" style="width: 950px; height: 400px;">
    </a>
</p>

Si la interpretación es correcta, se debe presionar el botón **Resolver** en esta ventana de visualización, con esto se procede a la realización de los cálculos necesarios para tener la aproximación numérica de la solución. Una vez finalizados los cálculos se abre la ventana de graficación con el botón **Visualizar** (la vista inicial se muestra en la siguiente imagen)

<p align="center">
    <a>
        <img src="https://github.com/LuisNavaFisBio/GraPhEr_Ecuaciones-Diferenciales-Parciales-Separables/blob/main/EjemploVentanaGraficacion.png">
    </a>
</p>

En esta ventana se puede obtener el valor de la solución en los distintos puntos del dominio, el valor de los coeficientes de cada uno de los términos considerados, la visualización de las curvas de nivel y, en este caso, también se puede realizar el cambio entre la vista 3D y una vista cenital. Además, la aplicación permite intercambiar entre los modos: 

- **_Solución completa_**, considera toda la solución ingresada por el usuario.
- **_Solución parcial_**, considera solo una parte de la solución ingresada.
- **_Modo por modo_**, considera cada subsolución ingresada por separado.

**Nota:** En el siguiente enlace [Ejemplos GraPher](https://youtube.com/playlist?list=PLDXxCxAJtfBglyxTJl_z-5euuph1bhJEH&si=NSw4tSfEgUvtZpNV) se pueden encontrar videos alojados en YouTube que muestran las animaciones obtenidas para varios problemas resueltos, las entradas para estos problemas se encuentran en la carpeta EjemplosResueltos.

---
---

# Contribuciones
Cualquier modificación sugerida es aceptada, por favor explique el motivo del cambio y ejemplos del efecto que tendría en la aplicación. 

# Licencia
Este proyecto (nombre, código, iconos, logo y animaciones de carga) se distribuye con la versión 3 de la Licencia Pública General de GNU, la cual puede ser consultada en el archivo **COPYING** o en [GNU](https://www.gnu.org/licenses/). 
