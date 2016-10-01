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

import re
import sys
import os.path
from copy import deepcopy
from nltk import sent_tokenize, word_tokenize
from collections import defaultdict

from futilities import extract_files

_sentences = defaultdict(dict)

# Regular expression for adding quotes to parse tree string
tree_ex = re.compile(r"([^\(\) ]+)")
class ParseTree:
  def __init__(self, s_t):
    t = ','.join(re.sub(tree_ex, r'"\1"', s_t[2:-2]).split())
    # Make lists not tuples
    self.t = eval(t.replace('(', '[').replace(')',']'))

  def spt(self, *args):
    """
      Returns a tree trimmed into the shortest path between terminals a and b
      WARNING: ERROR occurs if a == b for a and b in args 
    """
    out = deepcopy(self)
    out.t = out._spt(out.t, *args)
    return out

  def insertion(self, entities, labels):
    """
      Returns enriched tree for with inserted label nodes for the specified entities.
    """
    out = deepcopy(self)
    for entity, label in zip(entities, labels):
      tree = out._spt(out.t, entity)
      copy = tree[:]
      while len(tree):
        tree.pop()
      tree.insert(0,copy)
      tree.insert(0,label)
    return out.spt(*entities)

  def suffix(self, entities, labels):
    """
      Returns enriched tree with suffixes
    """
    out = deepcopy(self)
    for entity, label in zip(entities, labels):
      t = out._spt(out.t, entity)
      out._suffix(t, label)
    return out.spt(*entities)

  def find(self, tree, words):
    for word in words:
      if not self._find(tree, word):
        return False
    return True

  def _spt(self,n,*args):
    p = self._getProduction(n)

    if self._isPreterminal(n):
      return n

    out = n
          
    for i in range(len(p[1])):
      flag = True
      for a in args:
        if not self.find(n[i+1], a.split()):
          flag = False
          break
      if flag:
        out = self._spt(n[i+1], *args)
                                                   
    return out
                                

  def _find(self, n, a):
    p = self._getProduction(n)

    if self._isPreterminal(n):
      return a == p[1]

    for i in range(len(p[1])):
      if self._find(n[i+1], a):
        return True

    return False
  
  def _suffix(self, n, label):
    p = self._getProduction(n)

    if self._isPreterminal(n):
      n[0] += '-' + label
      return n

    for i in range(len(p[1])):
      if type(n[i]) == str:
        n[i] += '-' + label
      self._suffix(n[i+1], label)

    return n

  def __str__(self):
    return '( ' + self._str(self.t) + ' )'

  def __repr__(self):
    return str(self)

  def _getProduction(self, n):
    if self._isPreterminal(n):
      return n
    return [n[0], [t[0] for t in n[1:]]]

  def _isPreterminal(self, p):
    return (type(p[1]) == str)

  def _str(self, n):
    p = self._getProduction(n)

    if self._isPreterminal(n):
      return '(' + p[0] + ' ' + p[1] + ')'
    
    out = '(' + n[0]
    for i in range(len(p[1])):
      out += ' ' + self._str(n[i+1])
    out += ')'
    return out

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

  def getSentence(self, dn):
    return _sentences[dn][self.lineNo][0]
  
  def getParse(self, dn):
    return _sentences[dn][self.lineNo][1]

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
    if self.con1.start > self.con2.start:
      x = [ self.con1.lineNo,
            self.con1.start,
            self.con1.end,
            self.con2.start,
            self.con2.end ]
    else: 
      x = [ self.con1.lineNo,
            self.con2.start,
            self.con2.end,
            self.con1.start,
            self.con1.end ]
    return hash("%d%d%d%d%d" % tuple(x))

    #return hash("%d%d%d%d%d" % ( self.con1.lineNo,
    #                             self.con1.start,
    #                             self.con1.end,
    #                             self.con2.start,
    #                             self.con2.end ))

  def getConcepts(self):
    return self.con1, self.con2

  def get_sentences(self, dn):
    return self.con1.getSentence(dn), self.con2.getSentence(dn)
  
  def get_parses(self, dn):
    return self.con1.getParse(dn), self.con2.getParse(dn)

class Entry:

  def __init__(self, relation, docName):
    self._dn = docName
    self.relation = relation

  def validateRelation(self, relations):
    try:
      self.relation.label = relations[self.relation]
    except KeyError:
      cp = (self.relation.con1.label, self.relation.con2.label)
      if cp == ('treatment', 'problem') or cp == ('problem', 'treatment'):
        # No relation between treatment and medical problem.
        self.relation.label = 'NTrP'
      elif cp == ('test', 'problem') or cp == ('problem', 'test'):
        # No relationship between test and a medical problem.
        self.relation.label = 'NTeP'
      elif cp == ('problem', 'problem'):
        # No relationship between problem and problem.
        self.relation.label = 'NPP'
      else:
        # Undefined pair. (Invalid relation)
        self.relation.label = 'O'

  def getConcepts(self):
    return self.relation.getConcepts()

  def getSentences(self):
    return self.relation.get_sentences(self._dn)

  def getParses(self):
    return self.relation.get_parses(self._dn)

  def getEnrichedTree(self, mode='spt'):
    """
      Returns enriched tree.
    """
    parse = self.getParses()[0]
    con_tokens = [c.concept for c in self.getConcepts()]
    con_labels = [c.label for c in self.getConcepts()]
    if mode == 'insert':
      return parse.insertion(con_tokens, con_labels)
    elif mode == 'suffix':
      return parse.suffix(con_tokens, con_labels)
    else:
      return parse.spt(*con_tokens)
      
class Note:
  
  def __init__(self, txt, con, par, rel = None):

    self.docName = os.path.splitext(os.path.basename(txt))[0] 
    self.data = set() # A set of entries
    self.read(txt, con, par, rel)

  def read(self, txt, con, par, rel = None):
    '''
    Note:read()
      Read in data from document set

    @param txt: file path for medical record
    @param con: file path for concept annotations for given txt file
    @param rel: file path for relations between concepts in given con file
    @param par: file path for parse trees
    '''


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
          concepts[concept.lineNo].append(concept)
        except KeyError:
          concepts[concept.lineNo] = list()
          concepts[concept.lineNo].append(concept)

    # read medical record
    # Only the sentences that contain concepts are needed for training/testing
    with open(txt) as t:
      with open(par) as p:
        for lineNo, (sent,pars) in enumerate(zip(t,p)):
          lineNo += 1 # Line number starts at 1, not 0
          try:
          #>>> for i, v1 in enumerate(a):
          #...     for v2 in a[i+1:]:
          #...             print v1, v2
          #  for i, concept1 in enumerate(concepts[lineNo]):
          #    for j, concept2 in enumerate(concepts[lineNo]):
          #      if i != j:
          #        self.data.add(Entry(Relation(con1=concept1, con2=concept2), self.docName))
          #        _sentences[self.docName][concept1.lineNo] = (sent, ParseTree(pars))
            for i, concept1 in enumerate(concepts[lineNo]):
              for concept2 in concepts[lineNo][i+1:]:
                self.data.add(Entry(Relation(con1=concept1, con2=concept2), self.docName))
                _sentences[self.docName][concept1.lineNo] = (sent, ParseTree(pars))
            #for concept1 in concepts[lineNo]:
            #  for concept2 in concepts[lineNo]:
            #    if concept1 != concept2:
            #      self.data.add(Entry(Relation(con1=concept1, con2=concept2), self.docName))
            #      _sentences[self.docName][concept1.lineNo] = (sent, ParseTree(pars))
          except KeyError:
            continue
          except SyntaxError:
            print "WARNING: could not make parse tree for %s : %d" % (self.docName, concept1.lineNo)
            _sentences[self.docName][concept1.lineNo] = (sent, ParseTree('( (root NULL) )'))
    
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
      # Remove invalid Entries
      self.data = self.data.intersection([x for x in self.data if x.relation.label != 'O'])



  def write(self, outDir):
    outPath = os.path.join(outDir, self.docName + ".rel")

    with open(outPath, 'w') as f:
      for entry in self.data:
        # Ommit unlabeled concept pairs
        if entry.relation.label !=  'O':
          print >>f, entry.relation

def makeNotes(dir, v, train=False):
  """
    Returns a list of notes
  """
  notes = list()

  if (v):
    sys.stdout.write("\t\tExtracting files from %s\n" % dir)

  files = extract_files(dir, train)

  if (files == None):
    sys.stderr.write("Error parsing files\n")
    sys.exit(1)

  for file in files:
    notes.append(Note(*file))

  if (v):
    sys.stdout.write("\t\t%d notes created\n" % len(notes))

  return notes

if __name__ == "__main__":
  NUM = 3
  notes = makeNotes('i2b2_examples/', True, True)
  entries = list()
  for n in notes:
    entries += n.data

  entry = entries[1] 
  par = entry.getParses()[0]
 
  for entry in entries:
    print entry.getParses()[0]
    print "spt:"
    print entry.getEnrichedTree()
    print "Insertion:"
    print entry.getEnrichedTree('insert')
    print "Suffix"
    print entry.getEnrichedTree('suffix')
    print entry.getSentences()[1].strip()
    print entry.relation.label
    print
