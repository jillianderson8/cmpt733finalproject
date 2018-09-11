#!/bin/bash

DARKNET_PATH='../../../../darknet/darknet'
DATA_PATH='../input/darknet-cfg/bc.data'
CFG_PATH='../input/darknet-cfg/bc.cfg'
WEIGHTS_PATH='../input/bc_45000.weights'

$DARKNET_PATH detector valid $DATA_PATH $CFG_PATH $WEIGHTS_PATH

