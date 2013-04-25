import math
import store
import utils


def score(file_path, hmm_depth=3):
    song = utils.parse_song(file_path)
    song = utils.trim_song(song, length=2500)
    song_len = len(song[0])
    score = 0

    for x in range(0, song_len):
        frame = utils.sized_observation_from_index(song, start=x, length=hmm_depth)
        frame_obs = frame.split(".")
        numerator_obs = frame
        denominator_obs = ".".join(utils.flatten_redundant_starts(frame_obs[:-1]))
        numerator_count = store.count_for_obs(numerator_obs)
        denominator_count = store.count_for_obs(denominator_obs)

        if numerator_count is None:
            print "SHOULD SMOOTH COUNT for numerator %s" % (numerator_obs)
            numerator_count = 1

        if denominator_count is None:
            print "SHOULD SMOOTH COUNT for denominator %s" % (denominator_obs)
            denominator_count = 1

        score -= math.log(float(numerator_count))
        score += math.log(float(denominator_count))
    print float(score) / song_len


def get_scorer(hmm_depth):
    return lambda file_path: score(file_path, hmm_depth)
