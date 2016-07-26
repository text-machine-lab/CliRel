#! /bin/bash
#
# Text-Machine Lab : CliRel
# 
# File Name : parse_texts.sh
#
# Creation Date : 27-05-2016
#
# Created By : Renan Campos
#
# Purpose : Uses the BerkeleyParser to create parse trees of the text files.
#           These parses are written to the parse directory as .pt files.
#
#           NOTE: Parenthesis are taken out to make life easier.

printf "Running Parser...\n"
d=`dirname $0`

if [[ -f $1 ]]
then
  printf "Parsing $1...\n"
  sed 's/(\+\|)\+//g' $1 | java -jar $d/berkeleyparser/BerkeleyParser-1.7.jar -gr $d/berkeleyparser/eng_sm6.gr > `dirname $1`/../parse/`basename $1.pt`
  exit
fi

for f in `ls $d/../data/txt/`
do
  printf "Parsing $d/../data/txt/$f...\n"
  sed 's/(\+\|)\+//g' $d/../data/txt/$f | java -jar $d/berkeleyparser/BerkeleyParser-1.7.jar -gr $d/berkeleyparser/eng_sm6.gr > $d/../data/parse/$f.pt
done
