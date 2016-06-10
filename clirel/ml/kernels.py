""" 
 Text-Machine Lab: CliRel

 File Name : kernels.py

 Creation Date : 08-06-2016

 Created By : Renan Campos

 Purpose : This module defines a composite kernel consisting of an entity 
           kernel and a convolution tree kernel.
           based on 'Extracting Clinical Relations in Electronic Health Records
           Using Enriched Parse Trees' by (Jisung Kim, et al.)

"""

from math import e, sqrt

# Hyperparameters
BETA  = e
ALPHA = 0.5

#
# Helpers
#
def _getProduction(n):
  return [n[0], [t[0] for t in n[1:]]]

def _isPreTerminal(p):
  return (type(p[1]) == str)

def _C(n1, n2, l = 0):
  p1 = _getProduction(n1); p2 = _getProduction(n2)
  
  if p1 != p2:
    return 0

  if _isPreTerminal(p1) and _isPreTerminal(p2):
    return 1
  
  total = 1
  for i in range(len(p1[1])):
    total *= (1 + _C(n1[i+1], n2[i+1], l+1))

  return BETA**-l * total 

#
# Kernels
#
def K_T(T1, T2):
  """
    Convolution Tree Kernel - computes the similarity between two given parse
    trees based on how similar the two trees are in terms of matches between
    their fragments (subtrees)
  """
  total = _C(T1,T2)

  if type(T1[1]) == str or type(T2[1]) == str:
    return total

  for n1 in T1[1:]:
    for n2 in T2[1:]:
      total += K_T(n1,n2)

  return total

def K_L(R1, R2):
  """
    Entity Kernel - Computes the similarity between two relations using features
    of the two entities in each relation.
  """
  c1a,c1b = R1.getConcepts(); c2a,c2b = R2.getConcepts()

  return ((c1a.label == c2a.label) + (c1b.label == c2b.label))

def K_C(E1, E2):
  """
    Linear combination of the normalized polinomial expansion of the entity 
    kernel and the normalized tree kernel.
  """
  R1 = E1.relation ;        R2 = E2.relation
  T1 = E1.getParses()[0] ; T2 = E2.getParses()[0]
  
  return (ALPHA *((1+K_L(R1,R2))**2/9.0) +\
       (1-ALPHA)*(K_T(T1,T2)/sqrt(K_T(T1,T1)*K_T(T2,T2))))
