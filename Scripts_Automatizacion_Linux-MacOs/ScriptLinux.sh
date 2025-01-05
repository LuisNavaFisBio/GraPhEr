#!/bin/sh
sudo apt-get install python3-pip ffmpeg python3-venv texlive-latex-base && python3 -m venv grapher_env \
source "./grapher_env/bin/activate" 
pip install -U --only-binary :all: matplotlib==3.7.5 PyQt5 plasTeX sympy scipy PySide6 ffmpeg-python pyqtwebengine && deactivate 