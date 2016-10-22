""" 
 Text-Machine Lab: CliRel

 File Name :

 Creation Date : 22-10-2016

 Created By : Renan Campos

 Purpose : Trains, predicts and evaluates for clinical relation task.

"""

import os
import imp
import note

def absPath(path):
  """ Return absolute path from where this file is located """
  return os.path.join(os.path.dirname(os.path.abspath(__file__)), path)

def train(t_dir, model_path, model_flags=None):
  """
    >>> train('i2b2_examples/', 'model_example/')
    'Example model success.'
    >>> train('i2b2_examples/', 'model_example/', ['a', 'b'])
    'Example model success with flags a b.'
  """
  con = os.path.join(t_dir, 'concept')
  txt = os.path.join(t_dir, 'txt')
  rel = os.path.join(t_dir, 'rel')

  data = note.createEntries(con, txt, rel)

  # import the model.
  # The model will be loaded as a module. This provides modularity for the
  # assumption that the model is implemented with a 'model.py' in its main dir. 
  model = imp.load_module('model', *imp.find_module('model', [model_path]))

  return model.train(data, model_flags)


def predict(t_dir, model_path, model_flags=None):
  """
    Output should be the data with labels. 
    For the example model, the new labels are all !
    >>> predict('i2b2_examples/', 'model_example/').ix[0]
    conEnd1                                              1
    conEnd2                                              4
    conStart1                                            0
    conStart2                                            3
    conText1                                This treatment
    conText2                               medical problem
    conType1                                     treatment
    conType2                                       problem
    fileName                                        health
    lineNum                                              1
    relType                                              !
    text         This treatment improves medical problem .
    Name: 0, dtype: object
  """
  con = os.path.join(t_dir, 'concept')
  txt = os.path.join(t_dir, 'txt')
  data = note.createEntries(con, txt)

  # import the model.
  # The model will be loaded as a module. This provides modularity for the
  # assumption that the model is implemented with a 'model.py' in its main dir. 
  model = imp.load_module('model', *imp.find_module('model', [model_path]))

  out =  model.predict(data, model_flags)
  data["relType"] = out

  for each in set(data['fileName']):
    with open(os.path.join(absPath('predictions'), 
                             each + '.pred'), 'w') as f:
      def writeToFile(d):
        f.write(note.writeRel(d) + '\n')
      data.apply(writeToFile, axis=1)

  return data

def evaluate(g_dir, p_dir):
  """
    Extracts the relation files from the gold directory and the 
    prediciton directory, and calculates the F1, recall, and precision.
    For this current iteration of the task, we are only concerned if the model
    is able to identify a relation between two concepts (ignoring order).
  """
  return


if __name__ == '__main__':
  import doctest
  doctest.testmod()
