#!/bin/bash

set -e

pip install -U pip setuptools wheel
pip install pdm
if [ -d "tmp" ]; then
  rm -rf "tmp"
fi
mkdir "tmp"
cp -r ../../mocks/sustainability-api/* "tmp"
cd "tmp"
pdm sync --prod --no-editable
cd __pypackages__/3.9/lib
zip -r ../../../deployment-package.zip .
cd ../../../src

zip -g ../deployment-package.zip *.py
