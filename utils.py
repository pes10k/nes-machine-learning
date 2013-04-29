try:
    import midi
except ImportError:
    print "Error: Can't import Midi package. Did you run 'python setup.py install' from ./contrib/python-midi?"

try:
    from midiutil.MidiFile import MIDIFile
except ImportError:
    print "Error: Can't import midiutil package. Did you run `python setup.py install` from ./contrib/MIDIUtil?"


def write_song(song, dest, tempo=240):
    num_channels = len(song)
    midi_scratch_file = MIDIFile(num_channels)
    for i in range(0, num_channels):
        midi_scratch_file.addTrackName(i, 0, "Pop Flute {0}".format(i))
        midi_scratch_file.addTempo(i, 0, tempo)
        time = 0
        for x in range(0, song_length(song)):
            duration = 0.5
            pitch = song[i][x]
            midi_scratch_file.addNote(i, i, pitch, time, duration, 100)
            time += duration

    bin_file = open(dest, 'w')
    midi_scratch_file.writeFile(bin_file)
    bin_file.close()


def song_length(song):
    return len(song[0])


def score_files_with_model(file_paths, model_scorer):
    scores = dict()
    for path in file_paths:
        print " -- Scoring " + path
        scores[path] = model_scorer(path)
    return scores


def parse_song(file_path, max_channel=2):
    """Reads a MIDI file from disk and returns a dense, python representation

    Args:
        file_path -- Path to MIDI file on disk

    Keyword Args:
        max_channel -- The highest channel to return, zero indexed

    Returns:
        A dict, with each index being the channel for the corresponding data
    """
    handle = open(file_path)
    parser = midi.FileReader()
    midi_data = parser.read(handle)
    song = [[], [], []]

    for track in midi_data:
        track.make_ticks_abs()
        note_events = [event for event in track if hasattr(event, 'channel') and event.channel <= max_channel and event.tick > 0]

        for event in note_events:
            name = event.name

            if name == "Note On":
                song[event.channel] += ([0] * (event.tick - len(song[event.channel]) - 1))
                song[event.channel].append(event.get_pitch())
            elif name == "Note Off":
                song[event.channel] += ([event.get_pitch()] * (event.tick - len(song[event.channel])))
            else:
                song[event.channel] += ([0] * (event.tick - len(song[event.channel])))
    return song


def trim_song(song, length=None):
    song = normalize_song(song, length)
    song = strip_header_off_song(song)
    song = strip_end_off_song(song)
    return song


def normalize_song(song, length=None):
    """Make sure that all tracks in the song have the same length, equal
    to the shortest track"""
    channel_sizes = [len(channel) for channel in song]
    if length:
        channel_sizes.append(length)
    min_length = min(channel_sizes)
    return [channel[:min_length] for channel in song]


def strip_header_off_song(song):

    # First check for the trivial corner case of having an empty song
    is_empty = sum([sum(channel) for channel in song]) == 0

    if is_empty:
        return [[], [], []]
    else:
        index = 0
        while sum([channel[index] for channel in song]) == 0:
            index += 1
        return [channel[index:] for channel in song]


def strip_end_off_song(song):
    song = [channel[::-1] for channel in song]
    song = strip_header_off_song(song)
    return [channel[::-1] for channel in song]


def serialize_observation(song, index):
    return "|".join([str(channel[index]) for channel in song])


def flatten_redundant_starts(frames):
    first_non_start = -1
    last_viewed_frame = -1
    for i in range(0, len(frames)):
        last_viewed_frame += 1
        if frames[i] != "S|S|S":
            first_non_start = i
            break

    if first_non_start > 0:
        frames[first_non_start:]
    elif last_viewed_frame == len(frames) - 1:
        frames = frames[0:1]

    return frames


def sized_observation_from_index(song, start=0, length=1, serialize=True):
    pre_flow = (start - length) + 1
    frames_left = 0

    # if the requested section flows past the start of the song, pad the
    # returned set with 0's
    if pre_flow < 0:
        frames = ".".join(["S|S|S"] * abs(pre_flow)) + "."
        frames_left = length - abs(pre_flow)
    else:
        frames_left = length
        frames = ""

    frames_indexes = range(start - frames_left, start)
    frames += ".".join([serialize_observation(song, i) for i in frames_indexes])
    return frames
