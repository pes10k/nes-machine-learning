import os
import math
import store
from utils import trim_song, sized_observation_from_index, flatten_redundant_starts

try:
    import midi
except ImportError:
    print "Error: Can't import Midi package. Did you run 'python setup.py install' from ./contrib/python-midi?"

data_dir = os.path.join("data")
max_channel_to_capture = 3
prev_frames_to_record = 16

#test songs' path
test_data_dir = os.path.join("test_data")
#path of file to store scores
score_store_path = os.path.join(os.getcwd(), test_data_dir, 'scores.data')

score_store = dict(files=[], counts=dict())

for root, dirs, files in os.walk(test_data_dir):
    for name in [a_file for a_file in files if a_file[-4:] == ".mid"]:
        relative_test_file_path = os.path.join(root, name)

        print 'Adding %s into path array' % relative_test_file_path
        score_store['files'].append(relative_test_file_path)
        score_store.setdefault(relative_test_file_path, dict())
        tmp_score = score_store[relative_test_file_path]

        song = {}
        handle = open(relative_test_file_path)
        parser = midi.FileReader()
        test_file_data = parser.read(handle)

        #print relative_test_file_path
        for track in test_file_data:
            track.make_ticks_abs()
            note_events = [event for event in track if hasattr(event, 'channel') and event.channel < max_channel_to_capture and event.tick > 0]

            for event in note_events:
                channel = song.setdefault(event.channel, [])
                channel_index = int(event.channel)
                name = event.name

                if name == "Note On":
                    channel += ([0] * (event.tick - len(channel) - 1))
                    channel.append(event.get_pitch())
                elif name == "Note Off":
                    channel += ([event.get_pitch()] * (event.tick - len(channel)))
                else:
                    channel += ([0] * (event.tick - len(channel)))

        song = trim_song(song, length=2500)
        song_len = len(song[0])

        print 'Length is %d.' % song_len

        scores = dict()
        for y in range(2, prev_frames_to_record + 1):
            scores[y] = 0
            score = 0
            for x in range(0, song_len):
                frame = sized_observation_from_index(song, start=x, length=y)
                frame_obs = frame.split(".")
                numerator_obs = frame
                denominator_obs = ".".join(flatten_redundant_starts(frame_obs[:-1]))
                numerator_count = store.count_for_obs(numerator_obs)
                denominator_count = store.count_for_obs(denominator_obs)
                score -= math.log(float(numerator_count))
                score += math.log(float(denominator_count))

            scores[y] = score
        print scores

# print score_store

# score_handle = open(score_store_path, 'w')
# pickle.dump(score_store, score_handle)
# score_handle.close()
