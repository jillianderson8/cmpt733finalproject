This folder contains configuration for different experiments.

From this folder, darknet can be run. It relies on some modifications to darknet
made in the https://github.com/bgerspac/darknet fork of darknet. E.g.:

../<path-to-bgerspac-darknet>/darknet detector train bc.data bc.cfg

Leaving it to run in the background with output piped to logs is recommended:

../<path-to-bgerspac-darknet>/darknet detector train bc.data bc.cfg > bc.out 2> bc.error &

The files bc_test.txt and bc_train.txt contain the standard list of tiles
produced from JupyterNotebooks/TileAnnotate.ipynb.

The train_dir and valid_dir settings in the .data file should be modified to
refer to the path containing the image jpgs and label txt files.

Some of the specific configuration present are:
bc - Basic YOLO with bananas and coconuts
pretrained - YOLO using pretrained weights. This does not have its own .cfg
             because the only thing that needs to be done differently is to
             provide weights on the command line
22froze - YOLO with ALL BUT 1 connvolutional layer frozen (intended to be used
          with pretrained weights for at least 22 layers)
13froze - YOLO with 13 convolutional layers frozen (intended to be used with
          pretrained weights for at least 13 layers)
noaugment - YOLO with cfg modification to not manipulate input images during training
