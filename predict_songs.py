import hmm
import utils


song_length = 150


def get_begin_of_song(relative_file_path, depth):
    song = utils.parse_song(relative_file_path)
    song = utils.trim_song(song, length=depth)
    begin = [song[channel][:depth] for channel in song]
    return begin


def predict_song(song_start, scoring_function, length=100, order=1, variability=5):
    from copy import copy
    from random import randint

    song = copy(song_start)
    current_length = utils.song_length(song_start)
    possible_frames = hmm.all_observations()

    for i in range(current_length, length):

        current_frame_obs = [channel[i - 1:order + i - 1] for channel in song]
        scores = {}
        for a_frame in possible_frames:
            frame_parts = [int(note) for note in a_frame.split("|")]
            scores[a_frame] = scoring_function(current_frame_obs, frame_parts)
        sorted_scores = sorted(scores, key=lambda x: x[1])[::-1]
        selected_observation = sorted_scores[randint(0, variability - 1)]
        frame_parts = [int(part) for part in selected_observation.split("|")]
        for i in range(0, 3):
            song[i].append(frame_parts[i])
    return song


if __name__ == "__main__":
    import sys
    from hmm import all_observations
    from random import randint
    import bayes_net

    if len(sys.argv) > 1:
        # Get a random starting note from the training data.
        possible_starts = all_observations(cutoff=100, include_starts=True)
        start_position = possible_starts[randint(0, len(possible_starts) - 1)]
        start_notes = start_position.split('|')

        # Transform this starting position into a "song", even if it'll be really
        # short
        song = [[int(start_notes[i])] for i in range(0, len(start_notes))]
        new_song = predict_song(song, bayes_net.score_transition, length=100)
        utils.write_song(new_song, sys.argv[1])
