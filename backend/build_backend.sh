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
    --paths . \
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
    --hidden-import=data_processing \
    --hidden-import=weighting \
    --hidden-import=analysis \
    --hidden-import=food_nps \
    --collect-all uvicorn \
    --collect-all pandas \
    main.py

# Manually copy local modules to _internal to ensure they are found
echo "Copying local modules to _internal..."
cp data_processing.py weighting.py analysis.py food_nps.py dist/nps-backend/_internal/

echo "Build complete. Executable is in backend/dist/nps-backend"
