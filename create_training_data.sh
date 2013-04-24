#!/bin/bash
# Delete any existing training and testing data
rm -Rf training_data
rm -Rf testing_data
mkdir training_data
mkdir testing_data


# Create any possible needed directories
find data -type d | sed 's/ /\\ /g' |  xargs -I % mkdir -p "training_%"
find data -type d | sed 's/ /\\ /g' |  xargs -I % mkdir -p "testing_%"

# Copy over 2/3rds of data into training directory, 1/3rd to testing
find data -name *.mid | tr ' ' '\ ' | awk 'BEGIN { srand() } { if (rand() >= .33) print "cp \""$0"\" \"training_"$0"\""; else print "cp \""$0"\" \"testing_"$0"\"";}' | tr ' ' '\ ' | xargs
# find data -name *.mid | tr ' ' '\ ' | awk 'BEGIN { srand() } (rand() >= .33) { print $0 }' | tr '\n' '\0' | xargs -0 -I % cp % training_%
