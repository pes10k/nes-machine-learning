import random
import hmm
import utils
import midi
try:
	from midiutil.MidiFile import MIDIFile
except ImportError:
	print "Error: Can't import midiutil package. Did you run `python setup.py install` from ./contrib/MIDIUtil?"

pitch_upbound = 100
pitch_lowbound = 0 
duration_max = 4
duration_min = 0
song_length = 150
count_of_songs = 1

max_score = -1000000
min_score = 0

volume = 100
relative_file_path = "attempts/generated_begin.mid"

def create_song_beginning(beginning_dept):
	midi_scratch_file = MIDIFile(3)
	for i in range(0,3):
		midi_scratch_file.addTrackName(i, 0, "Pop Flute {0}".format(i))
		midi_scratch_file.addTempo(i, 0, 240)

		time = 0
		while time  < beginning_dept:
			duration = random.uniform(duration_min, duration_max)
			duration = 1
			pitch = random.randint(pitch_lowbound+20, pitch_upbound)
			midi_scratch_file.addNote(i, i, pitch, time, duration, volume)

			time+=duration
	binfile = open(relative_file_path, 'w')
	midi_scratch_file.writeFile(binfile)
	binfile.close
	return relative_file_path


def get_begin_of_song(relative_file_path, depth):
	song = utils.parse_song(relative_file_path)
	song = utils.trim_song(song, length=2500)
	song_len = len(song[0])

	begin = {i: song[i][:depth] for i in range(0,3)}
	return begin

def predict_songs(begin, Model_name):
	if Model_name == "HMM":
		depth = len(begin[0])
		#midi_scratch_file = MIDIFile(3)
		#for i in range(0,3):
			#midi_scratch_file.addTrackName(i, 0, "Pop Flute {0}".format(i))
			#midi_scratch_file.addTempo(i, 0, 240)
			#time = 0
			#for x in range(0, depth):
				#duration = 0.5;
				#pitch = begin[i][x]
				#midi_scratch_file.addNote(i, i, pitch, time, duration, volume)
				#time += duration
		#print begin
		#binfile = open(relative_file_path, 'w')
		#midi_scratch_file.writeFile(binfile)
		#binfile.close()

		song = begin

		#print song

		for x in range(depth, song_length):
			print x
			print song
			current_frame_obs= utils.sized_observation_from_index(song, x, length=depth)
			count_tmp = hmm.count_for_obs(current_frame_obs)
			#print count_tmp
			#print current_frame_obs
			cache = []
			option_count = 0
			#print current_frame_obs
			for option_1 in range(pitch_lowbound, pitch_upbound):
				for option_2 in range(pitch_lowbound, pitch_upbound):
					for option_3 in range(pitch_lowbound, pitch_upbound):
						next_frame_obs = str(option_1) + "|" + str(option_2) + "|" + str(option_3)
						next_obs_option = current_frame_obs + "." + next_frame_obs
						count = hmm.count_for_obs(next_obs_option)
						#print next_obs_option
						#print count
						if count == None:
							continue
						#break
						if option_count < 3:
							option_count += 1
						cache.append({'obs':[option_1,option_2,option_3],'count':count})
						

			cache.sort(key = lambda cache:cache['count'], reverse = True)
			print cache
			option_index = random.randint(0, option_count-1)
			for i in range(0,3):
				song[i].append(cache[option_index]['obs'][i])
		midi_scratch_file = MIDIFile(3)
		for i in range(0,3):
			midi_scratch_file.addTrackName(i, 0, "Pop Flute {0}".format(i))
			midi_scratch_file.addTempo(i, 0, 240)
			time = 0
			for x in range(0, song_length):
				duration = 0.5
				pitch = song[i][x]
				midi_scratch_file.addNote(i,i,pitch,time,duration,volume)
				time += duration

		binFile = open(relative_file_path, 'w')
		midi_scratch_file.writeFile(binFile)
		binFile.close()



if __name__ == "__main__":
	for i in range(1, 2):
		print 
		begin = get_begin_of_song("data/training_songs/Contra/2.mid",i)
		predict_songs(begin, "HMM")
	#predict_songs(relative_path, "HMM", beginning_depth)
	#predict_songs(relative_path, "HMM", beginning_depth)
