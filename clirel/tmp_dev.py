""" 
 Text-Machine Lab: CliRel

 File Name : tmp_dev.py

 Creation Date : 22-05-2016

 Created By : Renan Campos

 Purpose : A script that loads a toy note containing one fake entry, 
           for iterative development of the feature set.

"""

from clirel import makeNotes

import features.features as feat

notes = makeNotes('tmp/', True, True)

note = notes[0]

entry = note.data.pop()
note.data.add(entry)
