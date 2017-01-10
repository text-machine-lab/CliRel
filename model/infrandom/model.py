"""
 Text-Machine Lab: CliRel

 File Name : model.py

 Creation Date : 10-10-2016

 Created By : Renan Campos

 Purpose : Defines a simple baseline model that assigns a random label.

"""

import note

import os
import random
import numpy as np

# Labels svm should train.
_LABELS = ['TrIP','TrWP','TrCP',
           'TrAP','TrNAP','TeRP',
           'TeCP','PIP']

def absPath(path):
  """ Return absolute path from where this file is located """
  return os.path.join(os.path.dirname(os.path.abspath(__file__)), path)


def almostRandom(x):
  if (x.conType1 == 'treatment' and x.conType2 == 'problem') or \
     (x.conType2 == 'treatment' and x.conType1 == 'problem'):
    return random.choice(_LABELS[:5] + ['NTrP'])

  if (x.conType1 == 'test' and x.conType2 == 'problem') or \
     (x.conType2 == 'test' and x.conType1 == 'problem'):
    return random.choice(_LABELS[5:7] + ['NTeP'])

  if x.conType1 == 'problem' and x.conType2 == 'problem':
    return random.choice(_LABELS[7:] + ['NPP'])

  else:
    return random.choice(_LABELS + ['NTrP', 'NTeP', 'NPP'])

def filterUnlabeled(x):
  if x.relType not in ['NTrP','NTeP','NPP']:
    return x.relType
  return np.nan

def train(data, flags):
  # No training required.
  return

def predict(data, flags):

  # Get test data
  for (c,t) in data:
    X = note.createTesting(c, t)
    if type(X) == type(None) or X.empty:
      f_name = os.path.basename(t).split(".")[0]
      with open(os.path.join(absPath('../predictions'),
                               f_name + '.pred'), 'w') as f:
        continue

    # Assign random label based on entity types:
    X['relType'] = X.apply(almostRandom, axis=1)


    # Filter out non-positive labels
    # Write predictions to file
    f_name = set(X['fileName']).pop()
    X['relType'] = X.apply(filterUnlabeled,axis=1)
    X = X[X['relType'].notnull()]
    with open(os.path.join(absPath('../predictions'),
                             f_name + '.pred'), 'w') as f:
      def writeToFile(d):
        f.write(note.writeRel(d) + '\n')

      if X.empty:
        continue

      X.apply(writeToFile, axis=1)
  return
