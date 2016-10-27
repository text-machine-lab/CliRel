""" 
 Text-Machine Lab: CliRel

 File Name : bParser.py

 Creation Date : 11-10-2016

 Created By : Renan Campos

 Purpose : Gives parse trees. To save computation and time resources, the 
           data is assumed to have already been parsed with the parsing script,
           and saved to a specified location. This script will extract the 
           parses from that file.

"""

import os
from pandas import DataFrame

def extractPars(parFile):
  """
    Takes a parse file and returns a panda datatable.
    >>> print extractPars('../i2b2_examples/parse/health.parse').ix[0]
    lineNum                                                     1
    parse       (S (NP (DT This) (NN treatment)) (VP (VBZ impr...
    fileName                                               health
    Name: 0, dtype: object
    >>> print extractPars('../i2b2_examples/parse/health.parse').ix[1]
    lineNum                                                     2
    parse       (S (NP (NNP Treatment)) (VP (VBZ worsens) (NP ...
    fileName                                               health
    Name: 1, dtype: object
  """
  data = list()

  with open(parFile, 'r') as f:
    for i, line in enumerate(f):
      data.append((i+1, line.strip()[2:-2]))
  
  out = DataFrame(data, columns = ["lineNum", 
                                   "parse"])
  out['fileName'] = os.path.basename(parFile).split(".")[0]
  return out

if __name__ == '__main__':
  import doctest
  doctest.testmod()
