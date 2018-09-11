import argparse
import os
import sys
from tileAnnotate import tileAnnotate

def counttrees(classes, temp, darknetpath, imagefile, cfgfile, weightsfile, outputfile, errorfile):

	tileAnnotate(imagefile, None, temp + "/tile", "jpg", 448, 448)

	tiles = os.listdir(temp)

	with open(temp + "/valid.txt", "w") as valid:
		for tile in tiles:
			valid.write(tile + os.linesep)

	with open(temp + "/names.txt", "w") as names:
		for tree in classes:
			names.write(tree + os.linesep)

	results = temp + "/results"

	with open(temp + "/counttrees.data", "w") as f:
		f.write("classes={}{}".format(len(classes), os.linesep))
		f.write("valid_dir={}/{}".format(temp, os.linesep))
		f.write("valid={}/valid.txt{}".format(temp, os.linesep))
		f.write("names={}/names.txt{}".format(temp, os.linesep))
		f.write("results={}/{}".format(results, os.linesep))

	os.mkdir(results)

	command = "{darknetpath}/darknet detector valid {temp}/counttrees.data {cfgfile} {weightsfile} -out {results}".format(
		darknetpath=darknetpath, temp=temp, cfgfile=cfgfile, weightsfile=weightsfile, results="_")
	if errorfile:
		command += " 2> " + errorfile
	if outputfile:
		command += " > " + outputfile
	code = os.system(command)
	if code:
		raise Exception("An error occured during the prediction proccess. Error code: " + str(int(code / 256)));

if __name__ == "__main__":

	parser = argparse.ArgumentParser(prog="treecount")
	parser.add_argument("--darknetpath", required=True)
	parser.add_argument("--imagefile", required=True)
	parser.add_argument("--cfgfile", required=True)
	parser.add_argument("--weightsfile", required=True)
	parser.add_argument("--confidence", required=False, type=float, default=.5)
	args = parser.parse_args()

	results = counttrees([ "coconut", "banana", "mango", "papaya" ], args.darknetpath, args.imagefile, args.cfgfile, args.weightsfile)
