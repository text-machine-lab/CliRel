""" 
 Text-Machine Lab: CliRel

 File Name :

 Creation Date : 10-10-2016

 Created By : Renan Campos
 
 Purpose : Trains a specified model on the given data.

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
    >>> main('i2b2_examples/', 'model_example/')
    'Example model success.'
    >>> main('i2b2_examples/', 'model_example/', ['a', 'b'])
    'Example model success with flags a b.'
  """
  con = os.path.join(t_dir, 'concept')
  txt = os.path.join(t_dir, 'txt')
  rel = os.path.join(t_dir, 'rel')

  data = createEntries(con, txt, rel)

  # import the model.
  # The model will be loaded as a module. This provides modularity for the
  # assumption that the model is implemented with a 'model.py' in its main dir. 
  model = imp.load_module('model', *imp.find_module('model', [model_path]))

  return model.train(data, model_flags)

if __name__ == '__main__':
  import doctest
  doctest.testmod()
