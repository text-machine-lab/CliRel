"""                                                                              
 Text-Machine Lab: CliRel  

 File Name :                                                                  
                                                                              
 Creation Date : 14-01-2016
                                                                              
 Created By : Renan Campos                                               
                                                                              
 Purpose : File utility functions used by clirel.py

"""

# Import os to check directory
import os

# Import sys to write to stderr
import sys

# The text, concepts and relations are subdirs listed as:
# txt, con, rel.
# TODO glob instead of directory assumption.

def checkFile(t_file):
  
  if not os.path.isfile(t_file):
    sys.stderr.write("ERROR: %s is not a valid file.\n" % t_file)
    sys.exit(1)

def checkDir(t_dir):
  
  if not os.path.isdir(t_dir):
    sys.stderr.write("ERROR: %s is not a valid directory.\n" % t_dir)
    sys.exit(1)

def filter_files(dir, extension):
  """ Only list files with the specified extension """
  files = list()
  for file in os.listdir(dir):
    if file.endswith(extension):
      files.append(os.path.join(dir, file))

  files.sort()

  return files

def extract_files(t_dir, train=False):
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
  checkDir(txt_path)
  checkDir(con_path) 
  if train: checkDir(rel_path)

  # This creates a list of files that will be used.
  dirs = [filter_files(txt_path, "txt"), filter_files(con_path, "con")]

  if (len(dirs[0]) != len(dirs[1])):
    sys.stderr.write("ERROR: Number of text and concept files do not match.\n")
    sys.exit(1)

  if train:
    dirs.append(filter_files(rel_path, "rel"))
    if (len(dirs[0]) != len(dirs[2])):
      sys.stderr.write("ERROR: Number of text and relation files do not match.\n")
      sys.exit(1)

  # Zip iterates through multiple objects at the same time, returning tuples
  # This function assumes there are matches for all files and all dirs have the
  # same number of files.
  return zip(*dirs)
