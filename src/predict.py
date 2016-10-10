""" 
 Text-Machine Lab: CliRel

 File Name : predict.py

 Creation Date : 10-10-2016

 Created By : Renan Campos

 Purpose : Creates relation labesl for the data given the model.

"""

import os
import imp
from note import createEntries

# Take in data dir and model type
# Load in model's train
# Save model
# return the model
def main(t_dir, model_path, model_flags=None):
  """
    Output should be the data with labels. 
    For the example model, the new labels are all !
    >>> main('i2b2_examples/', 'model_example/').ix[0]
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
  data = createEntries(con, txt)

  # import the model.
  # The model will be loaded as a module. This provides modularity for the
  # assumption that the model is implemented with a 'model.py' in its main dir. 
  model = imp.load_module('model', *imp.find_module('model', [model_path]))

  out =  model.predict(data, model_flags)
  data["relType"] = out
  return data

if __name__ == '__main__':
  import doctest
  doctest.testmod()
