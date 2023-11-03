#!/bin/sh
if [ -f pyproject.toml ]; then
    pip install pdm > /dev/null 2>&1
    pdm export -o /tmp/requirements.txt > /dev/null 2>&1
    pip install -r /tmp/requirements.txt > /dev/null 2>&1
fi
if [ -f docs/requirements.txt ]; then
    pip install -r docs/requirements.txt > /dev/null 2>&1
fi
mypy .
