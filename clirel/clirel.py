"""                                                                              
 Copyright Renan Campos 2015                                                  
                                                                              
 File Name : clirel.py
                                                                              
 Creation Date : 29-12-2015
                                                                              
 Last Modified : Tue 05 Jan 2016 05:28:34 PM EST
                                                                              
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

# The text, concepts and relations are subdirs listed as:
# txt, con, rel.
#DATA_DIR = "/data1/nlp-data/cliner_data/train_partners/"
DATA_DIR = "../data/" 

def check_dir(t_dir):
  """ Redundant function, just wrote for memory"""
  if not os.path.isdir(t_dir):
    sys.stderr.write("(ERROR): %s is not a valid directory\n" % t_dir)
    return False
  return True

def filter_files(dir, extension):
  """ Only list files with the specified extension """
  files = list()
  for file in os.listdir(dir):
    if file.endswith(extension):
      files.append(os.path.join(dir, file))

  files.sort()

  return files

def extract_files(t_dir, test=None):
  """ 
    Returns a list of tuples (text_file, concept_file, relation_file) in
    from the txt, concept, rel of the training directory
    Expects matching text and concept file, but relation file is not necassary
    (wouldn't be included in testing)
  """

  txt_path = os.path.join(t_dir, "txt") 
  con_path = os.path.join(t_dir, "concept") 
  rel_path = os.path.join(t_dir, "rel") 

  # If the main, txt or con don't exist. Or if it is not a test and rel doesn't
  if not check_dir(t_dir)    \
  or not check_dir(txt_path) \
  or not check_dir(con_path) \
  or not test and not check_dir(rel_path):
    return None

  # This creates a list of files that will be used.
  dirs = [filter_files(txt_path, "txt"), filter_files(con_path, "con")]

  if (len(dirs[0]) != len(dirs[1])):
    sys.stderr.write("ERROR: Number of text and concept files do not match.\n")
    sys.exit(1)

  if not test:
    dirs.append(filter_files(rel_path, "rel"))
    if (len(dirs[0]) != len(dirs[2])):
      sys.stderr.write("ERROR: Number of text and relation files do not match.\n")
      sys.exit(1)

  # Zip iterates through multiple objects at the same time, returning tuples
  # This function assumes there are matches for all files and all dirs have the
  # same number of files.
  return zip(*dirs)

def train(t_dir, model_path, v):
  """
     Extract files from the training directory and make a note instance for each
     Train a model the given notes. 
  """
  
  notes = list()

  if (v):
    sys.stdout.write("Extracting files from %s\n" % t_dir)

  files = extract_files(t_dir)

  if (files == None):
    sys.stderr.write("Error parsing files\n")
    sys.exit(1)

  for file in files:
    notes.append(Note(*file))

  if (v):
    sys.stdout.write("%d notes created\n" % len(notes))


  model = Model()
  model.train(notes)

  with open(model_path, "wb") as mod_file:
    cPickle.dump(model, mod_file)


def main():

  parser = argparse.ArgumentParser(description="CliRel (Clinical Relation) \
                                    extractor- trains a classifier able to \
                                    determine the type of relation between \
                                    two medical concepts in a sentence.")

  # Add arguments here
  parser.add_argument("--train_dir", type=str,
                      help="Directory should contain three subdirs (txt, \
                      concept, rel) containing .txt, .con, .rel files. \
                      Will train a classifier on this data.",
                      default=None)
  parser.add_argument("--test_dir", type=str,
                      help="Directory contains concept and text files \
                      that the specified (or default) model will test on.",
                      default=None)
  parser.add_argument("--model", type=str,
                      help="Specify the path to the model that will either \
                      trained, or will be used to classify the test set. \
                      Default model = model/clirel.model",
                      default="model/clirel.model")
  parser.add_argument("--verbose", action="store_true",
                      default=False, help="Show debugging info.")

  # Begin error-checking command args
  args = parser.parse_args()

  if args.train_dir:
    train(args.train_dir, args.model, args.verbose)

  if args.test_dir:
    if not os.path.isfile(args.model):
      sys.stderr.write("ERROR: No valid model specified\n")
      sys.exit(1)

  if not args.train_dir and not args.test_dir:
    sys.stderr.write("ERROR: No training dir or test dir specified\n")
    parser.print_help()
    sys.exit(1)
    
    
if __name__ == '__main__':
  main()
