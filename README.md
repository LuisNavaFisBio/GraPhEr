<p align="center">
    <a href="https://github.com/LuisNavaFisBio/GraPhEr_Ecuaciones-Diferenciales-Parciales-Separables">
        <img src="https://github.com/LuisNavaFisBio/GraPhEr_Ecuaciones-Diferenciales-Parciales-Separables/blob/main/LogoPrincipal.png">
    </a>
</p>

[![GNU GENERAL PUBLIC LICENSE](https://www.gnu.org/graphics/gplv3-127x51.png?style=flat)](https://www.gnu.org/licenses/gpl-3.0.html#license-text)

GraPhEr es una aplicación de graficación, visualización y exploración de las soluciones de ecuaciones diferenciales parciales que admitan una resolución en variables separadas.

## Requerimientos

GrahPhEr requiere [Python 3](https://www.python.org/downloads/) o superior. 

En Windows es necesario instalar Python con las opciones “Use admin privileges when installing py.exe” y “Add python.exe to PATH”, antes de finalizar elegir la opción “Disable PATH limit”.

---

Adicionalmente, requiere la instalación de [FFMPEG](https://ffmpeg.org/download.html) en el sistema (las instrucciones de instalación para diferentes sistemas se pueden encontrar en 
[ffmpeg-python](https://github.com/kkroening/ffmpeg-python)). Este es un software para grabar los animaciones.

El procedimiento en Windows es el siguiente:
1. Descargar el archivo ffmpeg-release-full.7z de [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/) y descomprimirlo.
2. Agregar los archivos ejecutables de la carpeta *bin* en una carpeta que se llame *FFMPEG* y pasar dicha carpeta a la carpeta de *archivos de programa* del sistema.
3. Posteriormente añadir la dirección de la carpeta en donde están los ejecutables copiados a PATH en las variables de entorno del sistema.

---

Finalmente, requiere la instalación de varias librerías de Python. Para ello es necesario abrir la consola del sistema (dependiendo del sistema operativo y de preferencia en modo administrador) y correr el comando (o equivalente según el sistema operativo; el objetivo es añadir todas estas librerías a Python).

```
pip install matplotlib, PyQt5, plasTeX, sympy, scipy, PySide6, ffmpeg-python
```

Después de la instalación, abrir el archivo “PantallaInicialInterfaz.py” con el IDLE de Python y correr el archivo en la pestaña “Run”.



System requirements are [FFmpeg](https://ffmpeg.org/), [OpenGL](https://www.opengl.org/) and [LaTeX](https://www.latex-project.org) (optional, if you want to use LaTeX).
For Linux, [Pango](https://pango.gnome.org) along with its development headers are required. See instruction [here](https://github.com/ManimCommunity/ManimPango#building).


## Ejecución de la aplicación
Try running the following:
```sh
manimgl example_scenes.py OpeningManimExample
```
This should pop up a window playing a simple scene.

Look through the [example scenes](https://3b1b.github.io/manim/getting_started/example_scenes.html) to see examples of the library's syntax, animation types and object types. In the [3b1b/videos](https://github.com/3b1b/videos) repo, you can see all the code for 3blue1brown videos, though code from older videos may not be compatible with the most recent version of manim. The readme of that repo also outlines some details for how to set up a more interactive workflow, as shown in [this manim demo video](https://www.youtube.com/watch?v=rbu7Zu5X1zI) for example.

When running in the CLI, some useful flags include:
* `-w` to write the scene to a file
* `-o` to write the scene to a file and open the result
* `-s` to skip to the end and just show the final frame.
    * `-so` will save the final frame to an image and show it
* `-n <number>` to skip ahead to the `n`'th animation of a scene.
* `-f` to make the playback window fullscreen

Take a look at custom_config.yml for further configuration.  To add your customization, you can either edit this file, or add another file by the same name "custom_config.yml" to whatever directory you are running manim from.  For example [this is the one](https://github.com/3b1b/videos/blob/master/custom_config.yml) for 3blue1brown videos.  There you can specify where videos should be output to, where manim should look for image files and sounds you want to read in, and other defaults regarding style and video quality.

### Documentation
Documentation is in progress at [3b1b.github.io/manim](https://3b1b.github.io/manim/). And there is also a Chinese version maintained by [**@manim-kindergarten**](https://manim.org.cn): [docs.manim.org.cn](https://docs.manim.org.cn/) (in Chinese).

[manim-kindergarten](https://github.com/manim-kindergarten/) wrote and collected some useful extra classes and some codes of videos in [manim_sandbox repo](https://github.com/manim-kindergarten/manim_sandbox).


## Contributing
Is always welcome.  As mentioned above, the [community edition](https://github.com/ManimCommunity/manim) has the most active ecosystem for contributions, with testing and continuous integration, but pull requests are welcome here too.  Please explain the motivation for a given change and examples of its effect.


## Licencia
Este proyecto se distribuye con la Licencia Pública General de GNU, la cual puede ser consultada en el archivo **COPYING**.
