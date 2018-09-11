# What does this file do? 

from PIL import Image
from PIL import ImageFile
import math
import argparse
import json

def annotate(mapping, allxycw, i, j, tile_width, tile_height, result_width, result_height, outfilename):
	"""
		Write out labels in the format required by darknet from the tile with the
		properties provided 
	"""

	# Filter trees
	xycwh = [(x,y,c,w,w) for x,y,c,w in allxycw if (x >= (j*tile_width)) & 
	                                               (x <= j*tile_width+result_width) &
	                                               (y >= i*tile_height) & 
	                                               (y <= i*tile_height+result_height)]
	
	x2ratio = lambda x: (x-j*tile_width)/result_width
	y2ratio = lambda y: (y-i*tile_height)/result_height
	w2ratio = lambda w: w/result_width
	h2ratio = lambda h: h/result_height

	toprint = [str(mapping[c]) + ' ' +             # Class
	           str(x2ratio(x)) + ' ' +             # Box Center x
	           str(y2ratio(y)) + ' ' +             # Box Center y
	           str(w2ratio(w)) + ' ' +             # Box width
	           str(h2ratio(h))                     # Box height
	           for x,y,c,w,h in xycwh]

	try:
		# Save Annotation
		with open("{filename}.{i}.{j}.txt".format(i=i, j=j, filename=outfilename), "w") as f:
			for line in toprint:
				f.write(line+'\n')

	except Exception as e:
		print(e)

def tile(image, img_width, img_height, tile_height, tile_width, outfilename, outextension, mapping, on_tile_saved, allxycw):
	"""
		Divide the given image into tiles
	"""

	# Tile Images
	num_tiles_vert = math.ceil(img_height/tile_height)
	num_tiles_horiz= math.ceil(img_width/tile_width)
	for i in range(0, num_tiles_vert):
		result_height = min(img_height - i*tile_height, tile_height)
		for j in range(0, num_tiles_horiz):
			result_width = min(img_width - j*tile_width, tile_width)
			box = (j*tile_width, i*tile_height, j*tile_width+result_width, i*tile_height+result_height)
			tile = image.crop(box)

			try:
				# Save Tile Image
				tile.convert('RGB').save('{filename}.{i}.{j}.{extension}'.format(i=i, j=j, filename=outfilename, extension=outextension), 'JPEG')

			except Exception as e:
				print(e)

			if on_tile_saved:
			#	on_tile_saved(mapping, allxycw, i, j, tile_width, tile_height, result_width, result_height, outfilename)
                                annotate(mapping, allxycw, i, j, tile_width, tile_height, result_width, result_height, outfilename)

def tileAnnotate(image_in, json_in, outfilename, outextension, tile_height, tile_width):

	# Load Image
	Image.MAX_IMAGE_PIXELS = 500000000
	image = Image.open(image_in)
	img_width, img_height = image.size

	mapping = None
	allxycw = None
	if json_in:
		# Load GeoJSON data
		trees = json.load(open(json_in))
		allxycw = [(x['properties']['box_x'], 
		            x['properties']['box_y'], 
		            x['properties']['class'],
		            80)
		            for x in trees['features']]

		# Create Class Mapping
		classes = sorted(set([c for x,y,c,w in allxycw]))
		mapping = dict(zip(classes, list(range(0,len(classes)))))
		with open(outfilename + '_classes.json', 'w+') as fp:
				json.dump(mapping, fp)

	tile(image, img_width, img_height, tile_height, tile_width, outfilename, outextension, mapping, annotate if mapping else None, allxycw)

if __name__ == '__main__':
	# Parser
	parser = argparse.ArgumentParser(description='Takes an image file as input and writes tiles that together match the original image.')
	parser.add_argument('image_in', help='File path of the image to split into tiles')
	parser.add_argument('json_in', help='File path to the JSON containing objects to assign to tiles.')
	parser.add_argument('output_path_prefix', help='Path and file prefix of the resulting tiles (tile numbers are filled in to complete the resulting file names)')
	parser.add_argument('output_file_extension', help='File suffix of the resulting tiles (appended to output_path_prefix and tile numbers)')

	parser.add_argument('tile_height', type=int, help='Height in pixels of the resulting tiles')
	parser.add_argument('tile_width', type=int, help='Width in pixels of the resulting tiles')
	args = parser.parse_args()

	tileAnnotate(args.image_in, args.json_in, args.output_path_prefix, args.output_file_extension, args.tile_height, args.tile_width)
