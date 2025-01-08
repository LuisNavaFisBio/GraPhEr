#!/bin/sh
sudo apt install ffmpeg
sudo rpm -i "./GraPhEr_V_1-0.rpm"
sudo chown -R $USER /usr/bin/GraPhEr/ && sudo chmod +x /usr/bin/GraPhEr/_internal/PyQt5/Qt5/libexec/QtWebEngineProcess

