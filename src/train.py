""" 
 Text-Machine Lab: CliRel

 File Name : train.py

 Creation Date : 15-06-2016

 Created By : Renan Campos

 Purpose : Training Script.

"""

import sys
import numpy as np

import note
import svm as ml
from futilities import abs_path

def main(t_dir, model_path, v):
  """
     Extract files from the training directory and make a note instance for each
     Train a model the given notes. 
  """
 
  # Create notes
  if (v):
    sys.stdout.write("Begin Training\n\tCreating notes...\n")
  notes = note.makeNotes(t_dir, v, True)
  
  entries = list()
  for n in notes:
    entries += n.data    
  labels  = [e.relation.label for e in entries]
  
  if (v):
    print "\t%d entries read" % len(entries)

  # Create Model
  if (v):
    sys.stdout.write("\tCreating model...\n")
  model = ml.Model()
  model.train(entries, labels)

  # Save model for later use
  if (v):
    sys.stdout.write("\tPickling model to %s...\n" % model_path)
  model.save(model_path)

if __name__ == "__main__":
  main(abs_path('./i2b2_examples/'), abs_path('../model/example.mod'), True)
