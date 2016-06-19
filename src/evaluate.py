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

from sklearn.metrics import classification_report

#
# Should all relations be gathered and then evaluate, or should evaluation be
# done on each pairs of files individually and then combined?
# 

def relation_detection_metric(p_r, g_r):
  """
    Enter glorious comments here
    True Negatives aren't important when computing precision or recall.
  """

  TP = 0
  FP = 0
  
  # Relation labels for true positive will be used for classification testing
  p_labels = list()
  g_labels = list()

  for each in p_r.keys():
    try:
      p_label = p_r[each]
      g_label = g_r[each]
      
      p_labels.append(p_label)
      g_labels.append(g_label)

      # True  Positive: both gold and pred sets contain relation
      TP += 1
    except:
      # False Positive: pred contains relation but gold does not
      FP += 1

  # False Negative: gold contains relation but pred does not
  # Can be calculated as the difference between the number of relations in the
  # gold set and the number in the predicted set, once the false positives are
  # neglected. 
  FN = max(0, len(g_r) - (len(p_r) - FP))
 
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
  precision = float(total_TP) / (total_TP + total_FP)
  recall    = float(total_TP) / (total_TP + total_FN)
  F1        = 2 * (precision * recall) / (precision + recall)

  with open(results_file, "w") as f:
    print >>f, "-" * 80
    print >>f, "Relation Detection Statistics:"
    print >>f, ""
    print >>f, "\tTrue positives: ",   total_TP
    print >>f, "\tFalse positives:",  total_FP
    print >>f, "\tFalse negatives:",  total_FN
    print >>f, ""
    print >>f, "\tPrecision: %.4f \t Recall: %.4f \t F1: %.4f" % (precision, recall, F1)
    print >>f, ""
    print >>f, "-" * 80
    print >>f, "Classification Statistics:"
    print >>f, ""
    print >>f, classification_report(total_g_labels, total_p_labels)
    print >>f, "-" * 80
    print >>f, ""

if __name__ == "__main__":
  #TODO Unit Tests
  pass
