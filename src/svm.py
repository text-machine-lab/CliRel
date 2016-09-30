""" 
 Text-Machine Lab: CliRel

 File Name : svm.py

 Creation Date : 09-06-2016

 Created By : Renan Campos

 Purpose : Defines an svm with a custom kernel.
           Kernels defined below.
           This module defines a composite kernel consisting of an entity 
           kernel and a convolution tree kernel.
           based on 'Extracting Clinical Relations in Electronic Health Records
           Using Enriched Parse Trees' by (Jisung Kim, et al.)
"""

import os
import dill as pickle

import sklearn
import numpy as np

from math import e, sqrt
import subprocess

from futilities import abs_path

_CONS   = dict((v,k) for k,v in enumerate(['problem','treatment','test']))
_LABELS = dict((k,v) for k,v in enumerate(['TrIP','TrWP','TrCP',
                                           'TrAP','TrNAP','TeRP',
                                           'TeCP','PIP', 'NTrP', 
                                           'NTeP','NPP']))
MODE = 'spt'

from sklearn.cross_validation import KFold
from sklearn.metrics import f1_score

def hotty(con1, con2):
  """
  if con1 == 'problem' and con2 == 'problem':
    #return " 1:0 2:0 3:0 4:1"
    return " 1:1 4:1"
  if con1 == 'problem' and con2 == 'treatment':
    #return " 1:1 2:0 3:0 4:0 5:1 6:0"
    return " 1:1 5:1"
  if con1 == 'problem' and con2 == 'test':
    #return " 1:1 2:0 3:0 4:0 5:0 6:1"
    return " 1:1 6:1"
  
  if con1 == 'treatment' and con2 == 'problem':
    #return " 1:0 2:1 3:0 4:1 5:0 6:0"
    return " 2:1 4:1"
  if con1 == 'treatment' and con2 == 'treatment':
    #return " 1:0 2:1 3:0 4:0 5:1 6:0"
    return " 2:1 5:1"
  if con1 == 'treatment' and con2 == 'test':
    #return " 1:0 2:1 3:0 4:0 5:0 6:1"
    return " 2:1 6:1"
  
  if con1 == 'test' and con2 == 'problem':
    #return " 1:0 2:0 3:1 4:1 5:0 6:0"
    return " 3:1 4:1"
  if con1 == 'test' and con2 == 'treatment':
    #return " 1:0 2:0 3:1 4:0 5:1 6:0"
    return " 3:1 5:1"
  if con1 == 'test' and con2 == 'test':
    #return " 1:0 2:0 3:1 4:0 5:0 6:1"
    return " 3:1 6:1"
  """
  cons = (con1, con2)
  if cons == ('test', 'problem') or cons == ('problem', 'test'):
    return " 1:1 3:1"
  if cons == ('treatment', 'problem') or cons == ('problem', 'treatment'):
    return " 2:1 3:1"
  if cons == ('problem', 'problem'):
    return " 3:1 4:1"

class Model:
  def __init__(self):
    self.name = str(os.getpid()) # Name files will be trained on.
    self.mode = MODE

  def train(self, X, Y):
    """
      Trains a classifier using a custom kernel.
      Note: X is a list of entries Y is a list of labels 
    """
    for label in _LABELS.values():
      f_name = os.path.join(abs_path('../model'), self.name + '.' + label + '.tmp')
      with open(f_name, 'w') as f:
        for y, x in zip(Y,X):
          if y == label:
            y = '1'
          else:
            y = '-1'
         
          out = (str(y) + " |BT| " + str(x.getEnrichedTree(self.mode)) + " |ET|"
                 + hotty(x.getConcepts()[0].label, x.getConcepts()[1].label)
                 + " |EV|\n")
          f.write(out)

      subprocess.call([abs_path('../bin/svm-light-TK-1.2.1/svm_learn'), 
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
      
      #os.remove(f_name)

    
  def predict(self, X):
    """
      Uses trained support vector classifier to predict label.
    """
    f_name = os.path.join(abs_path("../model"), self.name + '.predict')

    first = True
    with open(f_name, 'w') as f:
      for x in X:
        out = ("|BT| " + str(x.getEnrichedTree(self.mode)) + " |ET|"
               + hotty(x.getConcepts()[0].label, x.getConcepts()[1].label)
               + " |EV|\n")
        f.write(out)
    for label in _LABELS.values():
      m_name = os.path.join(abs_path("../model"), self.name + '.' + label + '.svm')
      r_name = os.path.join(abs_path("../results"), self.name + '.' + label + '.predict')
      subprocess.call([abs_path('../bin/svm-light-TK-1.2.1/svm_classify'), 
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
        results = np.concatenate((results,np.array(r_label).reshape(len(r_label),1)),axis=1)
      os.remove(r_name)    
    os.remove(f_name)
   
    print "Stats"
    for i in results:
      print i
    return [_LABELS[r] for r in results.argmax(axis=1)]
    
              

  def save(self, p_file):
    """
      Saves svm to pickle file moves svm files to model dir.
    """
    with open(p_file, 'wb') as f:
      pickle.dump(self, f)

  def load(self, p_file):
    """
      Loads svm from pickle file
    """
    with open(p_file, 'rb') as f:
      obj = pickle.load(f)
    self.name = obj.name
    self.mode = obj.mode
