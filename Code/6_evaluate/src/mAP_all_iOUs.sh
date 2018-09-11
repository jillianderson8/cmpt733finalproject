#!/bin/bash
mod=../input/results/22froze30000/
python3 mean_average_precision.py $mod ../../3_tileAnnotate/output/DarknetData/ ../input/classes.json ../output/mAP_5_95.txt 0.5
python3 mean_average_precision.py $mod ../../3_tileAnnotate/output/DarknetData/ ../input/classes.json ../output/mAP_5_95.txt 0.55
python3 mean_average_precision.py $mod ../../3_tileAnnotate/output/DarknetData/ ../input/classes.json ../output/mAP_5_95.txt 0.60
python3 mean_average_precision.py $mod ../../3_tileAnnotate/output/DarknetData/ ../input/classes.json ../output/mAP_5_95.txt 0.65
python3 mean_average_precision.py $mod ../../3_tileAnnotate/output/DarknetData/ ../input/classes.json ../output/mAP_5_95.txt 0.70
python3 mean_average_precision.py $mod ../../3_tileAnnotate/output/DarknetData/ ../input/classes.json ../output/mAP_5_95.txt 0.75
python3 mean_average_precision.py $mod ../../3_tileAnnotate/output/DarknetData/ ../input/classes.json ../output/mAP_5_95.txt 0.80
python3 mean_average_precision.py $mod ../../3_tileAnnotate/output/DarknetData/ ../input/classes.json ../output/mAP_5_95.txt 0.85
python3 mean_average_precision.py $mod ../../3_tileAnnotate/output/DarknetData/ ../input/classes.json ../output/mAP_5_95.txt 0.90
python3 mean_average_precision.py $mod ../../3_tileAnnotate/output/DarknetData/ ../input/classes.json ../output/mAP_5_95.txt 0.95
