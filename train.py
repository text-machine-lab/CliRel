# CliRel: train.py
#   Primary script for training a model
#
# Connor Cooper

import os
import argparse
import cPickle
import glob

from code import model
from code.notes import note

def main():

    parser = argparse.ArguementParser()

    parser.add_argument("train_dir",
                        type=str,
                        help="Files to train the model on. Files should come in sets of three, in the form <name>.txt, <name>.con, <name>.rel")

    parser.add_argument("model_dest",
                        type=str,
                        help="Where the model will be stored")

    args = parser.parse_args()

    # TODO: ensure model output directory exists

    train_dir = args.train_dir

    files = glob.glob(train_dir)

    txt_files = []
    con_files = []
    rel_files = []

    for f in files:
        if f[-3:] == '.txt':
            txt_files.append(f)
        elif f[-3:] == '.con':
            con_files.append(f)
        elif f[-3:] == '.rel':
            rel_files.append(f)

    txt_files.sort()
    con_files.sort()
    rel_files.sort()

    assert len(txt_files) == len(con_files) == len(rel_files)

    model = train_model(txt_files, con_files, rel_files)

    # save model
    with open(args.model_dest, "wb") as mod_file:
        cPickle.dump(model, mod_file)


def train_model( txt_files, con_files, rel_files ):

    notes = []

    for txt, con, rel in zip(txt_files, con_files, rel_files):

        assert basename(txt) == basename(con) == basename(rel), "file names do not correspond; %s, %s, %s".format(txt, con, rel)

        tmp_note = Note(txt, con, rel)
        notes.append(tmp_note)

    mod = model.Model()
    mod.train(notes)

    return mod
    

if __name__ == "__main__":
    main()
