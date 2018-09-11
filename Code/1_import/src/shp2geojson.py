# What does this file do? 
# March 20, 2018

import json
import os
import argparse
import geopandas as gpd

def shp2geojson(inFile, outFile):
	trees = gpd.read_file(inFile)
	try:
		os.remove(outFile)
	except OSError:
		pass
	trees.to_file(outFile, driver='GeoJSON')


parser = argparse.ArgumentParser(description='Takes in a shapefile and writes a corresponding GeoJSON file.')
parser.add_argument('input_path', help='Path to the directory containing the shapefile to convert.')
parser.add_argument('output_path', help='File path of the resulting GeoJSON file.')
args = parser.parse_args()

shp2geojson(args.input_path, args.output_path)
