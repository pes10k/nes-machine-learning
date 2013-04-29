import hmm
import utils


song_length = 150


def get_begin_of_song(relative_file_path, depth):
    song = utils.parse_song(relative_file_path)
    song = utils.trim_song(song, length=depth)
    begin = [song[channel][:depth] for channel in song]
    return begin


def predict_song(song_start, scoring_function, length=100, order=1, variability=10):
    from copy import copy
    from random import randint

    song = copy(song_start)
    current_length = utils.song_length(song_start)
    possible_frames = [[int(note) for note in frame.split("|")] for frame in hmm.all_observations()]
    possible_frames = [frame for frame in possible_frames if frame.count(0) == 0]

    for i in range(current_length, length):

        current_frame_obs = [channel[i - 1:order + i - 1] for channel in song]
        scores = {}
        for a_frame in possible_frames:
            scores["|".join([str(note) for note in a_frame])] = scoring_function(current_frame_obs, a_frame)
        sorted_scores = sorted(scores, key=lambda x: x[1])[::-1]
        selected_observation = sorted_scores[randint(0, variability - 1)]
        frame_parts = [int(part) for part in selected_observation.split("|")]
        for i in range(0, 3):
            song[i].append(frame_parts[i])
        print "Song Generated {0}/{1}".format(utils.song_length(song), length)
    return song


if __name__ == "__main__":
    import sys
    from hmm import all_observations
    from random import randint
    import bayes_net
    import argparse

    parser = argparse.ArgumentParser(description='Generate chiptunes, magically.')
    parser.add_argument('--file', default="output.mid", dest='file', help='The file to write the resulting midi song to')
    parser.add_argument('--length', default="20", dest='length', help="The number of notes to generate in the song", type=int)
    parser.add_argument('--model', default="hmm", dest='model', help="The model to use to generate the resulting file", choices=('hmm', 'bayes'))
    parser.add_argument('--order', dest='order', default='1', help="The order to use when generating predictions for the next note.  If using HMM, must be 2 or larger", type=int)
    parser.add_argument('--shake', dest='shake', default='5', help="How randomly to generate notes in the song", type=int)

    args = parser.parse_args()

    scorer = hmm.score_transition if args.model == "hmm" else bayes_net.score_transition

    # Get a random starting note from the training data.
    possible_starts = all_observations(cutoff=200, include_starts=True)
    start_position = possible_starts[randint(0, len(possible_starts) - 1)]
    start_notes = start_position.split('|')

    # Transform this starting position into a "song", even if it'll be really
    # short
    song = [[int(start_notes[i])] for i in range(0, len(start_notes))]
    new_song = predict_song(song, scorer, length=args.length,
                            order=args.order, variability=args.shake)
    utils.write_song(new_song, args.file)
