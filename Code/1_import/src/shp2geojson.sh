#!/bin/bash
INPUT_PATH='../input/Trees/'
OUTPUT_PATH='../output/points.json'

python3 shp2geojson.py $INPUT_PATH $OUTPUT_PATH
