import sys
import csv
import hmm
import bayes_net
from collections import OrderedDict
import song_collections


models = [("Bayes Net", bayes_net.score)] + [("{0} Order HMM".format(i), hmm.get_scorer(i)) for i in range(2, 7)]
models = OrderedDict(models)

writer = csv.writer(sys.stdout)

header_row = ["File", "Type"]

for label, model in models.items():
    header_row.append(label)
    header_row.append(r"% diff from random")

writer.writerow(header_row)

random_model_values = []
for i in range(len(models)):
    random_model_values.append(list())

for song in song_collections.random_songs:
    row = [song, "random"]
    index = 0
    for model in models.values():
        value = model(song)
        random_model_values[index].append(value)
        row.append(value)
        row.append("")
        index += 1
    writer.writerow(row)

averages_row = ['Averages', '']
print random_model_values
for model_values in random_model_values:
    averages_row.append(float(sum(model_values)) / len(model_values))
    averages_row.append('')

writer.writerow(averages_row)
writer.writerow(('',))
