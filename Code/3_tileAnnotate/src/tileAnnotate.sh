#!/bin/bash

IMAGE_IN='../input/single_layer.tif'
JSON_IN='../input/BCCleaned.json'
PREFIX='../output/tile'
EXT='jpg'
HEIGHT=596
WIDTH=593

python3 tileAnnotate.py $IMAGE_IN $JSON_IN $PREFIX $EXT $HEIGHT $WIDTH
