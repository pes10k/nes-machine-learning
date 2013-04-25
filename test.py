import os
import utils
import hmm
from pprint import pprint

files_to_test = []
test_path = os.path.join("data", "testing_songs")
for root, dirs, files in os.walk(test_path):
    for name in [a_file for a_file in files if a_file[-4:] == ".mid"]:
        files_to_test.append(os.path.join(root, name))


models = {"HMM: %d Step" % (i,): hmm.get_scorer(i) for i in range(2, 16)}
for label, model in models.items():
    print label
    scores_for_model = utils.score_files_with_model(files_to_test, model)
    num_scores = len(scores_for_model)
    total_scores = sum([score for score in scores_for_model.values()])
    average_score = float(total_scores) / num_scores
    print "Average Score: (%d/%d) -> %f" % (total_scores, num_scores, average_score)

