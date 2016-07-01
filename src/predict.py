""" 
 Text-Machine Lab: CliRel

 File Name : predict.py

 Creation Date : 15-06-2016

 Created By : Renan Campos

 Purpose : Prediction script

"""

import sys
import numpy as np


import note 
import svm as ml
from futilities import abs_path

def main(t_dir, model_path, res_dir, v):
  """
    Extract files from the test directory and make a note instance for each
    Predict a label for each entry in the given notes
  """

  # Create notes
  if (v):
    sys.stdout.write("Begin testing\n\tCreating notes...\n")
  notes = note.makeNotes(t_dir, v)

  entries = list()
  for n in notes:
    entries += n.data

  # Load model
  if (v):
    sys.stdout.write("\tLoading model from %s...\n" % model_path)
  model = ml.Model()
  model.load(model_path)

  # Predict Labels
  if (v):
    sys.stdout.write("\tPredicting labels...\n")
  labels = model.predict(entries)

  for e, label in zip(entries, labels):
    e.relation.label = label

  # Write labels to files
  if (v):
    sys.stdout.write("\tWriting relation files in %s directory...\n" % res_dir)
  for n in notes:
    n.write(res_dir)

if __name__ == "__main__":
  main(abs_path('./i2b2_examples/'), 
       abs_path('../model/example.mod'), 
       abs_path('../results/'), True)
