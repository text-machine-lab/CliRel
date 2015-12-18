# CliRel: model.py
#    model object for predicting relations
#
# Connor Cooper

import ml.sci as sci
from features.features import getFeatureDict

class Model:

    def train(self, notes):
        '''
        Model:train()
            train a model for predicting relations between concepts based on given training data

        @param notes: a list of notes with relation annotation data to train the model with
        '''

        featVectors = []
        labels = []

        # extract features and get labels for each note
        for note in notes:
            featVectors = featVectors + getFeatureDict(note)
            labels = labels + note.getRelationLabels()

        # train classifier and vectorizer
        clf, vec = sci.train(featVectors, labels)

        # memoize classifier and vectorizer
        self.clf = clf
        self.vec = vec

    def predict(self, note):

        # extract features
        featDicts = getFeatureDict(note)

        featVecs = vec.transform(featDicts)
        labels = clf.predict(featVecs)

        return labels

if __name__ == "__main__":
    print "nothing to do"

