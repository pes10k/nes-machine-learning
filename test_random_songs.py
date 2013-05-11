import os
import utils
import hmm
import bayes_net
from collections import OrderedDict

files_to_test = []
test_path = os.path.join("data", "Random Songs")
for root, dirs, files in os.walk(test_path):
	for name in [a_file for a_file in files if a_file[-4:] == ".mid"]:
		files_to_test.append(os.path.join(root,name))

log_path = "log"
model_scores = OrderedDict()

for hmm_depth in range(2,7):
	model_label = "HMM: %d Depth" % (hmm_depth,)
	print model_label

	cache = dict()
	model = hmm.get_scorer(hmm_depth, cache)
	scores_for_model = utils.score_files_with_model(files_to_test, model)
	num_scores = len(scores_for_model)
	total_scores = sum([score for score in scores_for_model.values() if score is not None])
	average_score = float(total_scores) / num_scores


	log_name = "HMM_" + str(hmm_depth) + "_random.txt"
	log_full_path = os.path.join(log_path, log_name);
	f = open(log_full_path, 'w')
	index = 1
	for score in scores_for_model.values():
		if score is not None:
			print >> f, "%d %f" % (index, score)
			index += 1
	f.close()

	print "Average Score: (%d/%d) -> %f" % (total_scores, num_scores, average_score)
	model_scores[model_label] = average_score

print 'Bayes net'
bayes_net_scores = utils.score_files_with_model(files_to_test, bayes_net.score)
num_scores = len(bayes_net_scores)
total_scores = sum([score for score in bayes_net_scores.values() if score is not None])
average_score = float(total_scores) / num_scores
model_scores['Bayes Net'] = average_score
log_name = "bayes_net_random.txt"
log_full_path = os.path.join(log_path, log_name)
f = open(log_full_path, 'w')
index = 1
for score in bayes_net_scores.values():
	if score is not None:
		print >> f, "%d %f" % (index, score)
		index += 1

f.close()

log_name = 'model_aver_random_scores.txt'
log_full_path = os.path.join(log_path, log_name)
f = open(log_full_path, 'w')
for label, score in model_scores.items():
	print "%s: %f" % (label, score)
	print >> f, "%s: %f" % (label, score)
f.close()
