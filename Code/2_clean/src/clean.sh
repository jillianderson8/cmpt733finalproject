#!/bin/bash

JSON_IN='../input/points.json'
IMAGE_IN='../input/single_layer.tif'
CLIP_IN='../input/clipping_boundary.geojson'
OUTPUT_PATH='../output/BCCleaned.json'
CLASSES="banana tree,coconut tree"

python3 clean.py "$JSON_IN"  "$IMAGE_IN" "$CLIP_IN" "$OUTPUT_PATH" "$CLASSES"
