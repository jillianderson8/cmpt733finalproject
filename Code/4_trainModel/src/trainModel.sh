#!/bin/bash

DARKNET_PATH='../../../../darknet/darknet'
DATA_PATH='../input/darknet-cfg/bc.data'
CFG_PATH='../input/darknet-cfg/bc.cfg'
PRETRAINED_WEIGHT_PATH='../input/darknet-cfg/darknet19_448.conv.23'
OUT_PATH='../output/bc.out'
ERROR_PATH='../output/bc.error'

$DARKNET_PATH detector train $DATA_PATH $CFG_PATH $WEIGHT_PATH
