#!/bin/sh -e

pip install --upgrade pip
pip install --no-cache-dir -e '.[dev,test]'

if [ -z "$CI" ]; then
    pre-commit install
    pre-commit autoupdate

    pyenv rehash

    ./scripts/install-tailwind.sh
fi
