#!/bin/bash
# Delete any existing training and testing data
rm -Rf data/all_songs
rm -Rf data/training_songs
rm -Rf data/testing_songs
mkdir data/all_songs
mkdir data/training_songs
mkdir data/testing_songs

# Also delete the training counts in the database, since they're no longer valid
rm data/training_counts.sqlite3

# Create any possible needed directories
for i in 'all' 'training' 'testing';
    do find data/raw -type d | tail -n `ls -ld data/raw/* | wc -l` | sed 's/ /\\ /g' | sed 's/data\/raw\//songs\//' | xargs -I % mkdir -p "data/${i}_%"
done;

# Next, copy the files that are actual songs into the data/all_songs directory
(cat data/non_songs.txt; find data/raw -name *.mid | sed 's/data\/raw\///g') | sort | uniq -u | tr '\n' '\0' | xargs -0 -I % cp "data/raw/%" "data/all_songs/%"

# Next, split the contents of the all_songs directory, with 2/3rds winding up
# in training set, and 1/3rd in the testing set
for file in `find data/all_songs -name *.mid | sed 's/\ /-/g'`;
    do
        if [ $(( $RANDOM % 3 )) == 0 ] ;
        then
            echo $file | sed 's/data\/all_songs//' | sed 's/\-/\\ /g' | xargs -I % cp "data/all_songs%" "data/testing_songs%";
        else
            echo $file | sed 's/data\/all_songs//' | sed 's/\-/\\ /g' | xargs -I % cp "data/all_songs%" "data/training_songs%";
        fi;
done;

