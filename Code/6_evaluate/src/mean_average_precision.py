from time import gmtime, strftime
from PIL import Image
import pandas as pd
import numpy as np
import argparse
import json
import sys
import os

parser = argparse.ArgumentParser(description='')

parser.add_argument('predictionDir', help='Path to directory containing the prediction files (one for each class). The name of the directory should be the prefix for each of the result files.')
parser.add_argument('groundTruthDir', help='Path to the directory containing the ground truth information (images and annotations).')
parser.add_argument('classPath', help='File path to the json containing a class mapping between class strings and integers.')
parser.add_argument('outPath', help='Path to the file where output should be written.')
parser.add_argument('iouThreshold', type=float, help='The IoU threshold which will be used to determine whether a detection is true.')
args = parser.parse_args()


# ***************************
# TENSORFLOW MODELS FUNCTIONS - https://github.com/tensorflow/models/blob/master/research/object_detection/utils/metrics.py
# ***************************
def compute_average_precision(precision, recall):
    """Compute Average Precision according to the definition in VOCdevkit.
       Precision is modified to ensure that it does not decrease as recall decrease.
       Args:   
           precision: A float [N, 1] numpy array of precisions
           recall: A float [N, 1] numpy array of recalls
       Raises:
           ValueError: if the input is not of the correct format
       Returns:
           average_precison: The area under the precision recall curve. NaN if
                             precision and recall are None.
    """
    if precision is None:
        if recall is not None:
            raise ValueError("If precision is None, recall must also be None")
        return np.NAN

    if not isinstance(precision, np.ndarray) or not isinstance(recall, np.ndarray):
        raise ValueError("precision and recall must be numpy array")
    if precision.dtype != np.float or recall.dtype != np.float:
        raise ValueError("input must be float numpy array.")
    if len(precision) != len(recall):
        raise ValueError("precision and recall must be of the same size.")
    if not precision.size:
        return 0.0
    if np.amin(precision) < 0 or np.amax(precision) > 1:
        raise ValueError("Precision must be in the range of [0, 1].")
    if np.amin(recall) < 0 or np.amax(recall) > 1:
        raise ValueError("recall must be in the range of [0, 1].")
    if not all(recall[i] <= recall[i + 1] for i in range(len(recall) - 1)):
        raise ValueError("recall must be a non-decreasing array")

    recall = np.concatenate([[0], recall, [1]])
    precision = np.concatenate([[0], precision, [0]])

    # Preprocess precision to be a non-decreasing array
    for i in range(len(precision) - 2, -1, -1):
        precision[i] = np.maximum(precision[i], precision[i + 1])

    indices = np.where(recall[1:] != recall[:-1])[0] + 1
    average_precision = np.sum((recall[indices] - recall[indices - 1]) * precision[indices])

    return average_precision

def compute_precision_recall(scores, labels, num_gt):
    """Compute precision and recall.
       Args:
           scores: A float numpy array representing detection score
           labels: A boolean numpy array representing true/false positive labels
           num_gt: Number of ground truth instances
       Raises:
           ValueError: if the input is not of the correct format
       Returns:
           precision: Fraction of positive instances over detected ones. This value is
                      None if no ground truth labels are present.
          recall: Fraction of detected positive instance over all positive instances.
                  This value is None if no ground truth labels are present.
    """
    if not isinstance(labels, np.ndarray) or labels.dtype != np.bool or len(labels.shape) != 1:
        raise ValueError("labels must be single dimension bool numpy array")
    if not isinstance(scores, np.ndarray) or len(scores.shape) != 1:
        raise ValueError("scores must be single dimension numpy array")
    if num_gt < np.sum(labels):
        raise ValueError("Number of true positives must be smaller than num_gt.")
    if len(scores) != len(labels):
        raise ValueError("scores and labels must be of the same size.")
  
    if num_gt == 0:
        return None, None

    sorted_indices = np.argsort(scores)
    sorted_indices = sorted_indices[::-1]
    labels = labels.astype(int)
    true_positive_labels = labels[sorted_indices]
    false_positive_labels = 1 - true_positive_labels
    cum_true_positives = np.cumsum(true_positive_labels)
    cum_false_positives = np.cumsum(false_positive_labels)
    precision = cum_true_positives.astype(float) / (
        cum_true_positives + cum_false_positives)
    recall = cum_true_positives.astype(float) / num_gt
    
    return precision, recall

# ***************************
# Our Functions
# ***************************

def train2rect(ratios, imagew, imageh):
    """
    Takes in data used during training and transforms it into format matching
    the format outputted by darknet's valid function.
    """
    xratio, yratio, wratio, hratio = ratios
    xmin = xratio*imagew - wratio*imagew/2
    ymin = yratio*imageh - hratio*imageh/2
    xmax = xratio*imagew + wratio*imagew/2
    ymax = yratio*imageh + hratio*imageh/2
    
    return (xmin, ymin, xmax, ymax)


def calc_iou(recs):
    """
    recs: A tuple containing two tuples, each representing a rectangle
    returns: Float. The calculated intersection over union metric.  
    """
    recA, recB = recs
    xminA, yminA, xmaxA, ymaxA = recA
    areaA = (xmaxA-xminA) * (ymaxA-yminA)
    
    xminB, yminB, xmaxB, ymaxB = recB
    areaB = (xmaxB-xminB) * (ymaxB-yminB)
    
    diffx = min(xmaxA, xmaxB) - max(xminA, xminB)
    diffy = min(ymaxA, ymaxB) - max(yminA, yminB)
    

    if (diffx>=0) & (diffy>=0):
        intersection= diffx * diffy    
    else:
        intersection=0
        
    union = areaA + areaB - intersection

    return intersection/union


def calculate_class_AP (detectionPath, imgPath, iouThresh, clss):
    """
    """

    # Read in the object detections 
    predictions = pd.read_csv(detectionPath, delimiter=' ', header=None, engine='python')
    predictions.columns = ['filename', 'confidence', 'xmin', 'ymin', 'xmax', 'ymax']
    predictions['prRect'] = list(zip(predictions.xmin, predictions.ymin, 
                                          predictions.xmax, predictions.ymax))
    predictions = predictions.drop(['xmin', 'ymin', 'xmax', 'ymax'], axis=1)

    all_scores = []
    all_bools = []
    all_gttot = 0

    for f in predictions['filename'].unique():
        im = Image.open((imgPath + f)[:-3] + 'jpg')
        imagew, imageh = im.size

        try: 
            # Load Ground Truth
            gt = pd.read_csv((imgPath + f)[:-3] + 'txt', delimiter=' ', header=None)
            gt.columns=['class', 'xratio', 'yratio', 'wratio', 'hratio']
            gt = gt[gt['class'] == clss]


            gt['temp'] = list(zip(gt['xratio'], gt['yratio'], gt['wratio'], gt['hratio']))
            gt['gtRect'] = gt['temp'].apply(train2rect, args=(imagew, imageh))
            gt['filename'] = f

            gt=gt[['gtRect', 'filename']]



	    # Find Predictions for specific file
            pr = predictions[predictions['filename']==f].sort_values('confidence', ascending=False)

            # Calculate IoU values
            comp = pr.merge(gt, on='filename', how='inner')
            comp['Rects'] = list(zip(comp['prRect'], comp['gtRect']))
            comp['IoU'] = comp['Rects'].apply(calc_iou)
            comp = comp[comp['IoU'] > iouThresh]

            # Assign True or False to Detections
            comp = comp.sort_values('confidence', ascending=False)
            td = comp.groupby('gtRect').nth(0)

            td = td[['filename', 'confidence', 'prRect']]
            td['TrueDetection'] = True
            detections = pr.merge(td, on=['filename', 'confidence', 'prRect'],
                                  how='left').fillna(False)

            # Add to totals for class
            all_scores += list(detections['confidence'])
            all_bools += list(detections['TrueDetection'])
            all_gttot += len(gt)
            

        except Exception as e:
            #print(e)
            # No ground truth values!
        
            # Get Predictions & Set all to false detections
            pr = predictions[predictions['filename']==f].sort_values('confidence', 
                                                             ascending=False)
            pr['TrueDetection'] = False
        
            # Add to totals
            all_scores += list(pr['confidence'])
            all_bools += list(pr['TrueDetection'])

    precision, recall = compute_precision_recall(np.array(all_scores), np.array(all_bools), all_gttot)    
    
    cap = compute_average_precision(precision, recall)

    return cap

def calculate_mAP(predDir, gtDir, classPath, outPath, iouThresh):
    out = {}
    out['time'] = strftime("%Y-%m-%d-%H:%M:%S", gmtime())
    out['model'] = predDir.split('/')[-2]
    out['iouThresh'] = iouThresh

    class_dict = json.load(open(classPath))
    files = os.listdir(predDir)

    class_count = 0
    class_APs = 0
    for f in files:
        file_path = predDir + f
        base_name = predDir.split('/')[-2]
        class_name = f[len(base_name):-len('.txt')]
        class_int = class_dict[class_name]

        # skip this class if the results file is empty
        if os.stat(file_path).st_size == 0:
            continue
       
        cap = calculate_class_AP(file_path, gtDir, iouThresh, class_int)
        class_count += 1
        class_APs += cap

        out[class_name + 'AP'] = cap
    
    mAP = class_APs / class_count
    out['mAP'] = mAP

    with open(outPath, 'a') as f:
        json.dump(out, f)
        f.write(os.linesep)
    
    print(mAP)

calculate_mAP(args.predictionDir, args.groundTruthDir, args.classPath,  args.outPath, args.iouThreshold)

