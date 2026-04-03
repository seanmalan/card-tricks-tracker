#!/bin/bash
# Build a standalone Mac/Linux app
# Linux pre-req: sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.0

set -e
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pyinstaller

pyinstaller \
  --onefile \
  --windowed \
  --name "Card Magic Tracker" \
  --add-data "static:static" \
  --collect-all pywebview \
  --collect-all flask \
  main.py

deactivate
echo ""
echo "Done! App is at: dist/Card Magic Tracker"
