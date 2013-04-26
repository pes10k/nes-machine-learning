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
song_length = 25
count_of_songs = 1

max_score = -1000000
min_score = 0

volume = 100

min_score = -87
score = -1000
temp_file = None
max_tries = 100000
tries = 0
best_score = -100000

relative_file_path = "attempts/generated.mid"

while score < min_score:
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

    binfile = open(relative_file_path, 'w')
    midi_scratch_file.writeFile(binfile)
    binfile.close()

    # And write it to disk.
    # temp_file = tempfile.NamedTemporaryFile()
    # midi_scratch_file.writeFile(temp_file)
    # Next, score the file using a 2-depth HMM
    score = hmm.score(relative_file_path, hmm_depth=3, obs=song_length)
    new_best_score = max(best_score, score)
    if new_best_score > best_score:
        best_score = new_best_score
        shutil.copyfile(relative_file_path, "attempts/score_{0}.mid".format(best_score))

    print "Got Score: %d (tries %d, best score: %d)" % (score, tries, best_score)

shutil.copyfile(relative_file_path, "attempts/best_%d.mid" % (score,))
print "Finished!"
