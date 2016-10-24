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

import bParser as parser
import tree
import numpy as np

import os
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


def genNeg(x):
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

#
# Feature extraction helpers
#

def parse(x):
  """
    Returns a parse of the given text
    This takes a second for the first sentence because the module has to load.
    >>> parse(Series({'text': 'Hello'})).strip()
    '(INTJ (UH Hello))'
    >>> parse(Series({'text': 'This is a test sentence .'})).strip()
    '(S (NP (DT This)) (VP (VBZ is) (NP (DT a) (NN test) (NN sentence))) (. .))'
  """
  return P.parse(x.text).strip()[2:-2]

def insert(x):
  return tree.createString(tree.insert(
           tree.createTree(x.parse), 
           int(x.conStart1), 
           int(x.conEnd1),
           x.conType1,
           int(x.conStart2),
           int(x.conEnd2),
           x.conType2))

def suffix(x):
  return tree.createString(tree.suffix(
           tree.createTree(x.parse), 
           int(x.conStart1), 
           int(x.conEnd1),
           x.conType1,
           int(x.conStart2),
           int(x.conEnd2),
           x.conType2))

def spt(x):
  return tree.createString(tree.spt(
           tree.createTree(x.parse), 
           int(x.conStart1), 
           int(x.conEnd2)))

def entityFeature(x):
  """
    Returns a two-hot vector of the types of entities contained in the entry.
    Note: Order is ignored. (T,P) == (P,T)
    Note: vector representation is of the form <index>:1, 0 for all else.
    1 - test
    2 - treatment
    3 - problem
    4 - second problem
    >>> entityFeature(test1)
    '2:1 3:1'
    >>> entityFeature(test2)
    '3:1 4:1'
    >>> entityFeature(test3)
    '1:1 3:1'
    >>> entityFeature(test4)
    '1:1 3:1'
    >>> entityFeature(test5)
    Traceback (most recent call last):
      ...
    ValueError: Invalid concept types given: treatment and test.
    >>> entityFeature(test6)
    '2:1 3:1'
    >>> entityFeature(test7)
    '1:1 3:1'
    >>> entityFeature(test9)
    Traceback (most recent call last):
      ...
    ValueError: Invalid concept types given: test and treatment.
  """
  cons = (x.conType1, x.conType2)
  if cons == ('test', 'problem') or cons == ('problem', 'test'):
    return '1:1 3:1'
  if cons == ('treatment', 'problem') or cons == ('problem', 'treatment'):
    return '2:1 3:1'
  if cons == ('problem', 'problem'):
    return '3:1 4:1'
  raise ValueError('Invalid concept types given: %s and %s.' % (cons[0], cons[1]))


def train(data, flags):

  # Generate Negative Examples
  data['relType'] = data.apply(genNeg, axis=1)

  # Filter invalid entries (i.e. test/treatment combinations)
  data = data[data['relType'].notnull()]

  # Obtain parse trees
  global P 
  P = parser.BerkeleyParser()
  data['parse'] = data.apply(parse, axis=1)
  P.close()
  del P

  # Enrich parse trees
  if flags:
    if flags[0] == 'insert':
      data['parse'] = data.apply(insert, axis=1)
    if flags[0] == 'suffix':
      data['parse'] = data.apply(suffix, axis=1)
    else:
      return 'Invalid flag.'
  else:
    data['parse'] = data.apply(spt, axis=1)

  # Create entity vectors
  data['vec'] = data.apply(entityFeature, axis=1)

  # Train svms
  for label in _LABELS:
    f_name = os.path.join(absPath('./svm'), label + '.tmp')
    with open(f_name, 'w') as f:
      def svmTrain(x):
        """
          Temporary function to write svm training files.
        """
        if x.relType == label:
          y = '1'
        else:
          y = '-1'
        out = y + ' |BT| ( ' + x.parse + ' ) |ET| ' + x.vec + ' |EV|\n'
        f.write(out)
        return

      data.apply(svmTrain, axis=1)

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
  
  del data['parse']
  del data['vec']
  
  # Returns nothing on sucess.
  return 

def predict(data, flags):

  # Generate Negative Examples - to ensure only valid entries are being labeled.
  data['relType'] = data.apply(genNeg, axis=1)

  # Filter invalid entries (i.e. test/treatment combinations)
  data = data[data['relType'].notnull()]

  # Obtain parse trees
  global P 
  P = parser.BerkeleyParser()
  data['parse'] = data.apply(parse, axis=1)
  P.close()
  del P

  # Enrich parse trees
  if flags:
    if flags[0] == 'insert':
      data['parse'] = data.apply(insert, axis=1)
    if flags[0] == 'suffix':
      data['parse'] = data.apply(suffix, axis=1)
    else:
      return 'Invalid flag.'
  else:
    data['parse'] = data.apply(spt, axis=1)

  # Create entity vectors
  data['vec'] = data.apply(entityFeature, axis=1)

  # Train svms
  f_name = os.path.join(absPath("./svm"), 'predict.tmp')

  first = True
  with open(f_name, 'w') as f:
    def svmPred(x):
      """
        Temporary function to write svm training files.
      """
      out = '|BT| ( ' + x.parse + ' ) |ET| ' + x.vec + ' |EV|\n'
      f.write(out)
      return
    data.apply(svmPred, axis=1)
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
  #os.remove(f_name)
  
  del data['parse']
  del data['vec']

  out = [_LABELS[r] for r in results.argmax(axis=1)]

  return out

if __name__ == '__main__':
  from pandas import Series
  from numpy import nan
  test1  = Series({'conType1': 'treatment', 'conType2': 'problem', 'relType': nan})
  test2  = Series({'conType1': 'problem',   'conType2': 'problem', 'relType': nan})
  test3  = Series({'conType1': 'test',      'conType2': 'problem', 'relType': nan})
  test4  = Series({'conType1': 'problem',   'conType2': 'test',    'relType': 'TeIP'})
  test5  = Series({'conType1': 'treatment', 'conType2': 'test',    'relType': nan})
  test6  = Series({'conType2': 'treatment', 'conType1': 'problem', 'relType': nan})
  test7  = Series({'conType2': 'test',      'conType1': 'problem', 'relType': nan})
  test8 = Series({'conType2': 'problem',   'conType1': 'test',    'relType': 'TeIP'})
  test9 = Series({'conType2': 'treatment', 'conType1': 'test',    'relType': nan})
  global P
  P = parser.BerkeleyParser()
  import doctest
  doctest.testmod()
  P.close()
