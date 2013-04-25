import random
import hmm
import shutil

try:
    from midiutil.MidiFile import MIDIFile
except ImportError:
    print "Error: Cann't import midiutil package. Did you run `python setup.py install` from ./contrib/MIDIUtil?"


# Tracks are numbered from zero. Times are measured in beats.

pitch_upbound = 100
pitch_lowbound = 20
duration_max = 4
duration_min = 0
song_length = 100
count_of_songs = 1

max_score = -1000000
min_score = 0

volume = 100

min_score = -5
score = -1000
temp_file = None
max_tries = 100000
tries = 0

while tries < max_tries:
    tries += 1
    if temp_file:
        temp_file.close()
    time = 0
    midi_scratch_file = MIDIFile(3)
    for i in range(0, 3):
        midi_scratch_file.addTrackName(i, 0, "Pop Flute {0}".format(i))
        midi_scratch_file.addTempo(i, 0, 240)

        time = 0
        while time < song_length:
            duration = random.uniform(duration_min, duration_max)
            pitch = random.randint(pitch_lowbound, pitch_upbound)
            midi_scratch_file.addNote(i, i, pitch, time, duration, volume)
            # print "D: %d, p: %d, t: %d" % (duration, pitch, time)
            time += duration

    relative_file_path = "attempts/generated.mid"
    binfile = open(relative_file_path, 'w')
    midi_scratch_file.writeFile(binfile)
    binfile.close()

    # And write it to disk.
    # temp_file = tempfile.NamedTemporaryFile()
    # midi_scratch_file.writeFile(temp_file)
    # Next, score the file using a 2-depth HMM
    try:
        score = hmm.score(relative_file_path, hmm_depth=5, obs=song_length)

        if score < min_score:
            min_score = score
            shutil.copyfile(relative_file_path, "attempts/min_generated_%d.mid" % (score,))

        if score > max_score:
            max_score = score
            shutil.copyfile(relative_file_path, "attempts/max_generated_%d.mid" % (score,))

        print "Got Score: %d (tries %d)" % (score, tries)
    except:
        pass

print "Finished!"
