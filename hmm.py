import math
import store
import utils


num_possible_prev_states = 128 ** 3


def score(file_path, hmm_depth=3, cache=None, obs=1000, smooth=True):
    song = utils.parse_song(file_path)
    song = utils.trim_song(song, length=2500)
    song_len = len(song[0])

    # I don't know of any reliable way to normalize the log-likelyhood
    # for different length probabilities, so we're just going to limit
    # things to a fixed number of observations to normalize the lenght
    # of observations per file, intestead of normalizing the probabilities
    # of different length songs
    if song_len < obs:
        print " !! %s is too short (%d)" % (file_path, song_len)
        return None

    scores = []

    for x in range(0, obs):
        frame = utils.sized_observation_from_index(song, start=x, length=hmm_depth)
        frame_obs = frame.split(".")
        numerator_obs = frame
        denominator_obs = ".".join(utils.flatten_redundant_starts(frame_obs[:-1]))

        if cache is not None:
            if numerator_obs in cache:
                numerator_count = cache[numerator_obs]
            else:
                numerator_count = store.count_for_obs(numerator_obs) or 0
                numerator_count += 1  # if smooth else 0
                cache[numerator_obs] = numerator_count

            if denominator_obs in cache:
                denominator_count = cache[denominator_obs]
            else:
                denominator_count = store.count_for_obs(denominator_obs) or 0
                denominator_count += num_possible_prev_states  # if smooth else 0
                cache[denominator_obs] = denominator_count
        else:
            numerator_count = store.count_for_obs(numerator_obs) or 0
            numerator_count += 1  # if smooth else 0
            denominator_count = store.count_for_obs(denominator_obs) or 0
            denominator_count += num_possible_prev_states  # if smooth else 0

        scores.append(math.log(float(numerator_count) / denominator_count, 10))

    return sum(scores)


def get_scorer(hmm_depth, cache=None):
    return lambda file_path: score(file_path, hmm_depth, cache)
