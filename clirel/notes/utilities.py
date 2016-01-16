"""                                                                              
 Text-Machine Lab: CliRel  

 File Name :                                                                  
                                                                              
 Creation Date : 12-01-2016
                                                                              
 Created By : Connor Cooper                                              
                                                                              
 Purpose : Various utilitiy functions for data manipulation adn formatting

"""

def getValidPairs(concepts):
	'''
	getValidPairs()
		Identify all pairs of concepts which can be mapped to a valid relation type

	@param concepts: a list of concepts to generate pairs for
	@return: a list of tuples containing valid pairs of concepts
	'''

	pairs = []

	for con1 in concepts:
		for con2 in concepts:
			if con1 == con2: # skip duplicate concepts
				continue
			if con1[1] == con2[1]: # if concepts are in the same sentence
				if con2[0] == "problem":
					pairs.append((con1, con2))

	return pairs

def getPairLabels(pairs, relations):
	'''
	getPairLabels()
		Label all given pairs based on given relation data. If no relation exists for given pair, label 'O'

	@param pairs: a list of 2 tuples of 4 tuple concept representations of form
					<label, lineNo, span start, span end>
	@param relations: a list of relations of form 
					<label, lineNo, first span start, first span end, second span start, second span end>
	@return: a list of labels with one to one corresponence with given list of pairs
	'''

	# TODO: support cross-sentence relations

	labels = []

	for pair in pairs:
		con1 = pair[0]
		con2 = pair[1]

		matchFound = False

		for relation in relations:
			if matchFound: break # if pair already labeled, break loop through relations

			if relation[1] == con1[1]: # if line numbers are the same

				sameFirstStart = False
				sameFirstEnd = False
				sameSecondStart = False
				sameSecondEnd = False

				if relation[2] == con1[2]: sameFirstStart = True
				if relation[3] == con1[3]: sameFirstEnd = True
				if relation[4] == con2[2]: sameSecondStart = True
				if relation[5] == con2[3]: sameSecondEnd = True

				if sameFirstStart and sameFirstEnd and sameSecondStart and sameSecondEnd:
					labels.append(relation[0]) # append relation labels
					matchFound = True

		if matchFound: matchFound = False 
		else: # if relation label was not found, label with 'O'
			labels.append('O')

	assert len(labels) == len(pairs)
	return labels

