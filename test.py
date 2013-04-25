import os
import utils
import hmm
from collections import OrderedDict

files_to_test = []
test_path = os.path.join("data", "testing_songs")
for root, dirs, files in os.walk(test_path):
    for name in [a_file for a_file in files if a_file[-4:] == ".mid"]:
        files_to_test.append(os.path.join(root, name))

model_scores = OrderedDict()

for hmm_depth in range(2, 7):
    model_label = "HMM: %d Depth" % (hmm_depth,)
    print model_label

    cache = dict()
    model = hmm.get_scorer(hmm_depth, cache)
    scores_for_model = utils.score_files_with_model(files_to_test, model)
    num_scores = len(scores_for_model)
    total_scores = sum([score for score in scores_for_model.values() if score is not None])
    average_score = float(total_scores) / num_scores

    print "Average Score: (%d/%d) -> %f" % (total_scores, num_scores, average_score)
    model_scores[model_label] = average_score

for label, score in model_scores.items():
    print "%s: %f" % (label, score)
