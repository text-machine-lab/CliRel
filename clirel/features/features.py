# CliRel: features.py
# Compute features to be used in training and predicting
#
# Connor Cooper
# Renan Campos

from nltk.tag import pos_tag


# Enumeration of concepts
CONCEPTS = { "problemproblem":0, 
             "treatmenttreatment":1,
             "testtest":2,
             "problemtreatment":3,
             "treatmentproblem":3,
             "problemtest":4,
             "testproblem":4,
             "treatmenttest":5,
             "testtreatment":5 } 

def get_features(pair, sentence):
  """
    Extract features for the given sentence and the concept pairs.
  """

  print pair, ' '.join(sentence)
  return {"pairs":CONCEPTS[pair[0][0]+pair[1][0]]}
  
