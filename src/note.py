""" 
 Text-Machine Lab: CliRel

 File Name : note.py

 Creation Date : 30-09-2016

 Created By : Renan Campos

 Purpose :  Internal data representation for a document set.
            Each entry consists of a concept pair, a sentence, and a relation
            label. The entries are indexed by filename and line number.
"""

import re
from pandas import DataFrame, Series

def extractConsFromText(line):
  """
    Takes a line in i2b2 concept syntax and returns the data.

    >>> extractConsFromText('c="This treatment" 1:0 1:1||t="treatment"')
    (1, 0, 1, 'treatment', 'This treatment')
    >>> extractConsFromText('c="medical problem" 1:3 1:4||t="problem"')
    (1, 3, 4, 'problem', 'medical problem')
    >>> extractConsFromText('c="Treatment" 2:0 2:0||t="treatment"')
    (2, 0, 0, 'treatment', 'Treatment')
  """
  
  m = re.match(r"c=\"(.*)\" (\d+):(\d+) \d+:(\d+)\|\|t=\"(.*)\"", line)
  return (int(m.group(2)), 
          int(m.group(3)), 
          int(m.group(4)), m.group(5), m.group(1))

def extractCons(consFile):
  """
    Takes a concept file and returns a panda datatable.
    Where every entry is a pair of concepts.

    >>> print extractCons('./i2b2_examples/concept/health.con').ix[0]
    lineNum                                       1
    conStart1                                     0
    conEnd1                                       1
    conType1                              treatment
    conText1                         This treatment
    conStart2                                     3
    conEnd2                                       4
    conType2                                problem
    conText2                        medical problem
    fileName     ./i2b2_examples/concept/health.con
    Name: 0, dtype: object
    >>> print extractCons('./i2b2_examples/concept/health.con').ix[1]
    lineNum                                       2
    conStart1                                     0
    conEnd1                                       0
    conType1                              treatment
    conText1                              Treatment
    conStart2                                     2
    conEnd2                                       3
    conType2                                problem
    conText2                        medical problem
    fileName     ./i2b2_examples/concept/health.con
    Name: 1, dtype: object
  """
  data = list()

  with open(consFile, 'r') as f:
    for line in f:
      data.append(extractConsFromText(line))
  
  out = list()
  for i,d1 in enumerate(data):
    for d2 in data[i+1:]:
      if d1[0] == d2[0]:
        out.append(d1 + d2[1:])
  out = DataFrame(out, columns = ["lineNum", 
                                    "conStart1",
                                    "conEnd1",
                                    "conType1",
                                    "conText1",
                                    "conStart2",
                                    "conEnd2",
                                    "conType2",
                                    "conText2"])
  out['fileName'] = consFile
  return out

def extractRelFromText(line):
  """
    Takes a line in i2b2 relation syntax and returns the data.

    >>> extractRelFromText('c="This treatment" 1:0 1:1||r="TrIP"||c="medical problem" 1:3 1:4')
    (1, 0, 1, 'This treatment', 3, 4, 'medical problem', 'TrIP')
    >>> extractRelFromText('c="Treatment" 2:0 2:0||r="TrWP"||c="medical problem" 2:2 2:3')
    (2, 0, 0, 'Treatment', 2, 3, 'medical problem', 'TrWP')
    >>> extractRelFromText('c="Treatment" 3:0 3:0||r="TrCP"||c="medical problem" 3:2 3:3')
    (3, 0, 0, 'Treatment', 2, 3, 'medical problem', 'TrCP')
  """
  m = re.match(r"c=\"(.*)\" (\d+):(\d+) \d+:(\d+)\|\|r=\"(.*)\"\|\|c=\"(.*)\" \d+:(\d+) \d+:(\d+)", line)
  return (int(m.group(2)),
          int(m.group(3)),
          int(m.group(4)),
          m.group(1),
          int(m.group(7)),
          int(m.group(8)),
          m.group(6),
          m.group(5))
  
def extractRels(relFile):
  """
    Takes a relation file and returns a panda datatable.

    >>> print extractRels('./i2b2_examples/rel/health.rel').ix[0]
    lineNum                                   1
    conStart1                                 0
    conEnd1                                   1
    conText1                     This treatment
    conStart2                                 3
    conEnd2                                   4
    conText2                    medical problem
    relType                                TrIP
    fileName     ./i2b2_examples/rel/health.rel
    Name: 0, dtype: object
    >>> print extractRels('./i2b2_examples/rel/health.rel').ix[1]
    lineNum                                   2
    conStart1                                 0
    conEnd1                                   0
    conText1                          Treatment
    conStart2                                 2
    conEnd2                                   3
    conText2                    medical problem
    relType                                TrWP
    fileName     ./i2b2_examples/rel/health.rel
    Name: 1, dtype: object
  """
  data = list()

  with open(relFile, 'r') as f:
    for line in f:
      data.append(extractRelFromText(line))
  
  out = DataFrame(data, columns = ["lineNum", 
                                   "conStart1",
                                   "conEnd1",
                                   "conText1",
                                   "conStart2",
                                   "conEnd2",
                                   "conText2",
                                   "relType"])
  out['fileName'] = relFile
  return out

def extractTxts(txtFile):
  """
    Takes a relation file and returns a panda datatable.

    >>> print extractTxts('./i2b2_examples/txt/health.txt').ix[0]
    lineNum                                             0
    text        This treatment improves medical problem .
    fileName               ./i2b2_examples/txt/health.txt
    Name: 0, dtype: object
    >>> print extractTxts('./i2b2_examples/txt/health.txt').ix[1]
    lineNum                                       1
    text        Treatment worsens medical problem .
    fileName         ./i2b2_examples/txt/health.txt
    Name: 1, dtype: object
  """
  data = list()

  with open(txtFile, 'r') as f:
    for i, line in enumerate(f):
      data.append((i, line.strip()))
  
  out = DataFrame(data, columns = ["lineNum", 
                                   "text"])
  out['fileName'] = txtFile
  return out

def createTraining(cFile, tFile, rFile):
  """
    Given the concepts, text and relation files, consilidate that
    data into a single dataframe.

    >>> print createTraining('./i2b2_examples/concept/health.con', './i2b2_examples/txt/health.txt', './i2b2_examples/rel/health.rel').ix[0]
    conEnd1                                              1
    conEnd2                                              4
    conStart1                                            0
    conStart2                                            3
    conText1                                This treatment
    conText2                               medical problem
    conType1                                     treatment
    conType2                                       problem
    fileName            ./i2b2_examples/concept/health.con
    lineNum                                              1
    relType                                           TrIP
    text         This treatment improves medical problem .
    Name: 0, dtype: object
    >>> print createTraining('./i2b2_examples/concept/health.con', './i2b2_examples/txt/health.txt', './i2b2_examples/rel/health.rel').ix[1]
    conEnd1                                        0
    conEnd2                                        3
    conStart1                                      0
    conStart2                                      2
    conText1                               Treatment
    conText2                         medical problem
    conType1                               treatment
    conType2                                 problem
    fileName      ./i2b2_examples/concept/health.con
    lineNum                                        2
    relType                                     TrWP
    text         Treatment worsens medical problem .
    Name: 1, dtype: object

  """
  concepts  = extractCons(cFile)
  text      = extractTxts(tFile)
  relations = extractRels(rFile)
  return concepts.combine_first(relations).combine_first(text)

if __name__ == "__main__":
  import doctest
  doctest.testmod()
  data = createTraining('./i2b2_examples/concept/health.con', './i2b2_examples/txt/health.txt', './i2b2_examples/rel/health.rel')

  def printData(x):
    print x
    raw_input("")
  
  import numpy as np
  import pandas as pd

  def genNeg(x):
    if not pd.isnull(x.relType):
      return x.relType

    return 'Banana'


  data['relType'] = data.apply(genNeg, axis=1)
  data.apply(printData, axis=1)


