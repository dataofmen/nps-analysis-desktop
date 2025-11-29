#!/bin/bash
# Build the backend executable using PyInstaller

# Ensure we are in the backend directory
cd "$(dirname "$0")"

# Install requirements just in case (though we checked)
# pip install -r requirements.txt
# pip install pyinstaller

# Run PyInstaller
# --onefile: Create a single executable file
# --name: Name of the executable
# --clean: Clean cache
# --hidden-import: Explicitly import dependencies that might be missed
pyinstaller --onedir \
    --name nps-backend \
    --clean \
    --hidden-import=uvicorn \
    --hidden-import=pandas \
    --hidden-import=fastapi \
    --hidden-import=python_multipart \
    --hidden-import=openpyxl \
    --hidden-import=chardet \
    --hidden-import=requests \
    --hidden-import=encodings \
    --collect-all uvicorn \
    --collect-all pandas \
    main.py

echo "Build complete. Executable is in backend/dist/nps-backend"
