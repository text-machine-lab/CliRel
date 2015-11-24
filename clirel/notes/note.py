# CliRel: note.py:
#	Internal data representation for a single document set (single text file and single set of annotation files)
#
# Connor Cooper

import os.path

from nltk import sent_tokenize, word_tokenize
from utilities import getValidPairs, getPairLabels

class Note:

	def __init__(self, txt, con, rel = None):

		self.data		= [] # list of tokens
		self.concepts	= [] # list of concept tuples
		self.relations	= [] # list of relation tuples

		self.lineInds	= [] # list of line index tuples (start, end)

		self.read(txt, con, rel)

	def read(self, txt, con, rel = None):
		'''
		Note:read()
			Read in data from document set

		@param txt: file path for medical record
		@param con: file path for concept annotations for given txt file
		@param rel: file path for relations between concepts in given con file
		'''

		# break text by sentence or token
		sentenceBreak = sent_tokenize
		tokenBreak = word_tokenize

		# read medical record
		with open(txt) as t:

			self.rawText = t.read()

			start = 0

			sentences = sentenceBreak(self.rawText)
			for sentence in sentences:

				# get starting indice of sentence
				start += self.rawText[start:].index(sentence)

				# get ending indice
				end = start + len(sentence)

				self.lineInds.append((start, end))

				self.data.append(tokenBreak(sentence))

		# read concept annotations
		with open(con) as c:

			for line in c:

				# skip empty lines
				if line == '\n':
					continue

				# concept information
				prefix, suffix = line.split('||')
				text = prefix.split()
				concept = suffix[3:-2]

				start = text[-2].split(':')
				end = text[-1].split(':')

				# line number concept occurs on
				lineNo = int(start[0])

				# start and end indices
				start = int(start[1])
				end = int(end[1])

				self.concepts.append((concept, lineNo, start, end))

		# read relation annotations if they were provided
		if rel:

			with open(rel) as r:

				#TODO: parse rel file
				for line in r:

					# skip empty lines
					if line == '\n':
						continue

					# relation information
					prefix, middle, suffix = line.split('||')
					firstText 	= prefix.split()
					secondText 	= suffix.split()
					relation 	= middle[3:-1]

					# start and end indices of concpets
					firstStart 	= int(firstText[-2].split(':')[1])
					firstEnd 	= int(firstText[-1].split(':')[1])

					secondStart	= int(secondText[-2].split(':')[1])
					secondEnd	= int(secondText[-1].split(':')[1])

					# extract line number
					lineNo = int(firstText[-2].split(':')[0])

					# TODO: ensure the offsets for concepts in a relation corespond to actual concept annotations
					# TODO: support cross-sentence relations
					self.relations.append((relation, lineNo, firstStart, firstEnd, secondStart, secondEnd))



	def write(self, labels=None):
		#TODO: write relation data into a string formatted using the i2b2 format

		pass

	def getRelationLabels(self):
		'''
		Note:getRelationLabels()
			return a list of labels with one to one correspondence to the list of valid pairs returned by getValidPairs()
		'''

		# must have some relation data from annotations
		assert self.relations != None

		# get list of pairs to obtain labels for 
		pairs = getValidPairs(self.concepts)

		labels = getPairLabels(pairs, self.relations)

		return labels

if __name__ == "__main__":
	print "nothing to do"

	# t = Note("pretend.txt", "pretend.con", "pretend.rel")

	# print t.data[0]
	# print t.data
	# print t.concepts
	# print t.relations