#!/bin/sh -

CORPUS_PATH=$1
PIPED_LEMMA=$2


ROOT=$(pwd)


function search_corpus()
{
    cd $CORPUS_PATH
    cd corpus

    grep -Ri -P -o "[^.?!]*\b($PIPED_LEMMA)\b[^.?!]*[.?!]?"

    cd $ROOT
}

search_corpus

