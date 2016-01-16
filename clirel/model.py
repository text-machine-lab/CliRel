"""                                                                              
 Text-Machine Lab: CliRel  

 File Name : model.py
                                                                              
 Creation Date : 12-01-2016
                                                                              
 Created By : Connor Cooper
              Renan Campos
                                                                              
 Purpose : Model object for predicting relations

"""

import ml.sci as sci

from features.features import featureDict

class Model:

  def train(self, notes):
    '''
    Model:train()
        train a model for predicting relations between concepts 
        based on given training data

        The notes will be split into three groups (problem-problem,
        treatment-problem, test-problem), and a classifier will be trained
        for each type. 

    @param notes: a list of notes with relation annotation data 
                  to train the model with
    '''

    # Dictionaries with the keys being the concept pair type. 
    featDicts = list()
    labels    = list()

    # extract features and get labels for each note
    for note in notes:
      for entry in note.data:
        featDicts.append(getFeatureDict(entry))
        labels.append(getRelationLabel(entry))

    # train classifier and vectorizer
    clf, vec = sci.train(featDicts, labels)

    # memoize classifier and vectorizer
    self.clf = clf
    self.vec = vec

  def predict(self, notes):

    # extract features
    for note in notes:
      for entry in note.data:
        featDict = getFeatureDict(entry)

        entry.relation.label = sci.predict(self.clf, self.vec, featDict)[0]

def getFeatureDict(entry):
  """
    Calls the feature functions to process the entry,
    Returns a dictionary of features
  """
  features = dict()

  for feature in featureDict:
    features[feature] = featureDict[feature](entry)
  return features
    

def getRelationLabel(entry):
  """
    Returns the entry's relation label
  """
  return entry.relation.label
