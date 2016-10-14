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
 
def spt(tree, a, b):
  """
    Finds the shortest path tree between tokens a and b.
    >>> spt(createTree(test0), 'is', 'sentence')
    ['VP', ['VBZ' 'is'], ['NP', ['DT', 'a'], ['NN', 'test'], ['NN', 'sentence']]]
  """

  return None

if __name__ == '__main__':
  test0 = '(S (NP (DT This)) (VP (VBZ is) (NP (DT a) (NN test) (NN sentence))) (. .))'
  test1 = '(S (NP (DT This) (NN treatment)) (VP (VBZ improves) (NP (JJ medical) (NN problem))) (. .))'
  test2 = '(S (NP (NNP Treatment)) (VP (VBZ worsens) (NP (JJ medical) (NN problem))) (. .))'
  test3 = '(S (NP (NNP Treatment)) (VP (VBZ causes) (NP (JJ medical) (NN problem))) (. .))'
  test4 = '(S (NP (DT The) (NN treatment)) (VP (VBZ is) (VP (VBN administered) (PP (IN for) (NP (JJ medical) (NN problem))))) (. .))'
  test5 = '(S (NP (NNP Treatment)) (VP (VBZ is) (RB not) (VP (VBN administered) (PP (IN because) (IN of) (NP (JJ medical) (NN problem))))) (. .))'
  test6 = '(S (S (NP (EX There)) (VP (VBD were) (NP (JJ many) (NNS symptoms)))) (, ,) (CC but) (S (NP (NN test)) (VP (VBZ reveals) (NP (JJ medical) (NN problem)))) (. .))'
  test7 = '(S (NP (DT The) (JJ great) (NNS tests)) (VP (VBD conducted) (S (VP (TO to) (VP (VB investigate) (NP (JJ medical) (NN problem)))))) (. .))'
  test8 = '(S (NP (JJ Medical) (NN problem)) (VP (VBD indicated) (NP (NP (JJ medical) (NN problem)) (: ;) (SBAR (WHNP (WDT which)) (S (VP (VBZ is) (ADJP (RB really) (JJ important))))))) (. .))'
  test9 = '(NP (NP (NP (DT The) (JJ great) (NNS tests)) (VP (VBD conducted) (S (VP (TO to) (VP (VB investigate) (NP (JJ medical) (NN problem)))))) (. .)) (NNP VOID))'
  test10 = '(FRAG (NP (JJ Medical) (NN problem) (VBN indicated) (JJ medical) (NN problem)) (: ;) (SBAR (WHNP (WDT which)) (S (VP (VBZ is) (ADJP (RB really) (JJ important))))) (. .) (NP (NNP VOID)))'
  test11 = '(S (NP (DT This) (NN treatment)) (VP (VBZ improves) (NP (JJ medical) (NN problem) (. .) (NNP VOID))))'
  import doctest
  doctest.testmod()
