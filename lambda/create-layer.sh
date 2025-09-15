#!/bin/bash
echo "Creating Lambda layer..."

# Create layer structure
mkdir -p python
cd python

# Install dependencies for layer
pip install Pillow==10.0.1 pytesseract==0.3.10 pdf2image==1.16.3 -t .

# Go back and create layer ZIP
cd ..
zip -r ocr-dependencies-layer.zip python/

# Clean up
rm -rf python

echo "Layer package created: ocr-dependencies-layer.zip"
echo "Upload this as a Lambda layer, then attach it to your function"