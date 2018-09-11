import sys
import os
import argparse
import json
import shutil
import uuid
from flask import Flask, Response, request
from flask import url_for, render_template, send_file, send_from_directory
from PIL import Image
from treecount import counttrees
from visual import untile
from werkzeug import secure_filename

app = Flask(__name__)

parser = argparse.ArgumentParser(prog="app")
parser.add_argument("--darknetpath", required=True, help="Path to the folder containing the darknet executable that does detections")
parser.add_argument("--cfg", required=False, default="model.cfg", help="The config file of the detection model to use")
parser.add_argument("--weights", required=False, default="model.weights", help="The weights file of the detection model to use")
parser.add_argument("--out", required=False, help="The file containing output from the latest detection run")
parser.add_argument("--err", required=False, help="The file containing error output from the latest detection run")
parser.add_argument("--sample", required=False, default="sample", help="The folder containing sample results that can be viewed without re-calculating predictions, relative to the app root folder")
parser.add_argument("--result", required=False, default="result", help="A folder that will contain results files for download, relative to the app root folder")
parser.add_argument("--temp", required=False, default="temp", help="A folder that can be used to temporarily store working files during the prediction process, relative to the app root folder")
parser.add_argument("--caveat", type=bool, required=False, help="Whether to show a caveat stating that the hardware is not capable of predictions")
args = parser.parse_args()
 
def get_samples():
	return os.listdir(app.root_path + "/" + args.sample) if args.caveat else []

@app.route("/")
def upload():
	"""
	The page that allow the user to select and submit an image.
	"""
	return render_template("result.htm", kind=None, caveat=args.caveat, samples=get_samples())

@app.route("/images/<string:image>")
def show(image):
	"""
	Displays an uploaded image.
	"""
	mime = image[-3:]
	if mime == "svg":
		mime = "svg+xml"
	return send_file("images/" + image, mimetype="image/" + mime)

@app.route("/style/<path:path>")
def show_style(path):
	"""
	Displays a stylesheet
	"""
	return send_file("style/" + path)

@app.route("/script/<path:path>")
def show_script(path):
	return send_from_directory("script", path)

@app.route("/sample/<string:ident>")
def show_sample(ident):
	return render_template("result.htm", kind="sample", ident=ident, caveat=args.caveat, samples=get_samples())

@app.route("/sample/<string:ident>/image")
def sample_image(ident):
	return send_image(args.sample, ident)

@app.route("/sample/<string:ident>/predictions")
def sample_prediction(ident):
	return send_predictions(args.sample, ident);

@app.route("/result/<string:ident>")
def show_result(ident):
	return render_template("result.htm", kind="result", ident=ident, caveat=args.caveat, samples=get_samples())

@app.route("/result/<string:ident>/image")
def result_image(ident):
	return send_image(args.result, ident)

@app.route("/result/<string:ident>/predictions")
def result_prediction(ident):
	return send_predictions(args.result, ident);


def send_image(kind, ident):
	return send_file("{kind}/{ident}/image.jpg".format(kind=kind, ident=ident))

def send_predictions(kind, ident):
	return send_file("{kind}/{ident}/predictions.json".format(kind=kind, ident=ident))

@app.route("/count", methods=["POST"])
def count():
	"""
	Reads an image from post data then writes and displays it.
	"""
	image = request.files["image"]
	if image:
		ident = str(uuid.uuid4())
		temp = app.root_path + "/" + args.temp + "/" + ident
		results = app.root_path + "/" + args.result + "/" + ident
		os.mkdir(temp)
		os.mkdir(results)
		
		imagepath = results + "/image.jpg"
		image.save(imagepath)
		savedimage = Image.open(imagepath)
		size = savedimage.size

		classes = [ "banana", "coconut" ] # Must match what weights file was trained on

		result = None
		try:
			counttrees(classes, temp, args.darknetpath, imagepath, args.cfg, args.weights, args.out, args.err)
			result = untile(classes, temp, size[0], size[1], 0.0)
		except Exception as ex:
			print(ex)
			return render_template("error.htm", text=str(ex))
		finally:
			if True: # Switch to False for debugging by inspecting the contents of the temp folder
				shutil.rmtree(temp)
			else:
				print("not deleting " + temp)

		with open(results + "/predictions.json", "w") as outfile:
			json.dump(result, outfile)
		
		return render_template("result.htm", kind="result", ident=ident, caveat=args.caveat, samples=get_samples())
	else:
		return render_template("error.htm", text="Image required")

if __name__ == "__main__":
	app.run(host="0.0.0.0")
