import os
from PIL import Image, ImageDraw, ImageFont
from collections import defaultdict

def untile(classes, temp, width, height, threshold):

	predictions = []
	for cl in classes:
		f = '{temp}/results/_{f}.txt'.format(temp=temp, f=cl)
		if os.path.isfile(f):
			predictions += [[cl] + line.strip().split(' ') for line in open(f)]

	untiled_predictions = []

	result = Image.new("RGB", (width, height))
	draw = ImageDraw.Draw(result)

	dull = defaultdict(lambda : (196,196,196))
	bright = defaultdict(lambda : (255,255,255))
	dull['banana'] = (196,196,0)
	bright['banana'] = (255,255,0)

	i = 0
	y = 0
	while os.path.isfile('{temp}/tile.{i}.0.jpg'.format(temp=temp, i=i)):
		j = 0
		x = 0
		while os.path.isfile('{temp}/tile.{i}.{j}.jpg'.format(temp=temp, i=i, j=j)):
			tile = Image.open('{temp}/tile.{i}.{j}.jpg'.format(temp=temp, i=i, j=j))
			dx, dy = tile.size
			result.paste(tile, (x, y, x + dx, y + dy))
			for line in ((float(p[3]), float(p[4]), float(p[5]), float(p[6]), p[0], float(p[2])) for p in predictions if p[1] == 'tile.{i}.{j}.jpg'.format(i=i, j=j) and float(p[2]) >= threshold):
				untiled_predictions.append({ 'tree' : line[4], 'confidence' : line[5], 'box' : (x+line[0], y+line[1], x+line[2], y+line[3]) }) 
				label = "{confidence:.0%} {cl}".format(cl=line[4], confidence=float(line[5]))
				draw.line((x+line[0], y+line[1], x+line[0], y+line[3]), fill=dull[line[4]], width=1)
				draw.line((x+line[0], y+line[1], x+line[2], y+line[1]), fill=bright[line[4]], width=2)
				draw.line((x+line[0], y+line[3], x+line[2], y+line[3]), fill=dull[line[4]], width=1)
				draw.line((x+line[2], y+line[1], x+line[2], y+line[3]), fill=dull[line[4]], width=1)
				draw.text((x+line[0] + 3, y+line[1]), label, fill=bright[line[4]])
			j += 1
			x += dx
		i += 1
		y += dy

	return untiled_predictions
