#!/bin/bash

PREDICTION_DIR='../input/basic30000/'
GROUND_TRUTH_DIR='../../3_tileAnnotate/output/'
CLASS_PATH='../input/classes.json'
OUT_PATH='../output/mAP.txt'
IOU_THRESH=0.5

python3 mean_average_precision.py $PREDICTION_DIR $GROUND_TRUTH_DIR $CLASS_PATH $OUT_PATH $IOU_THRESH
