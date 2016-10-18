""" 
 Text-Machine Lab: CliRel

 File Name : parser.py

 Creation Date : 11-10-2016

 Created By : Renan Campos

 Purpose : Uses the berkeley parser to create parse trees.

"""

import os
from subprocess import Popen, PIPE
from time import sleep
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, read

def absPath(path):
  """ Return absolute path from where this file is located """
  return os.path.join(os.path.dirname(os.path.abspath(__file__)), path)

class BerkeleyParser:

  def __init__(self):
    p = Popen(['java', 
               '-jar', 
               absPath('./berkeleyparser/BerkeleyParser-1.7.jar'), 
               '-gr', 
               absPath('./berkeleyparser/eng_sm6.gr')],
    stdin = PIPE, stdout = PIPE, stderr = PIPE, shell = False)
    self.p = p 

  def parse(self, s):
    p = self.p
    # Replace parantheses with special token (to make parsing easier).
    s = s.replace('(','<LPAR>').replace(')', '<RPAR>')
    p.stdin.write(s + '\n')
    return read(p.stdout.fileno(), 1024)

  def close(self):
    self.p.communicate()

if __name__ == '__main__':
  """
    To test the berkeley parser, here is an interactive session.
  """
  BP = BerkeleyParser()
  while True:
    sent = raw_input("Enter a sentence (q to quit): ")
    if sent == 'q':
      break
    print BP.parse(sent)
  BP.close()
