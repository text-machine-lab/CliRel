import os.path

# CliRel: note.py:
#	Internal data representation for a single document set (single text file and single set of annotation files)
#
# Connor Cooper


class Note:

	def __init__(self):

		self.data		= [] # list of tokens
		self.concepts	= [] # list of concept tuples
		self.relations	= [] # list of relation tuples

		self.lineInds	= [] # list of line index tuples (start, end)

	def read(self, txt, con, rel = None):
		'''
		Note:read()
			Read in data from document set

		@param txt: file path for medical record
		@param con: file path for concept annotations for given txt file
		@param rel: file path for relations between concepts in given con file
		'''

		# break text by sentence or token
		sentenceBreak = lambda text: text.split('\n')
		tokenBreak = lambda text: text.split(' ')

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
				print self.data[-1]

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
				print self.concepts[-1]

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

					self.relations.append((relation, lineNo, firstStart, firstEnd, secondStart, secondEnd))
					print self.relations[-1]



	def write(self, labels=None):
		#TODO: write relation data into a string formatted using the i2b2 format

		i = 0