#!/bin/bash

#set -e

pip install -U pip setuptools wheel
pip install pdm==2.1.1
if [ -d "tmp" ]; then
  rm -rf "tmp"
fi
mkdir "tmp"
cp -r ../mock/* "tmp"
cd "tmp"
pdm config python.use_venv false
pdm sync --prod --no-editable
cd __pypackages__/3.9/lib
zip -r ../../../deployment-package.zip .
cd ../../../
zip -g deployment-package.zip src/*.py
