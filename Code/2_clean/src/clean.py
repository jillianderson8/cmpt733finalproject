"""
Takes trees (json), image (tif) and clipping boundary (json) and outputs a new version of trees where longitude and latitude for each object have been mapped to x & y pixel values within the image and class and box width have been assigned for each object.
"""


from PIL import Image
import random
import json
import copy
import argparse

def othertag2class(s):
	s = s.lower()
	if "population" in s:
		return "settlement"
	elif "mangifera indica" in s:
		return "mango tree"
	elif ("musa" in s):
		return "banana tree"
	elif "carica" in s:
		return "papaya tree"
	elif ("cocos" in s) or ("cocus" in s):
		return "coconut tree"
	elif "pole" in s:
		return "power pole"
	else: 
		return 'other'

def othertag2width(s):
	s = s.lower()
	if "population" in s:
		return 1000
	elif ("cocos" in s) or ("cocus" in s):
		# Coconut
		return 100
	elif ("musa" in s):
		# Banana
		return 50
	elif "mangifera indica" in s:
		# Mango
		return 250
	elif "carica" in s:
		# Papaya
		return 250
	elif "pole" in s:
		return 10	
	else: 
		return 100


def clean(json_in, image_in, clip_in, json_out, classes='all'):
	def lng2px(lng):
		x = (lng-west)/(east-west) * width
		return x

	def lat2px(lat):
		y = (lat-north)/(south-north) * height	
		return y

	def transformX(x):
		return  x + (-30 + 60*x/width)

	def transformY(y):
		return y + (60 - 30*y/height)

	# Load Image
	Image.MAX_IMAGE_PIXELS = 500000000
	im = Image.open(image_in)
	width = im.width
	height = im.height

	# Load Clipping Boundary
	cb = json.load(open(clip_in))
	north = cb['coordinates'][0][0][1]
	south = cb['coordinates'][0][3][1]
	east = cb['coordinates'][0][1][0]
	west = cb['coordinates'][0][0][0]
	

	# Load GeoJSON
	trees = json.load(open(json_in))
	#coords = [c['geometry']['coordinates'] for c in trees['features']]
	#species = [c['properties']['other_tags'] for c in trees['features']]
	#classes = [c['properties']['class'] for c in trees['features']]

	# Assign New Properties
	for t in trees['features']:
		lng, lat = t['geometry']['coordinates']

		x,y = transformX(lng2px(lng)), transformY(lat2px(lat))

		t['properties']['box_x'] = x
		t['properties']['box_y'] = y
		t['properties']['class'] = othertag2class(t['properties']['other_tags'])
		t['properties']['box_w'] = othertag2width(t['properties']['other_tags'])

	# Filter
	if classes != 'all':
		classes = classes.split(',')
		trees_classes = [x for x in trees['features'] if x['properties']['class'] in classes] 
		trees['features'] = trees_classes
	
    # Output
	json.dump(trees, open(json_out, 'w'))

parser = argparse.ArgumentParser(description='Takes trees (json), image (tif) and clipping boundary (json) and outputs a new version of tree where longitude and latitude have been mapped to x & y values and class and box width have been assigned.')
parser.add_argument('json_in', help='File path to json file containing tree data.')
parser.add_argument('image_in', help='File path to image.')
parser.add_argument('clip_in', help='File path to clipping boundary.')
parser.add_argument('json_out', help='File path to outputted file.')
parser.add_argument('classes', nargs='?', default='all', help='Optional, defaults to all. The classes to include in the output.')
args = parser.parse_args()

clean(args.json_in, args.image_in, args.clip_in, args.json_out, args.classes)
