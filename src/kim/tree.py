""" 
 Text-Machine Lab: CliRel

 File Name : tree.py

 Creation Date : 12-10-2016

 Created By : Renan Campos

 Purpose : Module to produce tree enrichments.
           Here a tree is represented as a string consisting 
           of tokens and paranthesis.

"""

import re
tree_ex = re.compile(r"([^\(\) ]+)")

from copy import deepcopy

def createTree(s):
  """
    Takes a string and creates a list representation
    >>> createTree('()')
    []
    >>> createTree(test0)
    ['S', ['NP', ['DT', 'This']], ['VP', ['VBZ', 'is'], ['NP', ['DT', 'a'], ['NN', 'test'], ['NN', 'sentence']]], ['.', '.']]
  """
  if s == '':
    return []
  t = ','.join(re.sub(tree_ex, r'"\1"', s).split())
  # Make lists not tuples
  return eval(t.replace('(', '[').replace(')',']'))

def getLeaves(tree):
  """
    Returns a string of the leaves of this particular branch.
    >>> getLeaves([])
    ''
    >>> getLeaves(createTree(test0))
    'This is a test sentence .'
    >>> getLeaves(createTree(test6))
    'There were many symptoms , but test reveals medical problem .'
  """
  out = ''
 
  if len(tree) < 2:
    return out

  for child in tree[1:]:
    if type(child) == str:
      out += child 
    else:
      out += getLeaves(child)
    out += ' '
  
  return out[:-1]

def createString(tree):
  """
    Returns the tree as a string representation again.
    >>> createString(createTree('()'))
    '()'
    >>> createString(createTree(test0))
    '(S (NP (DT This)) (VP (VBZ is) (NP (DT a) (NN test) (NN sentence))) (. .))'
    >>> createString(createTree(test1))
    '(S (NP (DT This) (NN treatment)) (VP (VBZ improves) (NP (JJ medical) (NN problem))) (. .))'
    >>> createString(createTree(createString(createTree(test1))))
    '(S (NP (DT This) (NN treatment)) (VP (VBZ improves) (NP (JJ medical) (NN problem))) (. .))'
  """
  out = '('

  if len(tree) < 2:
    return out + ')'

  out += tree[0]
  for child in tree[1:]:
    if type(child) == str:
      out += ' ' + child
    else:
      out += ' ' + createString(child)

  return out + ')'
 
def spt(tree, conStart1, conEnd2, m=None, c=0):
  """
    Finds the smallest subtree that still contains the two token ranges.
    The challenge occurs when the two tokens are equal, or substrings of one another..
    >>> spt(createTree(test0), 1, 4)
    ['VP', ['VBZ', 'is'], ['NP', ['DT', 'a'], ['NN', 'test'], ['NN', 'sentence']]]
    >>> spt(createTree(test8), 0, 4)
    ['S', ['OO', ['JJ', 'medical'], ['NN', 'problem']], ['VP', ['VBD', 'indicated'], ['NP', ['NP', ['JJ', 'medical'], ['NN', 'problem']], [':', ';'], ['SBAR', ['WHNP', ['WDT', 'which']], ['S', ['VP', ['VBZ', 'is'], ['ADJP', ['RB', 'really'], ['JJ', 'important']]]]]]], ['.', '.']]
    >>> spt(createTree(test8), 0, 1)
    ['OO', ['JJ', 'medical'], ['NN', 'problem']]
    >>> spt(createTree(test8), 3, 4)
    ['NP', ['JJ', 'medical'], ['NN', 'problem']]
  """
  out = tree
  
  if m == None:
    # Create a mapping from tokens to id
    m = getLeaves(tree).split()
    # Determine number of times substring will occur before the correct subtree
    c1 = getLeaves(tree).count(' '.join(m[conStart1:conEnd2+1]))
    c2 = ' '.join(getLeaves(tree).split()[conStart1:]).count(' '.join(m[conStart1:conEnd2+1]))
    c = c1 - c2
  
  curr = c
  want_s = ' '.join(m[conStart1:conEnd2+1])

  for child in tree[1:]:
    if type(child) == str:
      continue

    if want_s in getLeaves(child):
      if curr == 0:
        return spt(child, conStart1, conEnd2, m, curr)
      out = spt(child, conStart1, conEnd2, m, c)
      curr -= 1

  return out

#TODO suffix and insert.
def insert(tree, conStart1, conEnd1, conType1,
                 conStart2, conEnd2, conType2):
  """
    Inserts a node in front of the subtree containing each concept type.
    >>> insert(createTree(test0), 1, 1, 'IS', 3, 4, 'TEST')
    ['VP', ['IS', ['VBZ', 'is']], ['TEST', ['NP', ['DT', 'a'], ['NN', 'test'], ['NN', 'sentence']]]]
    >>> insert(createTree(test8), 0, 1, 'PROBLEM', 3, 4, 'PROBLEM')
    ['S', ['PROBLEM', ['OO', ['JJ', 'medical'], ['NN', 'problem']]], ['VP', ['VBD', 'indicated'], ['NP', ['PROBLEM', ['NP', ['JJ', 'medical'], ['NN', 'problem']]], [':', ';'], ['SBAR', ['WHNP', ['WDT', 'which']], ['S', ['VP', ['VBZ', 'is'], ['ADJP', ['RB', 'really'], ['JJ', 'important']]]]]]], ['.', '.']]
  """
  out = spt(tree, conStart1, conEnd2)
  t1  = spt(tree, conStart1, conEnd1)
  t2  = spt(tree, conStart2, conEnd2)

  # Insertion
  t1.append(deepcopy(t1))
  del t1[:-1]
  t1.insert(0, conType1)

  t2.append(deepcopy(t2))
  del t2[:-1]
  t2.insert(0, conType2)

  return out

def suffix(tree, conStart1, conEnd1, conType1,
                 conStart2, conEnd2, conType2):
  """
    Suffixes the label in front of every node in the subtree.
    >>> suffix(createTree(test0), 1, 1, 'IS', 3, 4, 'TEST')
    ['VP', ['VBZ-IS', 'is'], ['NP-TEST', ['DT-TEST', 'a'], ['NN-TEST', 'test'], ['NN-TEST', 'sentence']]]
    >>> suffix(createTree(test8), 0, 1, 'PROBLEM', 3, 4, 'PROBLEM')
    ['S', ['OO-PROBLEM', ['JJ-PROBLEM', 'medical'], ['NN-PROBLEM', 'problem']], ['VP', ['VBD', 'indicated'], ['NP', ['NP-PROBLEM', ['JJ-PROBLEM', 'medical'], ['NN-PROBLEM', 'problem']], [':', ';'], ['SBAR', ['WHNP', ['WDT', 'which']], ['S', ['VP', ['VBZ', 'is'], ['ADJP', ['RB', 'really'], ['JJ', 'important']]]]]]], ['.', '.']]
  """
  out = spt(tree, conStart1, conEnd2)
  t1  = spt(tree, conStart1, conEnd1)
  t2  = spt(tree, conStart2, conEnd2)

  # Suffix
  _suffix(t1, conType1)
  _suffix(t2, conType2)
  
  return out

def _suffix(t, conType):
  """
    Helper for suffix, adds string to each label.
  """
  if len(t) == 0:
    return
  t[0] = t[0] + '-' + conType
  for child in t[1:]:
    if type(child) == list:
      _suffix(child, conType)
  return

if __name__ == '__main__':
  test0 = '(S (NP (DT This)) (VP (VBZ is) (NP (DT a) (NN test) (NN sentence))) (. .))'
  test1 = '(S (NP (DT This) (NN treatment)) (VP (VBZ improves) (NP (JJ medical) (NN problem))) (. .))'
  test2 = '(S (NP (NNP Treatment)) (VP (VBZ worsens) (NP (JJ medical) (NN problem))) (. .))'
  test3 = '(S (NP (NNP Treatment)) (VP (VBZ causes) (NP (JJ medical) (NN problem))) (. .))'
  test4 = '(S (NP (DT The) (NN treatment)) (VP (VBZ is) (VP (VBN administered) (PP (IN for) (NP (JJ medical) (NN problem))))) (. .))'
  test5 = '(S (NP (NNP Treatment)) (VP (VBZ is) (RB not) (VP (VBN administered) (PP (IN because) (IN of) (NP (JJ medical) (NN problem))))) (. .))'
  test6 = '(S (S (NP (EX There)) (VP (VBD were) (NP (JJ many) (NNS symptoms)))) (, ,) (CC but) (S (NP (NN test)) (VP (VBZ reveals) (NP (JJ medical) (NN problem)))) (. .))'
  test7 = '(S (NP (DT The) (JJ great) (NNS tests)) (VP (VBD conducted) (S (VP (TO to) (VP (VB investigate) (NP (JJ medical) (NN problem)))))) (. .))'
  test8 = '(S (OO (JJ medical) (NN problem)) (VP (VBD indicated) (NP (NP (JJ medical) (NN problem)) (: ;) (SBAR (WHNP (WDT which)) (S (VP (VBZ is) (ADJP (RB really) (JJ important))))))) (. .))'
  test9 = '(NP (NP (NP (DT The) (JJ great) (NNS tests)) (VP (VBD conducted) (S (VP (TO to) (VP (VB investigate) (NP (JJ medical) (NN problem)))))) (. .)) (NNP VOID))'
  test10 = '(FRAG (NP (JJ Medical) (NN problem) (VBN indicated) (JJ medical) (NN problem)) (: ;) (SBAR (WHNP (WDT which)) (S (VP (VBZ is) (ADJP (RB really) (JJ important))))) (. .) (NP (NNP VOID)))'
  test11 = '(S (NP (DT This) (NN treatment)) (VP (VBZ improves) (NP (JJ medical) (NN problem) (. .) (NNP VOID))))'
  import doctest
  doctest.testmod()

