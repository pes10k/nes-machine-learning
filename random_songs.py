import os
import random
try:
	from midiutil.MidiFile import MIDIFile
except ImportError:
	print "Error: Cann't import midiutil package. Did you run `python setup.py install` from ./contrib/MIDIUtil?"

data_dir = os.path.join("test_data/Random Song/")

# Tracks are numbered from zero. Times are measured in beats.

pitch_upbound = 100
pitch_lowbound = 20
duration_max = 1
duration_min = 0.1
song_length = 100
count_of_songs = 1
MyMIDI = [MIDIFile(3) for i in range (0,count_of_songs)]

track = 0
time = 0
channel = 0
pitch = 60
duration = 1
volume = 100

for count in range(1,count_of_songs+1):
	track = 0
	for track in range(0,3):
		MyMIDI[count-1].addTrackName(track,time,"Sample Track " + str(track))
		MyMIDI[count-1].addTempo(track,time,50)
		while time<song_length:
			duration = random.uniform(duration_min,duration_max)
			pitch = random.randint(pitch_lowbound,pitch_upbound)
			MyMIDI[count-1].addNote(track,channel,pitch,time,duration,volume)
			time += duration
		time = 0

	# And write it to disk.
	relative_file_path = data_dir + str(count) + ".mid"
	binfile = open(relative_file_path, 'w')
	MyMIDI[count-1].writeFile(binfile)
	binfile.close()
