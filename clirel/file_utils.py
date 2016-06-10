"""                                                                              
 Text-Machine Lab: CliRel  

 File Name : file_utils.py
                                                                              
 Creation Date : 14-01-2016
                                                                              
 Created By : Renan Campos                                               
                                                                              
 Purpose : File utility functions used by clirel.py

"""

# Import os to check directory
import os

# Import sys to write to stderr
import sys

# To create a new process
import subprocess

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
  par_path = os.path.join(t_dir, "parse")

  # If the main, txt or con don't exist. Or if it is not a test and rel doesn't
  checkDir(txt_path)
  checkDir(con_path) 
  if train: checkDir(rel_path)

  # This creates a list of files that will be used.
  dirs = [filter_files(txt_path, "txt"), filter_files(con_path, "con")]

  if (len(dirs[0]) != len(dirs[1])):
    sys.stderr.write("ERROR: Number of text and concept files do not match.\n")
    sys.exit(1)
  
  # Create parse files if they don't exist already
  dirs.append(filter_files(par_path, "pt"))
  parse = [os.path.basename(os.path.splitext(f)[0]) for f in dirs[2]]
  for t in dirs[0]:
    if os.path.basename(t) not in parse:
      subprocess.call(['../bin/parse_texts.sh',t])

  dirs[2] = filter_files(par_path, "pt")

  if train:
    dirs.append(filter_files(rel_path, "rel"))
    if (len(dirs[0]) != len(dirs[3])):
      sys.stderr.write("ERROR: Number of text and relation files do not match.\n")
      sys.exit(1)


  # Zip iterates through multiple objects at the same time, returning tuples
  # This function assumes there are matches for all files and all dirs have the
  # same number of files.
  return zip(*dirs)
