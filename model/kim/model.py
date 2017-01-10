"""
 Text-Machine Lab: CliRel

 File Name : model.py

 Creation Date : 10-10-2016

 Created By : Renan Campos

 Purpose : Defines an svm with a custom kernel.
           Kernels defined below.
           This module defines a composite kernel consisting of an entity
           kernel and a convolution tree kernel.
           based on 'Extracting Clinical Relations in Electronic Health Records
           Using Enriched Parse Trees' by (Jisung Kim, et al.)

"""


import tree
import bParser
import numpy as np

import os
import sys
import subprocess
import pandas as pd

def absPath(path):
  """ Return absolute path from where this file is located """
  return os.path.join(os.path.dirname(os.path.abspath(__file__)), path)

# Labels svm should train.
_LABELS = ['TrIP','TrWP','TrCP',
           'TrAP','TrNAP','TeRP',
           'TeCP','PIP', 'NTrP',
           'NTeP','NPP']


def genNeg(x, l=None):
  """
    Helper, generates negative examples.
    NTrP: No relationship between a treatment and a problem.
    NTeP: No relationship between a test and a problem.
    NPP:  No relationship between a problem and a problem.
    >>> genNeg(test1)
    'NTrP'
    >>> genNeg(test2)
    'NPP'
    >>> genNeg(test3)
    'NTeP'
    >>> genNeg(test4)
    'TeIP'
    >>> genNeg(test5)
    nan
    >>> genNeg(test6)
    'NTrP'
    >>> genNeg(test7)
    'NTeP'
    >>> genNeg(test8)
    'TeIP'
    >>> genNeg(test9)
    nan
  """
  # Special case where other order does have a valid label.
  if type(l) != type(None) and not l[(l.lineNum   ==  x.lineNum)  &
                                     (l.conStart1 == x.conStart2) &
                                     (l.conEnd1   == x.conEnd2)   &
                                     (l.conStart2 == x.conStart1) &
                                     (l.conEnd2   == x.conEnd1)   ].empty:
    return x.relType

  # Special cases due to noisy training data
  if x.conType1 == 'test' and x.conType2 == 'test':
    return np.nan

  if x.conType1 == 'treatment' and x.conType2 == 'treatment':
    return np.nan

  if not pd.isnull(x.relType):
    return x.relType

  if (x.conType1 == 'treatment' and x.conType2 == 'problem') or \
     (x.conType2 == 'treatment' and x.conType1 == 'problem'):
    return 'NTrP'

  if (x.conType1 == 'test' and x.conType2 == 'problem') or \
     (x.conType2 == 'test' and x.conType1 == 'problem'):
    return 'NTeP'

  if x.conType1 == 'problem' and x.conType2 == 'problem':
    return 'NPP'

  return x.relType

def filterUnlabeled(x):
  if x.relType in _LABELS[:8]:
    return x.relType
  return np.nan

# Only want one of the two negative labeled examples for each entry
def filterNegLabeled(x):
  if x.relType in _LABELS[-3:] and x.conStart1 > x.conStart2:
    return np.nan
  return x.relType


#
# Feature extraction helpers
#
I = 1

def insert(x):
  if int(x.conStart2) > int(x.conStart1):
    cStart1 = int(x.conStart1)
    cEnd1   = int(x.conEnd1)
    cType1  = x.conType1
    cStart2 = int(x.conStart2)
    cEnd2   = int(x.conEnd2)
    cType2  = x.conType2
  else:
    cStart1 = int(x.conStart2)
    cEnd1   = int(x.conEnd2)
    cType1  = x.conType2
    cStart2 = int(x.conStart1)
    cEnd2   = int(x.conEnd1)
    cType2  = x.conType1
  if V:
    print "Inserting: %s, line: %s" % (x.fileName, x.lineNum)
  return tree.createString(tree.insert(
           tree.createTree(x.parse),
           cStart1,
           cEnd1,
           cType1,
           cStart2,
           cEnd2,
           cType2))

def suffix(x):
  if int(x.conStart2) > int(x.conStart1):
    cStart1 = int(x.conStart1)
    cEnd1   = int(x.conEnd1)
    cType1  = x.conType1
    cStart2 = int(x.conStart2)
    cEnd2   = int(x.conEnd2)
    cType2  = x.conType2
  else:
    cStart1 = int(x.conStart2)
    cEnd1   = int(x.conEnd2)
    cType1  = x.conType2
    cStart2 = int(x.conStart1)
    cEnd2   = int(x.conEnd1)
    cType2  = x.conType1
  if V:
    print "Suffixing: %s, line: %s" % (x.fileName, x.lineNum)
  return tree.createString(tree.suffix(
           tree.createTree(x.parse),
           cStart1,
           cEnd1,
           cType1,
           cStart2,
           cEnd2,
           cType2))

def spt(x):
  if int(x.conStart2) > int(x.conStart1):
    cStart1 = int(x.conStart1)
    cEnd1   = int(x.conEnd1)
    cStart2 = int(x.conStart2)
    cEnd2   = int(x.conEnd2)
  else:
    cStart1 = int(x.conStart2)
    cEnd1   = int(x.conEnd2)
    cStart2 = int(x.conStart1)
    cEnd2   = int(x.conEnd1)
  if V:
    print "Finding spt for: %s, line: %s" % (x.fileName, x.lineNum)
  return tree.createString(tree.spt(
           tree.createTree(x.parse),
           cStart1,
           cEnd2))

def entityFeature(x):
  """
    Returns a two-hot vector of the types of entities contained in the entry.
    Note: vector representation is of the form <index>:1, 0 for all else.
    1 - first test
    2 - first treatment
    3 - first problem
    4 - second test
    5 - second treatment
    6 - second problem
    >>> entityFeature(test1)
    '2:1 6:1'
    >>> entityFeature(test2)
    '3:1 6:1'
    >>> entityFeature(test3)
    '1:1 6:1'
    >>> entityFeature(test4)
    '3:1 4:1'
    >>> entityFeature(test5)
    Traceback (most recent call last):
      ...
    ValueError: Invalid concept types given: treatment and test.
    >>> entityFeature(test6)
    '3:1 5:1'
    >>> entityFeature(test7)
    '3:1 4:1'
    >>> entityFeature(test9)
    Traceback (most recent call last):
      ...
    ValueError: Invalid concept types given: test and treatment.
  """
  if V:
    print "Finding entity vector for: %s, line: %s" % (x.fileName, x.lineNum)
  cons = (x.conType1, x.conType2)
  if cons == ('test', 'problem'):
    return '1:1 6:1'
  if cons == ('problem', 'test'):
    return '3:1 4:1'
  if cons == ('treatment', 'problem'):
    return '2:1 6:1'
  if cons == ('problem', 'treatment'):
    return '3:1 5:1'
  if cons == ('problem', 'problem'):
    return '3:1 6:1'
  raise ValueError('Invalid concept types given: %s and %s.' % (cons[0], cons[1]))


def train(data, flags):
  # Initialize training files
  for label in _LABELS:
    f_name = os.path.join(absPath('./svm'), label + '.tmp')
    with open(f_name, 'w') as f:
      pass

  parses = note.filterFiles(flags[0], 'parse')

  for ((c,t,r),p) in zip(data, parses):
    X = note.createTraining(c, t, r)
    if type(X) == type(None) or X.empty:
      continue
    # Generate negative examples
    X['relType'] = X.apply(genNeg, axis=1, args=(X[X['relType'].notnull()],))

    # Split number of negative examples in half by taking only the ordered ones.
    X['relType'] = X.apply(filterNegLabeled, axis=1)

    # Filter invalid entries (i.e. test/treatment combinations)
    X = X[X['relType'].notnull()]

    if X.empty:
      continue

    # Obtain parse trees
    P = bParser.extractPars(p)
    X = pd.merge(X, P, how='left')

    # Enrich parse trees
    if len(flags) > 1:
      if flags[1] == 'insert':
        X['parse'] = X.apply(insert, axis=1)
      elif flags[1] == 'suffix':
        X['parse'] = X.apply(suffix, axis=1)
      else:
        return 'Invalid flag.'
    else:
      X['parse'] = X.apply(spt, axis=1)

    # Create entity vectors
    X['vec'] = X.apply(entityFeature, axis=1)

    # Write to svm files
    for label in _LABELS:
      f_name = os.path.join(absPath('./svm'), label + '.tmp')
      with open(f_name, 'a') as f:
        def svmTrain(x):
          """
            Temporary function to write svm training files.
          """
          if x.relType == label:
            y = '1'
          else:
            y = '-1'
          if x.parse == '()':
            p = ' '
          else:
            p = ' ' + x.parse + ' '

          out = y + ' |BT|' + p + '|ET| ' + x.vec + ' |EV|\n'
          f.write(out)
          return

        X.apply(svmTrain, axis=1)

  # Train svms
  for label in _LABELS:
    f_name = os.path.join(absPath('./svm'), label + '.tmp')
    subprocess.call([absPath('./svm-light-TK-1.2.1/svm_learn'),
                     '-t', '5',
                     '-S', '1',
                     '-D', '1',
                     '-r', '1',
                     '-c', '0.5',
                     '-d', '2',
                     '-T', '3.35',
                     '-N', '3',
                     '-W', 'S',
                     '-v', '0',
                     f_name,
                     f_name.split('.tmp')[0] + '.svm',
                    ])

    os.remove(f_name)

  # Returns nothing on success
  return

def predict(data, flags):

  parses = note.filterFiles(flags[0], 'parse')

  for ((c,t),p) in zip(data, parses):
    X = note.createTesting(c, t)
    if type(X) == type(None) or X.empty:
      f_name = os.path.basename(t).split(".")[0]
      with open(os.path.join(absPath('../../predictions'),
                               f_name + '.pred'), 'w') as f:
        continue

    # Generate negative examples
    X['relType'] = X.apply(genNeg, axis=1)

    # Filter invalid entries (i.e. test/treatment combinations)
    X = X[X['relType'].notnull()]
    if X.empty:
      f_name = os.path.basename(t).split(".")[0]
      with open(os.path.join(absPath('../../predictions'),
                               f_name + '.pred'), 'w') as f:
        continue

    # Obtain parse trees
    P = bParser.extractPars(p)
    X = pd.merge(X, P, how='left')

    # Enrich parse trees
    if len(flags) > 1:
      if flags[1] == 'insert':
        X['parse'] = X.apply(insert, axis=1)
      elif flags[1] == 'suffix':
        X['parse'] = X.apply(suffix, axis=1)
      else:
        return 'Invalid flag.'
    else:
      X['parse'] = X.apply(spt, axis=1)

    # Create entity vectors
    X['vec'] = X.apply(entityFeature, axis=1)


    # Make predictions
    f_name = os.path.join(absPath("./svm"), 'predict.tmp')

    first = True
    with open(f_name, 'w') as f:
      def svmPred(x):
        """
          Temporary function to write svm training files.
        """
        if x.parse == '()':
          p = ' '
        else:
          p = ' ' + x.parse + ' '
        out = '|BT| (' + p + ') |ET| ' + x.vec + ' |EV|\n'
        f.write(out)
        return

      X.apply(svmPred, axis=1)

    for label in _LABELS:
      m_name = os.path.join(absPath("./svm"), label + '.svm')
      r_name = os.path.join(absPath("./svm"), label + '.predict')
      subprocess.call([absPath('./svm-light-TK-1.2.1/svm_classify'),
                       f_name,
                       m_name,
                       r_name])
      r_label = list()
      with open(r_name, 'r') as f:
        for line in f:
          r_label.append(float(line))
      if first:
        results = np.array(r_label).reshape(len(r_label),1)
        first = False
      else:
        results = np.concatenate((results,
                                  np.array(r_label).reshape(len(r_label),1)),
                                  axis=1)
      os.remove(r_name)
    os.remove(f_name)

    out = [_LABELS[r] for r in results.argmax(axis=1)]

    X['relType'] = out

    # Write predictions to file
    f_name = set(X['fileName']).pop()

    # Filter out non-positive labels
    X['relType'] = X.apply(filterUnlabeled,axis=1)
    X = X[X['relType'].notnull()]

    with open(os.path.join(absPath('../../predictions'),
                             f_name + '.pred'), 'w') as f:
      def writeToFile(d):
        f.write(note.writeRel(d) + '\n')

      if X.empty:
        continue

      X.apply(writeToFile, axis=1)

  return

if __name__ == '__main__':
  from pandas import Series
  from numpy import nan
  V = False
  test1  = Series({'conType1': 'treatment', 'conType2': 'problem', 'relType': nan})
  test2  = Series({'conType1': 'problem',   'conType2': 'problem', 'relType': nan})
  test3  = Series({'conType1': 'test',      'conType2': 'problem', 'relType': nan})
  test4  = Series({'conType1': 'problem',   'conType2': 'test',    'relType': 'TeIP'})
  test5  = Series({'conType1': 'treatment', 'conType2': 'test',    'relType': nan})
  test6  = Series({'conType2': 'treatment', 'conType1': 'problem', 'relType': nan})
  test7  = Series({'conType2': 'test',      'conType1': 'problem', 'relType': nan})
  test8 = Series({'conType2': 'problem',   'conType1': 'test',    'relType': 'TeIP'})
  test9 = Series({'conType2': 'treatment', 'conType1': 'test',    'relType': nan})
  import doctest
  doctest.testmod()
else:
 # V = False
  V = True

  sys.path.append(absPath('../'))
  import note
