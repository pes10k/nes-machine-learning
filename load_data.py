import os
import math
from utils import trim_song, sized_observation_from_index

try:
	import cpickle as pickle
except ImportError:
	import pickle

try:
	import midi
except ImportError:
	print "Error: Can't import Midi package. Did you run 'python setup.py install' from ./contrib/python-midi?"

data_dir = os.path.join("data")
max_channel_to_capture = 3
prev_frames_to_record = 32

persistant_store_path = os.path.join(os.getcwd(), data_dir, 'training_counts.data')
store_handle = open(persistant_store_path, 'rb')

try:
	print "Getting access to current data store"
	persistant_store = pickle.load(store_handle)
except (EOFError, IOError) as e:
	print "Cannot get access to current data store"

store_handle.close()
counts_dict = persistant_store['counts']

#print counts_dict['79|54|42.79|54|40']
#print counts_dict.get('79|54|42')

#test songs' path
test_data_dir = os.path.join("test_data")
#path of file to store scores
score_store_path = os.path.join(os.getcwd(), data_dir, 'scores.data')

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
	
		print 'Length is %d.'% song_len
		count = 0
		score = 0.0
		tmp = 0.0
		content = ''
		for y in range(1, prev_frames_to_record + 1):
			frame_next = sized_observation_from_index(song, start=0, length=y)
			for x in range(0, song_len):
				if x == 0:
					frame_next = sized_observation_from_index(song, start=x, length=y)
				#	print counts_dict.get(frame_next)
					if counts_dict.get(frame_next) == None:
						tmp = 1
					else:
						tmp = counts_dict[frame_next]
					#print tmp;
					score -= math.log(tmp);
				else:
					frame_previous = frame_next;	
					frame_next = sized_observation_from_index(song, start=x, length=y)
					content = frame_previous + '.' + frame_next
					#print content
					#print counts_dict.get(content)
					if counts_dict.get(content) == None:
						tmp = 1
					else:
						tmp = counts_dict.get(content)
					score -= math.log(tmp)
					if counts_dict.get(frame_previous) == None:
						tmp = 1
					else:
						tmp = counts_dict[frame_previous]
					score += math.log(tmp)
			#print score 
			tmp_score.setdefault(y,0)
			tmp_score[y] = score
			##print tmp_score
print score_store	

score_handle = open(score_store_path, 'w')
pickle.dump(score_store, score_handle)
score_handle.close()
