"""                                                                              
 Text-Machine Lab: CliRel  

 File Name : clirel.py
                                                                              
 Creation Date : 12-01-2016
                                                                              
 Created By : Renan Campos                                              
                                                                              
 Purpose : Clinical Relation Extraction main interface

"""

import os
import sys
import argparse

import train
import predict
import evaluate

from futilities import checkDir, checkFile

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
  parser.add_argument("--predict", nargs=3,
                      metavar=("test_dir", "model_file", "results_dir"), type=str,
                      help="Directory contains concept and text files \
                            that the specified (or default) model will predict. \
                            Resulting relation files will be written to \
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

  if not args.predict and not args.train and not args.evaluate:
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

    train.main(args.train[0], args.train[1], args.verbose)

  if args.predict:
    checkDir(args.predict[0])
    checkFile(args.predict[1])
    checkDir(args.predict[2])
    predict.main(args.predict[0], args.predict[1], args.predict[2], args.verbose)

  if args.evaluate:
    checkDir(args.evaluate[0])
    checkDir(args.evaluate[1])
    checkDir(os.path.dirname(args.evaluate[2]))
    if (os.path.isdir(args.evaluate[2])):
      sys.stderr.write("ERROR: eval_file expected to be a file, %s is a \
      directory\n" % args.evaluate[2])
      sys.exit(1)

    evaluate.main(args.evaluate[0], args.evaluate[1], args.evaluate[2], args.verbose)

if __name__ == '__main__':
  main()
