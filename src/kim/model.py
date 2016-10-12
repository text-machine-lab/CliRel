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

import parser

import pandas as pd

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

def train(data, flags):
# Training
# 1. Generate negative examples
# 2. Obtain parse trees by running Berkeley parser
# 3. Produce enriched parse trees 
# 4. train a SVM with examples of which features are entity types and enriched parse trees.
# Note: The entity feature is higher when the two relations share the same entity types 
# of their first and second entities.

  # Generate Negative Examples
  data['relType'] = data.apply(genNeg, axis=1)

  # Obtain parse trees
  global P 
  P = parser.BerkeleyParser()
  data['parse'] = data.apply(parse, axis=1)
  P.close()
  del P

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
