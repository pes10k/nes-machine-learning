import hmm
import utils


song_length = 150


def get_begin_of_song(relative_file_path, depth):
    song = utils.parse_song(relative_file_path)
    song = utils.trim_song(song, length=2500)
    begin = [channel[:depth] for channel in song]
    return begin


def predict_song(song_start, scoring_function, frame_filter=None, length=100, order=1, variability=0):
    from copy import copy
    from random import randint

    song = copy(song_start)
    init_song_len = utils.song_length(song)
    possible_frames = [[int(note) for note in frame.split("|")] for frame in hmm.all_observations()]

    cache = dict()

    for i in range(0, length - init_song_len):

        print "SONG: %s" % (song)

        if i == 0:
            current_frame_obs = [[channel[i]] for channel in song]
        else:
            obs_to_pull = min(utils.song_length(song), order - 1)
            current_frame_obs = [channel[-1 * obs_to_pull:] for channel in song]

        scores = {}

        prev_frame = [channel[-1] for channel in song]

        if frame_filter is not None:
            filtered_frames = [frame for frame in possible_frames if frame_filter(prev_frame, frame)]
            # if we filtered everything out, easy back and let the full set back in
            if len(filtered_frames) > 0:
                local_possible_frames = filtered_frames
            else:
                local_possible_frames = possible_frames
        else:
            local_possible_frames = possible_frames

        for a_frame in local_possible_frames:
            score = scoring_function(current_frame_obs, a_frame, smooth=False, cache=cache)
            scores["|".join([str(note) for note in a_frame])] = score

        sorted_scores = sorted([(value, key) for (key, value) in scores.items() if value is not None], reverse=True)

        print current_frame_obs
        print sorted_scores[0:10]

        # If we don't have any valid transitions from this state, we just have
        # to guess a new one at random (not great!)  We just use semi popular
        # observations, to limit the damage
        if len(sorted_scores) == 0:
            print "WARNING, Random Transition!"
            random_frames = all_observations(cutoff=200)
            selected_observation = (0, random_frames[randint(0, len(random_frames) - 1)])
        elif variability == 0 or len(sorted_scores) == 1:
            selected_observation = sorted_scores[0]
        else:
            selected_observation = sorted_scores[randint(0, min(variability - 1, len(sorted_scores) - 1))]

        print selected_observation

        frame_parts = [int(part) for part in selected_observation[1].split("|")]

        for i in range(0, 3):
            song[i].append(frame_parts[i])
        print "Generated note {0}/{1}".format(utils.song_length(song), length)
    print song
    return song


if __name__ == "__main__":
    from hmm import all_observations
    from random import randint
    import bayes_net
    import argparse
    import os

    parser = argparse.ArgumentParser(description='Generate chiptunes, magically.')
    parser.add_argument('--file', default="", dest='file', help='The file to write the resulting midi song to.  Defaults to m-<model>_o-<order>_s-<shake>_l-<length>.mid')
    parser.add_argument('--length', default=20, dest='length', help="The number of notes to generate in the song", type=int)
    parser.add_argument('--model', default="hmm", dest='model', help="The model to use to generate the resulting file", choices=('hmm', 'bayes'))
    parser.add_argument('--order', dest='order', default=1, help="The order to use when generating predictions for the next note.  If using HMM, must be 2 or larger", type=int)
    parser.add_argument('--shake', dest='shake', default=1, help="How randomly to generate notes in the song", type=int)
    parser.add_argument('--filter', dest='filter', default='none', help="Custom filter to apply to the set of possible next notes considered for each step.  Options include: 'none', 'require_lead', 'no_repeats', 'no_empties', 'all', max_one_empty")
    parser.add_argument('--start', dest='start', default='', help="Song to start building a song off.  If not included, we'll just choose a random note.")

    args = parser.parse_args()

    scorer = hmm.score_transition if args.model == "hmm" else bayes_net.score_transition

    # Get a random starting note from the training data.
    possible_starts = all_observations(cutoff=200, include_starts=True)
    start_position = possible_starts[randint(0, len(possible_starts) - 1)]
    start_notes = start_position.split('|')

    def require_lead(pre_frame, post_frame):
        return post_frame[0] > 0

    def no_repeats(pre_frame, post_frame):
        return pre_frame != post_frame

    def no_empties(pre_frame, post_frame):
        return post_frame.count(0) == 0

    def max_one_empty(pre_frame, post_frame):
        return post_frame.count(0) <= 1

    def all_filters(pre_frame, post_frame):
        filters = (
            require_lead,
            no_repeats,
            # no_empties
        )

        for a_filter in filters:
            if a_filter(pre_frame, post_frame) is False:
                return False
        return True

    if args.filter == "none":
        frame_filter = None
    elif args.filter == 'require_lead':
        frame_filter = require_lead
    elif args.filter == 'no_repeats':
        frame_filter = no_repeats
    elif args.filter == 'no_empties':
        frame_filter = no_empties
    elif args.filter == 'max_one_empty':
        frame_filter = max_one_empty
    elif args.filter == 'all':
        frame_filter = all_filters

    # If a song was specified, load it out of the song corpus, else
    # pick one randomly
    if args.start:
        song = get_begin_of_song(os.path.join('data', 'all_songs', args.start), args.order)
    else:
        song = [[int(start_notes[i])] for i in range(0, len(start_notes))]

    new_song = predict_song(song, scorer, length=args.length,
                            order=args.order, variability=args.shake, frame_filter=frame_filter)

    output_path = args.file if len(args.file) > 0 else "m-{0}_o-{1}_s-{2}_l-{3}.mid".format(
        args.model, args.order, args.shake, args.length)

    print "Writing song to {0}".format(output_path)
    utils.write_song(new_song, output_path)
