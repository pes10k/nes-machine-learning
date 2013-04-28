import os
import midi
import utils
from utils import trim_song, parse_song, sized_observation_from_index

data_dir = os.path.join("data", "training_songs")
training_files = []
max_pitch = 0
min_pitch = 100
for root, dirs, files in os.walk(data_dir):
	for name in [a_file for a_file in files if a_file[-4:] == ".mid"]:
		relative_path = os.path.join(root, name)
		print relative_path
		song = parse_song(relative_path)
		song = trim_song(song, length=2500)
		song_len = len(song[0])

		for x in range(0, song_len):
			frame = sized_observation_from_index(song, start=x, length=1)
			current_observation = [str(chan_data[x]) for chan_data in song.values()]
			for i in current_observation:
				print i
				if i>max_pitch:
					max_pitch = i
				if i<min_pitch:
					print i
					min_pitch = i

print max_pitch
print min_pitch
