"""                                                                              
 Text-Machine Lab: CliRel  

 File Name : clirel.py
                                                                              
 Creation Date : 12-01-2016
                                                                              
 Created By : Renan Campos                                              
                                                                              
 Purpose : Trains/Tests a classifier on given data to identify Clinical
           relations.

"""

# Import os to check directory
import os

# Import sys to write to stderr
import sys

import argparse
import cPickle

from notes.note import Note
from model import Model

from file_utils import extract_files, checkDir, checkFile
from evaluate import evaluate

def main():

  parser = argparse.ArgumentParser(description="CliRel (Clinical Relation) \
                                    extractor- trains a classifier able to \
                                    determine the type of relation between \
                                    two medical concepts in a sentence.")

  # Add arguments here
  parser.add_argument("--train", nargs=2, 
                      metavar=("train_dir", "model_file"), type=str, 
                      help="Directory should contain three subdirs (txt, \
                            concept, rel) containing .txt, .con, .rel files. \
                            Will train a classifier on this data. \
                            Trained model will be written to specified model file.",
                      default=None)
  parser.add_argument("--test", nargs=3, 
                      metavar=("test_dir", "model_file", "results_dir"), type=str,
                      help="Directory contains concept and text files \
                            that the specified (or default) model will test \
                            on. Resulting relation files will be written to \
                            the specified results directory.",
                      default=None)
  parser.add_argument("--evaluate", nargs=3,
                      metavar=("test_dir", "gold_dir", "eval_file"), type=str,
                      help="Evaluate the relation files in the test directory \
                      in comparison with those in the gold directory. The \
                      results will be written to the evaluation file.", 
                      default=None)
  parser.add_argument("--verbose", action="store_true",
                      default=False, help="Show debugging info.")
  
  args = parser.parse_args()

  if not args.test and not args.train and not args.evaluate:
    sys.stderr.write("ERROR: No valid flag specified.\n")
    parser.print_help()
    sys.exit(1)

  if args.train:
    checkDir(args.train[0])
    checkDir(os.path.dirname(args.train[1]))
    if (os.path.isdir(args.train[1])):
      sys.stderr.write("ERROR: Model expected to be a file, %s is a directory\n"
                 % args.train[1])
      sys.exit(1)

    train(args.train[0], args.train[1], args.verbose)

  if args.test:
    checkDir(args.test[0])
    checkFile(args.test[1])
    checkDir(args.test[2])
    test(args.test[0], args.test[1], args.test[2], args.verbose)

  if args.evaluate:
    checkDir(args.evaluate[0])
    checkDir(args.evaluate[1])
    checkDir(os.path.dirname(args.evaluate[2]))
    if (os.path.isdir(args.evaluate[2])):
      sys.stderr.write("ERROR: eval_file expected to be a file, %s is a \
      directory\n" % args.evaluate[2])
      sys.exit(1)

    evaluate(args.evaluate[0], args.evaluate[1], args.evaluate[2], args.verbose)

def train(t_dir, model_path, v):
  """
     Extract files from the training directory and make a note instance for each
     Train a model the given notes. 
  """
 
  # Create notes
  if (v):
    sys.stdout.write("Begin Training\n\tCreating notes...\n")
  notes = makeNotes(t_dir, v, True)

  # Create Model
  if (v):
    sys.stdout.write("\tCreating model...\n")
  model = Model()
  model.train(notes)

  # Pickle model for later use
  if (v):
    sys.stdout.write("\tPickling model to %s...\n" % model_path)
  with open(model_path, "wb") as mod_file:
    cPickle.dump(model, mod_file)

def test(t_dir, model_path, res_dir, v):
  """
    Extract files from the test directory and make a note instance for each
    Predict a label for each entry in the given notes
  """

  # Create notes
  if (v):
    sys.stdout.write("Begin testing\n\tCreating notes...\n")
  notes = makeNotes(t_dir, v)

  # Load model
  if (v):
    sys.stdout.write("\tLoading model from %s...\n" % model_path)
  with open(model_path, "rb") as mod_file:
    model = cPickle.load(mod_file)
  
  if (v):
    sys.stdout.write("\tPredicting labels...\n")
  model.predict(notes)

  if (v):
    sys.stdout.write("\tWriting relation files in %s directory...\n" % res_dir)
  for note in notes:
    note.write(res_dir)

def makeNotes(dir, v, train=False):
  """
    Returns a list of notes
  """
  notes = list()

  if (v):
    sys.stdout.write("\t\tExtracting files from %s\n" % dir)

  files = extract_files(dir, train)

  if (files == None):
    sys.stderr.write("Error parsing files\n")
    sys.exit(1)

  for file in files:
    notes.append(Note(*file))

  if (v):
    sys.stdout.write("\t\t%d notes created\n" % len(notes))

  return notes


if __name__ == '__main__':
  main()
