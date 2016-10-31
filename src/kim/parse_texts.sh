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
#           These parses are written to the parse directory as .parse files.

printf "Running Parser...\n"
d=`dirname $0`

if [[ -f $1 ]]
then
  printf "Parsing $1\n"
  # Removing file extension
  x=`basename $1`
  y=${x%%.*}
  cat $1 | java -jar $d/berkeleyparser/BerkeleyParser-1.7.jar -gr $d/berkeleyparser/eng_sm6.gr > `dirname $1`/../parse/${y##*/}.parse
  sed -i 's/\"/\\"/g' `dirname $1`/../parse/${y##*/}.parse
  exit
fi

if [[ -d $1 ]]
then
  for f in `ls $1`
  do
    printf "Parsing $1$f\n"
    # Removing file extension
    x=$f
    y=${x%%.*}
    # Parse
    cat $1$f | java -jar $d/berkeleyparser/BerkeleyParser-1.7.jar -gr $d/berkeleyparser/eng_sm6.gr > $1/../parse/${y##*/}.parse
    sed -i 's/\"/\\"/g' $1/../parse/${y##*/}.parse
  done
fi
