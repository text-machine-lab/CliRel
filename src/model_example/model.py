""" 
 Text-Machine Lab: CliRel

 File Name : model.py

 Creation Date : 10-10-2016

 Created By : Renan Campos

 Purpose : An example model to show the basic layout.

"""

def train(data, flags):
  """
    Example model just prints success for testing.
    Also shows flags.
    >>> train(None, None)
    'Example model success.'
    >>> train(None, ['a', 'b'])
    'Example model success with flags a b.'
  """

  out = "Example model success"

  if flags:
    out += " with flags"
    for f in flags:
      out += " " + f

  return out + "."

if __name__ == '__main__':
  import doctest
  doctest.testmod()
