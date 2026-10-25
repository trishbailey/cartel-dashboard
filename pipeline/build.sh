#!/usr/bin/env bash
# Render build: validate, then copy data next to the static site.
set -euo pipefail
python3 pipeline/validate.py
rm -rf public/data && mkdir -p public/data && cp -r data/*.json data/*.geojson data/arcs public/data/
echo "built"
