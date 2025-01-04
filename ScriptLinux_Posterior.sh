#!/bin/sh
export 'QT_QPA_PLATFORM=xcb' && export 'XDG_SESSION_TYPE=xcb'
source "./grapher_env/bin/activate" && python3 GraPhEr/GraPhEr-main/Aplicacion/GraPhEr_ArchivoPrincipal.py \
deactivate \\
