import os
from utils import trim_song, sized_observation_from_index
from pprint import pprint

try:
    import cpickle as pickle
except ImportError:
    import pickle

try:
    import midi
except ImportError:
    print "Error: Can't import Midi package.  Did you run `python setup.py install from ./contrib/python-midi?"

data_dir = os.path.join("data")
max_channel_to_capture = 3
prev_frames_to_record = 32

training_files = ["1.mid"]

persistant_store_path = os.path.join(os.getcwd(), data_dir, 'training_counts.data')
store_handle = open(persistant_store_path, 'rb')

try:
    print "Appending to current data store"
    persistant_store = pickle.load(store_handle)
except (EOFError, IOError) as e:
    print "Starting with empty data store"
    persistant_store = dict(files=[], counts=dict())

store_handle.close()
counts_dict = persistant_store['counts']

for root, dirs, files in os.walk(data_dir):
    for name in [a_file for a_file in files if a_file[-4:] == ".mid"]:
        relative_file_path = os.path.join(root, name)

        if relative_file_path in persistant_store['files']:
            print "Not recalculating counts for %s" % (relative_file_path,)
            continue
        else:
            print "Beginning to calculate counts for %s" % (relative_file_path,)
            persistant_store['files'].append(relative_file_path)

        song = {}
        handle = open(relative_file_path)
        parser = midi.FileReader()
        file_data = parser.read(handle)

        for track in file_data:
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

        # for x in range(0, len(song[0])):
        #     print "|".join([str(chanel[x]) for chanel in song.values()])
        #     #print "%d: %s" % (k, ["%03d" % (i,) for i in song[k]])
        # break

        for x in range(0, len(song[0])):
            for y in range(1, prev_frames_to_record + 1):
                frame = sized_observation_from_index(song, start=x, length=y)
                counts_dict.setdefault(frame, 0)
                counts_dict[frame] += 1
        print "finished calculating counts from %s" % (relative_file_path,)

store_handle = open(persistant_store_path, 'wb')
pickle.dump(persistant_store, store_handle)
store_handle.close()
