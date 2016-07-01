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

class Model:
  def __init__(self):
    self.name = str(os.getpid()) # Name files will be trained on.

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
          out = (str(y) + " |BT| " + x.getParses()[0] + " |ET|"
                 + " 1:" + str(_CONS[x.getConcepts()[0].label]) 
                 + " 2:" + str(_CONS[x.getConcepts()[1].label]) + " |EV|\n")
          f.write(out)


      subprocess.call([abs_path('../bin/svm-light-TK-1.2.1/svm_learn'), 
                       '-t', '4', 
                       '-u', '.5', 
                       f_name,
                       f_name.split('.tmp')[0] + '.svm'])
      
      os.remove(f_name)

    
  def predict(self, X):
    """
      Uses trained support vector classifier to predict label.
    """
    f_name = os.path.join(abs_path("../model"), self.name + '.predict')

    first = True
    with open(f_name, 'w') as f:
      for x in X:
        out = ("|BT| " + x.getParses()[0] + " |ET|"
               + " 1:" + str(_CONS[x.getConcepts()[0].label]) 
               + " 2:" + str(_CONS[x.getConcepts()[1].label]) + " |EV|\n")
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
