'''Created on Feb 20, 2017
@author: jumabek
'''
from os import listdir
from os.path import isfile, join
import argparse
#import cv2
import numpy as np
import sys
import os
import shutil
import random 
import math

width_in_cfg_file = 416.
height_in_cfg_file = 416.

def IOU(x,centroids):
    similarities = []
    k = len(centroids)
    for centroid in centroids:
        c_w,c_h = centroid
        w,h = x
        if c_w>=w and c_h>=h:
            similarity = w*h/(c_w*c_h)
        elif c_w>=w and c_h<=h:
            similarity = w*c_h/(w*h + (c_w-w)*c_h)
        elif c_w<=w and c_h>=h:
            similarity = c_w*h/(w*h + c_w*(c_h-h))
        else: #means both w,h are bigger than c_w and c_h respectively
            similarity = (c_w*c_h)/(w*h)
        similarities.append(similarity) # will become (k,) shape
    return np.array(similarities) 

def avg_IOU(X,centroids):
    n,d = X.shape
    sum = 0.
    for i in range(X.shape[0]):
        #note IOU() will return array which contains IoU for each centroid and X[i] // slightly ineffective, but I am too lazy
        sum+= max(IOU(X[i],centroids)) 
    return sum/n

def write_anchors_to_file(centroids,X,anchor_file):
    print("in write_anchors...")
    f = open(anchor_file,'w')
    
    anchors = centroids.copy()
    print(anchors.shape)

    for i in range(anchors.shape[0]):
        anchors[i][0]*=width_in_cfg_file/32.
        anchors[i][1]*=height_in_cfg_file/32.
         

    widths = anchors[:,0]
    sorted_indices = np.argsort(widths)

    print('Anchors = ', anchors[sorted_indices])
        
    for i in sorted_indices[:-1]:
        f.write('%0.2f,%0.2f, '%(anchors[i,0],anchors[i,1]))

    #there should not be comma after last anchor, that's why
    f.write('%0.2f,%0.2f\n'%(anchors[sorted_indices[-1:],0],anchors[sorted_indices[-1:],1]))
    
    f.write('%f\n'%(avg_IOU(X,centroids)))
    print("done")

def kmeans(X,centroids,eps,anchor_file):

    # N is number of data points (ie number of bounding boxes in training data)
    N = X.shape[0]
    iterations = 0
    
    # dim should be 2 for w,h
    k,dim = centroids.shape
    print("in kmeans with k = " + str(k))

    # initialize prev_assignments to a bunch of -1s
    prev_assignments = np.ones(N)*(-1)    
    iter = 0

    # a Nxk array to hold distance to from each data point to each of the k centroids
    # initialized to 0s
    old_D = np.zeros((N,k))

    while iter < 1000:
        D = [] 
        iter+=1        

        # for each data point
        for i in range(N):
            # distance measure is IOU between bounding box and centroid bounding box
            d = 1 - IOU(X[i],centroids)
            D.append(d)
        
        # D holds a dist for each bounding box in training data
        D = np.array(D) # D.shape = (N,k)
        
        # it is printing out the sum of the differences for all the data points
        #print("iter {}: dists = {}".format(iter,np.sum(np.abs(old_D-D))))
            
        #assign samples to centroids 
        # for each data pt we find the lowest dist value, ie; the centroid its closest to
        assignments = np.argmin(D,axis=1)  # assignments.shape = (10858,)

        # check if assignments have changed since last round
        if (assignments == prev_assignments).all() :
            print("Centroids = ",centroids)
            write_anchors_to_file(centroids,X,anchor_file)
            return


        #calculate new centroids

        # centroid_sums is a kx2 array to hold ...
        centroid_sums=np.zeros((k,dim),np.float)
        # go thru each data point and find the centroid it was assigned to and add
        # its w and h to its corresponding centroid_sums element
        for i in range(N):
            centroid_sums[assignments[i]]+=X[i]        
        # then go through each centroid and get the average w and h by dividing the
        # sum by the number of data points that got assigned to that centroid
        for j in range(k):
            centroids[j] = centroid_sums[j]/(np.sum(assignments==j))
        
        prev_assignments = assignments.copy()     
        old_D = D.copy()  

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-filelist', default = '\\path\\to\\voc\\filelist\\train.txt', 
                        help='path to filelist\n' )
    parser.add_argument('-output_dir', default = 'generated_anchors/anchors', type = str, 
                        help='Output anchor directory\n' )  
    parser.add_argument('-num_clusters', default = 0, type = int, 
                        help='number of clusters\n' )  

    image_path = "../../3_tileAnnotate/output/"

   
    args = parser.parse_args()
    
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    f = open(args.filelist)
  
    lines = [line.rstrip('\n') for line in f.readlines()]
    
    annotation_dims = []

    size = np.zeros((1,1,3))


    # these nested for loops go through every line in every tile.x.y.txt file and append the w 
    # and h of the listed bounding boxes to the annotation_dims list
    for line in lines:
                    
        #line = line.replace('images','labels')
        #line = line.replace('img1','labels')
        line = line.replace('JPEGImages','labels')        
        

        line = line.replace('.jpg','.txt')
        line = line.replace('.png','.txt')
        f2 = open(image_path + line)
        for line in f2.readlines():
            line = line.rstrip('\n')
            w,h = line.split(' ')[3:]            
            #print(w,h)
            #annotation_dims.append(map(float,(w,h)))
            # bh changed this line so that annotation_dims is a list of 2-tuples of float values
            # rather than a list of map objects
            annotation_dims.append((float(w),float(h)))
    
    # so now annotation_dims is a nx2 numpy array holding all the widths and heights of all 
    # the bounding boxes in all the training data
    annotation_dims = np.array(annotation_dims)
    np.savetxt("bounding_boxes.csv", annotation_dims, delimiter=",")
  
    eps = 0.005
    
    if args.num_clusters == 0:

        # this for loop runs the kmeans clustering algortihm 10 times, each time with a 
        # different k
        for num_clusters in range(1,11): #we make 1 through 10 clusters 

            # creates the filename for the kth file we will output with the k clusters
            anchor_file = join( args.output_dir,'anchors%d.txt'%(num_clusters))

            # generate a list of length k containing randomly selected indices from the 0-number of annotations-1
            indices = [ random.randrange(annotation_dims.shape[0]) for i in range(num_clusters)]
            # use this to randomly select k annotations to use as the initial centroids of the 
            # clustering alg
            centroids = annotation_dims[indices]

            # pass the array of annotations, the initial centroids to use, the eps value, and the output file
            kmeans(annotation_dims,centroids,eps,anchor_file)
            print('centroids.shape', centroids.shape)
    else:
        anchor_file = join( args.output_dir,'anchors%d.txt'%(args.num_clusters))
        indices = [ random.randrange(annotation_dims.shape[0]) for i in range(args.num_clusters)]
        centroids = annotation_dims[indices]
        kmeans(annotation_dims,centroids,eps,anchor_file)
        print('centroids.shape', centroids.shape)

if __name__=="__main__":
    main(sys.argv)
