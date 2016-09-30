"""                                                                              
 Text-Machine Lab: CliRel  

 File Name : evaluate.py
                                                                              
 Creation Date : 16-01-2016
                                                                              
 Created By : Renan Campos
                                                                              
 Purpose : Evaluate the relation files in the test directory in comparison with
           those in the gold directory. The results will be written to the
           evaluation file. This script assumes that for every relation file in
           the test directory, there is a corresponding file in the golden
           directory.

"""

import sys

import futilities
from note import Relation

import sklearn.metrics as metrics
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from futilities import abs_path

#
# Should all relations be gathered and then evaluate, or should evaluation be
# done on each pairs of files individually and then combined?
# 

def relation_detection_metric(p_r, g_r):
  """
    Metric calculations
  """

  TP = 0
  FP = 0
  FN = 0
  
  # Relation labels for true positive will be used for classification testing
  p_labels = list()
  g_labels = list()

  for each in p_r.keys():
    try:
      p_label = p_r[each]
      g_label = g_r[each]
      
    except KeyError:
    # False Positive: pred contains relation but gold does not
      if p_label[0] != 'N':
        FP += 1

  for each in g_r.keys():
    try:
      g_label = g_r[each]
      p_label = p_r[each]
      
      g_labels.append(g_label)
      p_labels.append(p_label)

      # True  Positive: both gold and pred sets contain relation
      if p_label[0] != 'N':
        TP += 1
      else:
        FN += 1
    except KeyError:
      continue

  return p_labels, g_labels, TP, FP, FN 


def extract_relations(rel_file):

  results = dict()

  with open(rel_file, 'r') as f:
    for line in f:
      r = Relation(string=line)
      results[r] = r.label

  return results

def main(test_dir, gold_dir, results_file, v):

  prediction_files = futilities.filter_files(test_dir, "rel")
  gold_files       = futilities.filter_files(gold_dir, "rel")

  if len(prediction_files) != len(gold_files):
    sys.stderr.write("ERROR: number of files in test and gold directories do not match. \n")
    sys.exit(1)

  total_TP = 0
  total_FP = 0
  total_FN = 0
  total_p_labels = list()
  total_g_labels = list()

  for pred, gold in zip(prediction_files, gold_files):
    pred_rels = extract_relations(pred)
    gold_rels = extract_relations(gold)

    p_labels, g_labels, TP, FP, FN = relation_detection_metric(pred_rels, gold_rels)
  
    total_TP += TP
    total_FP += FP
    total_FN += FN
    total_p_labels += p_labels
    total_g_labels += g_labels

  # Calculate Precision and Recall Using true positive, false positive, false
  # negative for relation detection
  if (total_TP+total_FP):
    precision = float(total_TP) / (total_TP + total_FP)
  else:
    precision = 0
  if (total_TP+total_FN):
    recall = float(total_TP) / (total_TP + total_FN)
  else:
    recall = 0
  if (precision+recall):
    F1 = 2 * (precision * recall) / (precision + recall)
  else:
    F1 = 0

  with open(results_file, "w") as f:
    print >>f, "-" * 80
    print >>f, "Relation Detection Statistics:"
    print >>f, ""
    print >>f, "\tTrue positives: ",  total_TP
    print >>f, "\tFalse positives:",  total_FP
    print >>f, "\tFalse negatives:",  total_FN
    print >>f, ""
    print >>f, "\tPrecision: %.4f \t Recall: %.4f \t F1: %.4f" % (precision, recall, F1)
    print >>f, ""
    print >>f, "-" * 80
    print >>f, "Classification Statistics:"
    print >>f, ""
    print >>f, "\tF1:        %.4f" % metrics.f1_score(total_g_labels, total_p_labels, average='micro')
    print >>f, "\tPrecision: %.4f" % metrics.precision_score(total_g_labels, total_p_labels)
    print >>f, "\tRecall:    %.4f" % metrics.recall_score(total_g_labels, total_p_labels)
    print >>f, ""
    print total_g_labels
    print total_p_labels
    print >>f, metrics.confusion_matrix(total_g_labels, total_p_labels)
    print >>f, "-" * 80
    print >>f, ""
#    x = set(total_g_labels)
#    x = list(x)
#    x.sort()
#    for each in x:
#      print >>f, each

if __name__ == "__main__":
  main(abs_path("../results/"), 
       abs_path("./i2b2_examples/rel/"),
       abs_path("../results/i2b2_results"), True)
