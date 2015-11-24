# CliRel: features.py
#	Compute features to be used in training and predicting
#
# Connor Cooper

from notes.utilities import getValidPairs

def getFeatureDict(note):
	'''
	getFeatureDict()
		Extract features for valid concept pairs in a given note. A concept pair is valid if it can map to 
		a relation class.

	@param note: a note object to get features from
	@return: a list of feature dictionaries; one for every valid concept pair
	'''

	feats = []

	conPairs = getValidPairs(note.concepts)

	for pair in conPairs:
		#TODO: extract actual featues
		featDict = {}
		featDict["dummy"] = 1
		feats.append(featDict)

	return feats