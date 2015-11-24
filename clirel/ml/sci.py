# CliRel: sci.py
#	sci-kit learn interface for training and predicting on classifiers
#
# Connor Cooper

from sklearn.svm import LinearSVC
from sklearn.feature_extraction import DictVectorizer

def train(featDicts, Y):
	'''
	sci.train():
		train an SVM classifier based on a list of dictionary representations of features and a list of labels
	'''
	#vectorize feature dictionaries
	vec = DictVectorizer()
	X = vec.fit_transform(featDicts).toarray()

	assert len(X) == len(Y)

	#train classifier
	clf = LinearSVC()
	clf.fit(X, Y)

	return clf, vec

def predict(clf, vec, featDicts):
	'''
	sci.predict():
		use given classifier and vectorizer to obtain labels for given list of feature dictionaries
	'''


	#vectorize feature dictionaries
	X = vec.transform(featDicts)

	return list(clf.predict(X))