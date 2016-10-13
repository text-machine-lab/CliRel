""" 
 Text-Machine Lab: CliRel

 File Name :

 Creation Date : 12-10-2016

 Created By : Renan Campos

 Purpose : Module to produce tree enrichments.
           Here a tree is represented as a string consisting 
           of tokens and paranthesis.

"""

import re
tree_ex = re.compile(r"([^\(\) ]+)")

def createTree(s):
  """
    Takes a string and creates a list representation
    >>> createTree(test1)
    '(S (NP (DT This)) (VP (VBZ is) (NP (DT a) (NN test) (NN sentence))) (. .))'
  """
  t = ','.join(re.sub(tree_ex, r'"\1"', s).split())
  # Make lists not tuples
  return eval(t.replace('(', '[').replace(')',']'))

def getLeaves(tree):
  """
    Returns a string of the leaves of this particular branch.
    >>> getLeaves(test1)
    'This is a test sentence'
    >>> getLeaves(test2)
    'Sentences can also have ()'
    >>> getLeaves(test3)
    'medical problem reveals medical problem'
  """
  return None

def spt(tree, a, b):
  """
    Finds the shortest path tree between tokens a and b.
  """
  return None

if __name__ == '__main__':
  test1 = '(S (NP (DT This)) (VP (VBZ is) (NP (DT a) (NN test) (NN sentence))) (. .))'
  import doctest
  doctest.testmod()
