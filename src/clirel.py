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
  con = os.path.join(t_dir, 'concept')
  txt = os.path.join(t_dir, 'txt')
  rel = os.path.join(t_dir, 'rel')

  data = note.createEntries(con, txt, rel)

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
  """
    Output should be the data with labels. 
    For the example model, the new labels are all PIP
    >>> predict('i2b2_examples/', 'model_example/').ix[0]
    conEnd1                                              1
    conEnd2                                              4
    conStart1                                            0
    conStart2                                            3
    conText1                                This treatment
    conText2                               medical problem
    conType1                                     treatment
    conType2                                       problem
    fileName                                        health
    lineNum                                              1
    relType                                            PIP
    text         This treatment improves medical problem .
    Name: 0, dtype: object
  """
  con = os.path.join(t_dir, 'concept')
  txt = os.path.join(t_dir, 'txt')
  data = note.createEntries(con, txt)

  for f in note.filterFiles(absPath('predictions'), 'pred'):
    os.remove(f)

  # import the model.
  # The model will be loaded as a module. This provides modularity for the
  # assumption that the model is implemented with a 'model.py' in its main dir. 
  sys.path.insert(0, model_path)
  import model
  sys.path = sys.path[1:]

  out =  model.predict(data, model_flags)
  data["relType"] = out

  for each in set(data['fileName']):
    with open(os.path.join(absPath('predictions'), 
                             each + '.pred'), 'w') as f:
      def writeToFile(d):
        f.write(note.writeRel(d) + '\n')
      data.apply(writeToFile, axis=1)

  del model

  return data

def evaluate(g_dir, p_dir):
  """
    Extracts the relation files from the gold directory and the 
    prediciton directory, and calculates the F1, recall, and precision.
    For this current iteration of the task, we are only concerned if the model
    is able to identify a relation between two concepts (ignoring order).
  """
  gold = dict()
  pred = dict()

  def addGold(d):
    ind = [int(d.conStart1), int(d.conEnd1), int(d.conStart2), int(d.conEnd2)]
    # Ignore ordering
    ind.sort()
    ind.append(d.lineNum)
    ind.append(d.fileName)
    gold[tuple(ind)] = d.relType

  for g in note.filterFiles(g_dir, 'rel'):
    rel = note.extractRels(g) 
    rel.apply(addGold, axis=1) 
  
  def addPred(d):
    ind = [int(d.conStart1), int(d.conEnd1), int(d.conStart2), int(d.conEnd2)]
    # Ignore ordering
    ind.sort()
    ind.append(d.lineNum)
    ind.append(d.fileName)
    pred[tuple(ind)] = d.relType

  for p in note.filterFiles(p_dir, 'pred'):
    rel = note.extractRels(p) 
    rel.apply(addPred, axis=1) 

  TP = 0
  FP = 0
  FN = 0

  g_labels = list()
  p_labels = list()
  for p in pred.keys():
    try:
      gold[p]
    except KeyError:
      # Ignore negative classification
      if pred[p][0] != 'N':
        FP += 1
  
  for g in gold.keys():
    g_labels.append(gold[g])
    if pred[g][0] != 'N':
      TP += 1
    else:
      FP += 1
    p_labels.append(pred[g])
  
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
  print "\tF1:        %.4f" % metrics.f1_score(g_labels, 
                                               p_labels, 
                                               average='micro')
  print "\tPrecision: %.4f" % metrics.precision_score(g_labels, 
                                                      p_labels,
                                                      average='micro')
  print "\tRecall:    %.4f" % metrics.recall_score(g_labels, 
                                                   p_labels,
                                                   average='micro')
  print ""
  print (list(set(g_labels)))
  print metrics.confusion_matrix(g_labels, 
                                 p_labels, 
                                 labels=list(set(g_labels)))
  print "-" * 80
  print ""
 
if __name__ == '__main__':
  # Uncomment to run tests
  #import doctest
  #doctest.testmod()
  # Uncomment to test evaluate
  #evaluate('i2b2_examples/rel/', 'predictions/')
  print "train"
  train('i2b2_examples/', 'kim/')
  print "predict"
  predict('i2b2_examples/', 'kim/')
  print "evaluate"
  evaluate('i2b2_examples/rel/', 'predictions/')
  #print "train"
  #train('i2b2_examples/', 'kim/', ['insert'])
  #print "predict"
  #predict('i2b2_examples/', 'kim/', ['insert'])
  #print "evaluate"
  #evaluate('i2b2_examples/rel/', 'predictions/')
  #print "train"
  #train('i2b2_examples/', 'kim/', ['suffix'])
  #print "predict"
  #predict('i2b2_examples/', 'kim/', ['suffix'])
  #print "evaluate"
  #evaluate('i2b2_examples/rel/', 'predictions/')
  #print "train"
  #train('../data/train/', 'kim/')
  #print "predict"
  #predict('../data/train/', 'kim/')
  #print "evaluate"
  #evaluate('../data/train/rel/', 'predictions/')
