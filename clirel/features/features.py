"""                                                                              
 Text-Machine Lab: CliRel  

 File Name : features.py
                                                                              
 Creation Date : 12-01-2016
                                                                              
 Created By : Connor Cooper
              Renan Campos
                                                                              
 Purpose : Compute features to be used in training and predicting

"""

# POS tagging
from nltk.tag import pos_tag


def getConceptPair(entry):
  """
    Extract features for the given sentence and the concept pairs.
  """
  return hash(entry.getConcepts())

featureDict = { "pairs": getConceptPair }

