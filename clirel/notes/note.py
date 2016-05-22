"""                                                                              
 Text-Machine Lab: CliRel  

 File Name : note.py
                                                                              
 Creation Date : 15-01-2016
                                                                              
 Created By : Connor Cooper
              Renan Campos
                                                                              
 Purpose :  Internal data representation for a single document set 
            (single text file and single set of annotation files)
            A note is a set of entries and the base name of the file
            An Entry is a sentence and the potential relation in that sentence
            A Relation is an ordered pair of concepts and a label between them
            A Concept consists of the words it comprises, its label, line number
            and word indices
"""
import os.path

from nltk import sent_tokenize, word_tokenize
from utilities import getValidPairs, getPairLabels

Sentences = dict()

#TODO Add support for cross-sentence relations

class Concept:

  def __init__(self, concept=None, label=None, lineNo=None, start=None, end=None, string=None):

    if string:
      # concept information
      prefix, suffix = string.split('||')
      
      # Label without quotes
      self.label = suffix[3:-2]

      text  = prefix.split()

      start = text[-2].split(':')
      end   = text[-1].split(':')

      # Concept text without quotes
      self.concept = " ".join(text[:-2])[3:-1]

      # line number concept occurs on
      self.lineNo = int(start[0])

      # start and end indices
      self.start = int(start[1])
      self.end   = int(end[1])

    else:
      self.concept = concept
      self.label   = label
      self.lineNo  = lineNo
      self.start   = start
      self.end     = end
    

  def __repr__(self):
    return "c=\"%s\" %d:%d %d:%d||t=\"%s\"" % ( self.concept,
                                                self.lineNo,
                                                self.start,
                                                self.lineNo,
                                                self.end,
                                                self.label)

  def getSentence(self):
    return Sentence[self.lineNo]

class Relation:

  def __init__(self, con1=None, con2=None, string=None):
    if string:
      # relation information
      prefix, middle, suffix = string.split('||')

      firstText   = prefix.split()
      secondText  = suffix.split()
      relation    = middle[3:-1]

      # start and end indices of concpets
      firstconcept = " ".join(firstText[:-2])[3:-1]
      firstStart   = int(firstText[-2].split(':')[1])
      firstEnd     = int(firstText[-1].split(':')[1])

      secondconcept = " ".join(secondText[:-2])[3:-1]
      secondStart   = int(secondText[-2].split(':')[1])
      secondEnd     = int(secondText[-1].split(':')[1])

      # extract line number
      lineNo = int(firstText[-2].split(':')[0])

      self.label = relation
      self.con1  = Concept(firstconcept,  None, lineNo,  firstStart,  firstEnd)
      self.con2  = Concept(secondconcept, None, lineNo, secondStart, secondEnd)

    else:
      assert con1.lineNo == con2.lineNo
    
      self.label = None
      self.con1  = con1
      self.con2  = con2

  def __eq__(self, other):
    return self.__hash__() == other.__hash__()

  def __repr__(self):
    return "%s||r=\"%s\"||%s" % ( str(self.con1).split("||")[0],
                                  self.label,
                                  str(self.con2).split("||")[0])
    

  def __hash__(self):
    return hash("%d%d%d%d%d" % ( self.con1.lineNo,
                                 self.con1.start,
                                 self.con1.end,
                                 self.con2.start,
                                 self.con2.end ))

  def getConcepts(self):
    return self.con1, self.con2

  def getSentences(self):
    return self.con1.getSentence(), self.con2.getSentence()


class Entry:

  def __init__(self, relation):
    self.relation = relation

  def validateRelation(self, relations):
    try:
      self.relation.label = relations[self.relation]
    except:
      self.relation.label = 'O'

  def getConcepts(self):
    return self.relation.getConcepts()

  def getSentences(self):
    return self.relation.getSentences()


class Note:
  
  def __init__(self, txt, con, rel = None):

    self.docName = os.path.splitext(os.path.basename(txt))[0] 
    self.data = set() # A set of entries
    self.read(txt, con, rel)

  def read(self, txt, con, rel = None):
    '''
    Note:read()
      Read in data from document set

    @param txt: file path for medical record
    @param con: file path for concept annotations for given txt file
    @param rel: file path for relations between concepts in given con file
    '''


    # TODO: convert from line number used in annoation to the actual sentence number obtained by the sent_tokenizer.
    # break text by sentence or token
    sentenceBreak = lambda text: text.split('\n')
    tokenBreak = word_tokenize

    # read concept annotations
    with open(con) as c:
      concepts  = dict()

      for line in c:

        # skip empty lines
        if line == '\n':
          continue

        concept = Concept(string=line)

        try:
          concepts[concept.lineNo].add(concept)
        except KeyError:
          concepts[concept.lineNo] = set()
          concepts[concept.lineNo].add(concept)

    # read medical record
    # Only the sentences that contain concepts are needed for training/testing
    with open(txt) as t:
    
      for lineNo, sentence in enumerate(t):
        lineNo += 1 # Line number starts at 1, not 0
        try:
          for concept1 in concepts[lineNo]:
            for concept2 in concepts[lineNo]:
              if concept1 != concept2:
                self.data.add(Entry(Relation(con1=concept1, con2=concept2)))
                Sentences[concept1.lineNo] = sentence
        except KeyError:
          continue
              
    # read relation annotations if they were provided
    if rel:

      with open(rel) as r:
        
        relations = dict()

        for line in r:
          
          # skip empty lines
          if line == '\n':
            continue
          
          relation = Relation(string=line)

          relations[relation] = relation.label

      # Assign label to each entry that contains a valid relation
      for entry in self.data:
        entry.validateRelation(relations)


  def write(self, outDir):
    outPath = os.path.join(outDir, self.docName + ".rel")

    with open(outPath, 'w') as f:
      for entry in self.data:
        # Ommit unlabeled concept pairs
        if entry.relation.label != 'O':
          print >>f, entry.relation

