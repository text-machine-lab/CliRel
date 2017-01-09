"""
 Text-Machine Lab: CliRel

 File Name : clirel.py

 Creation Date : 22-10-2016

 Created By : Renan Campos

 Purpose : Trains, predicts and evaluates for clinical relation task.

"""

import os
import sys
import sklearn.metrics as metrics
import numpy as np
from collections import defaultdict

import note

def absPath(path):
  """ Return absolute path from where this file is located """
  return os.path.join(os.path.dirname(os.path.abspath(__file__)), path)

def train(t_dir, model_path, model_flags=None):
  """
    >>> train('i2b2_examples/', 'model_example/')
    'Example model success.'
    >>> train('i2b2_examples/', 'model_example/', ['a', 'b'])
    'Example model success with flags a b.'
  """
  cons = note.filterFiles(os.path.join(t_dir, 'concept'), 'con')
  txts = note.filterFiles(os.path.join(t_dir,     'txt'), 'txt')
  rels = note.filterFiles(os.path.join(t_dir,     'rel'), 'rel')

  data = list()

  for c,t,r in zip(cons, txts, rels):
    data.append((c, t, r))

  # import the model.
  # The model will be loaded as a module. This provides modularity for the
  # assumption that the model is implemented with a 'model.py' in its main dir.
  sys.path.insert(0, absPath(model_path))
  import model
  sys.path = sys.path[1:]

  out = model.train(data, model_flags)
  del model

  return out


def predict(t_dir, model_path, model_flags=None):

  cons = note.filterFiles(os.path.join(t_dir, 'concept'), 'con')
  txts = note.filterFiles(os.path.join(t_dir,     'txt'), 'txt')

  data = list()

  for c,t in zip(cons, txts):
    data.append((c, t))

  for f in note.filterFiles(absPath('predictions'), 'pred'):
    os.remove(f)

  # import the model.
  # The model will be loaded as a module. This provides modularity for the
  # assumption that the model is implemented with a 'model.py' in its main dir.
  sys.path.insert(0, model_path)
  import model
  sys.path = sys.path[1:]

  out = model.predict(data, model_flags)

  del model

  return out

def evaluate(e_dir, p_dir):
  """
    Extracts the relation files from the gold directory and the
    prediciton directory, and calculates the F1, recall, and precision.
  """

  c_files = note.filterFiles(os.path.join(e_dir, 'concept'), 'con')
  t_files = note.filterFiles(os.path.join(e_dir,     'txt'), 'txt')
  g_files = note.filterFiles(os.path.join(e_dir,     'rel'), 'rel')
  p_files = note.filterFiles(p_dir, 'pred')

  def ugh():
    return np.nan

  gold = defaultdict(ugh)
  pred = defaultdict(ugh)

  def addGold(d):
    ind = [int(d.conStart1), int(d.conEnd1), int(d.conStart2), int(d.conEnd2)]
    ind.append(d.lineNum)
    ind.append(d.fileName)

    ind.append(d.conType1)
    ind.append(d.conType2)
    gold[tuple(ind)] = d.relType

  def addPred(d):
    ind = [int(d.conStart1), int(d.conEnd1), int(d.conStart2), int(d.conEnd2)]
    ind.append(d.lineNum)
    ind.append(d.fileName)

    ind.append(d.conType1)
    ind.append(d.conType2)

    pred[tuple(ind)] = d.relType


  for c, t, g in zip(c_files, t_files, g_files):
    #print c.split('/')[-1].split('.')[0], t.split('/')[-1].split('.')[0], g.split('/')[-1].split('.')[0]
    assert c.split('/')[-1].split('.')[0] == t.split('/')[-1].split('.')[0] == g.split('/')[-1].split('.')[0]
    data = note.createTraining(c, t, g)
    if type(data) == type(None):
      continue
    data.apply(addGold, axis=1)

  for c, t, p in zip(c_files, t_files, p_files):
    #print c.split('/')[-1].split('.')[0], t.split('/')[-1].split('.')[0], p.split('/')[-1].split('.')[0]
    assert c.split('/')[-1].split('.')[0] == t.split('/')[-1].split('.')[0] == p.split('/')[-1].split('.')[0]
    data = note.createTraining(c, t, p)
    if type(data) == type(None):
      continue
    data.apply(addPred, axis=1)

  TP = 0
  FP = 0
  FN = 0

  g_labels = list()
  p_labels = list()
  for p in pred.keys():
    if type(gold[p]) != str:
      gold[p] = 'N%s%s' % (p[-2][:2].upper(), p[-1][:2].upper())
      FP += 1

  for g in gold.keys():
    if type(pred[g]) != str:
      if gold[g][0] != "N":
        p_labels.append('N%s%s' % (g[-2][:2].upper(), g[-1][:2].upper()))
        g_labels.append(gold[g])
      FN += 1
    else:
      TP += 1
# This ignores concept pairs that did not have a relation.
# Meaning this metric won't take into account Falsely labeled pairs.
      if gold[g][0] != "N":
        p_labels.append(pred[g])
        g_labels.append(gold[g])

  if (TP + FP):
    P = float(TP) / (TP + FP)
  else:
    P = 0
  if (TP + FN):
    R = float(TP) / (TP + FN)
  else:
    R = 0
  if (P + R):
    F1 = 2 * (P * R) / (P + R)
  else:
    F1 = 0

  labels = list(set(p_labels + g_labels))
  labels.sort()
  print "-" * 80
  print "Relation Detection Statistics:"
  print ""
  print "\tTrue positives: ",  TP
  print "\tFalse positives:",  FP
  print "\tFalse negatives:",  FN
  print ""
  print "\tF1: %.4f\n\tPrecision: %.4f\n\tRecall: %.4f" % (F1, P, R)
  print ""
  print "-" * 80
  print "Classification Statistics:"
  print ""
  _LABELS = list(set(['PIP', 'TeCP', 'TeRP', 'TrAP',
                      'TrCP', 'TrIP', 'TrNAP', 'TrWP']).union(p_labels))
  _LABELS.sort()
  print "\t F1:        %.4f" % metrics.f1_score(g_labels,
                                               p_labels,
                                               average='micro',
                                               labels=_LABELS)
  print ""
  for label in _LABELS:
    print "%5s " % label,
  print ""
  confusion = metrics.confusion_matrix(g_labels,
                                       p_labels,
                                       )#labels=_LABELS)
  for row in confusion:
    for col in row:
      print "%4d" % col, " ",
    print
  print "-" * 80
  print ""

if __name__ == '__main__':
  # Uncomment to run tests
  #import doctest
  #doctest.testmod()

  if (len(sys.argv) < 2):
    print "USAGE: clirel.py train|test|eval data_dir [model|pred_dir] [options]"
    sys.exit(1)

  if (sys.argv[1] == "train"):
    try:
      t_dir = sys.argv[2]
      model = sys.argv[3]
      opts  = sys.argv[4:]
    except:
      print "Invalid arguemnts"
      print "USAGE: clirel.py train data_dir model options"
      sys.exit(1)
    print "Training..."
    train(t_dir, model, opts)
  elif (sys.argv[1] == "test"):
    try:
      t_dir = sys.argv[2]
      model = sys.argv[3]
      opts  = sys.argv[4:]
    except:
      print "Invalid arguments"
      print "USAGE: clirel.py test data_dir model options"
      sys.exit(1)
    print "Predicting..."
    predict(t_dir, model, opts)
  elif (sys.argv[1] == "eval"):
    try:
      e_dir = sys.argv[2]
      pred  = sys.argv[3]
    except:
      print "Invalid arguments"
      print "USAGE: clirel.py eval data_dir pred_dir"
      sys.exit(1)
    print "Evaluating..."
    evaluate(e_dir, pred)
  else:
    print "USAGE: clirel.py train|test|eval data_dir [model|pred_dir] [options]"
    sys.exit(1)

  # Uncomment to test evaluate
  #evaluate('i2b2_examples/rel/', 'predictions/')
  #print "train"
  #train('i2b2_examples/', 'kim/', ['i2b2_examples/parse'])
  #print "predict"
  #predict('i2b2_examples/', 'kim/', ['i2b2_examples/parse'])
  #print "evaluate"
  #evaluate('i2b2_examples/rel/', 'predictions/')
  #print "train"
  #train('i2b2_examples/', 'blrandom/')
  #print "predict"
  #predict('i2b2_examples/', 'blrandom/')
  #print "evaluate"
  #evaluate('i2b2_examples/concept',
  #         'i2b2_examples/txt',
  #         'i2b2_examples/rel/',
  #         'predictions/')
  #print "train"
  #train('i2b2_examples/', 'kim/', ['suffix'])
  #print "predict"
  #predict('i2b2_examples/', 'kim/', ['suffix'])
  #print "evaluate"
  #evaluate('i2b2_examples/rel/', 'predictions/')
  #print "train"
  #train('../data/train/', 'kim/', ['../data/train/parse'])
  #train('../data/train/', 'blrandom/', ['../data/train/parse'])
  #print "predict"
  #predict('../data/train/', 'blrandom/', ['../data/train/parse'])
  #predict('../data/train/', 'kim/', ['../data/train/parse'])
  #print "evaluate"
  #evaluate('../data/train/concept',
  #         '../data/train/txt',
  #         '../data/train/rel', 'predictions/')
  #print "predict"
  #predict('../data/test/', 'kim/', ['../data/test/parse'])
#  print "evaluate"
#  evaluate('../data/test/concept',
#           '../data/test/txt',
#           '../data/test/rel', 'predictions/')
