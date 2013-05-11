import random
import hmm
import shutil
import os

try:
	from midiutil.MidiFile import MIDIFile
except ImportError:
	print "Error: Cann't import midiutil package. Did you run `python setup.py install` from ./contrib/MIDIUtil?"

# Tracks are numbered from zero. Times are measured in beats.

pitch_upbound = 100
pitch_lowbound = 0
duration_max = 4
duration_min = 0
song_length = random.randint(25, 80)
count_of_songs = 100

volume = 100

relative_file_path = "data/testing_songs/Random Songs"

for index in range(0, count_of_songs):
	song_length = random.randint(25, 80)
	file_name = str(index) + ".mid";
	time = 0;
	midi_scratch_file = MIDIFile(3)
	for i in range(0,3):
		midi_scratch_file.addTrackName(i, 0, "Pop Flute {0}".format(i))
		midi_scratch_file.addTempo(i, 0, 240)

		time = 0;
		while time < song_length:
			duration = random.uniform(duration_min, duration_max)
			pitch = random.randint(pitch_lowbound, pitch_upbound)
			midi_scratch_file.addNote(i, i, pitch, time, duration, volume)
			time += duration

	file_full_path = os.path.join(relative_file_path, file_name)
	binfile = open(file_full_path, 'w')
	midi_scratch_file.writeFile(binfile)
	binfile.close()

	score = hmm.score(file_full_path, hmm_depth=3, obs=song_length)
	print 'The socre of %s is %d' % (file_name, score)

print 'Finished!'
