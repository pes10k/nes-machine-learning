try:
    import midi
except ImportError:
    print "Error: Can't import Midi package. Did you run 'python setup.py install' from ./contrib/python-midi?"


def score_files_with_model(file_paths, model_scorer):
    scores = dict()
    for path in file_paths:
        print "Scoring " + path
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
    song = {}

    for track in midi_data:
        track.make_ticks_abs()
        note_events = [event for event in track if hasattr(event, 'channel') and event.channel <= max_channel and event.tick > 0]

        for event in note_events:
            channel = song.setdefault(event.channel, [])
            name = event.name

            if name == "Note On":
                channel += ([0] * (event.tick - len(channel) - 1))
                channel.append(event.get_pitch())
            elif name == "Note Off":
                channel += ([event.get_pitch()] * (event.tick - len(channel)))
            else:
                channel += ([0] * (event.tick - len(channel)))
    return song


def trim_song(song, length=None):
    song = normalize_song(song, length)
    song = strip_header_off_song(song)
    song = strip_end_off_song(song)
    return song


def normalize_song(song, length=None):
    """Make sure that all tracks in the song have the same lenght, equal
    to the shortest track"""
    channel_sizes = [len(channel) for k, channel in song.items()]
    if length:
        channel_sizes.append(length)
    min_length = min(channel_sizes)
    return {k: v[:min_length] for k, v in song.items()}


def strip_header_off_song(song):
    # First check for the trivial corner case of having an empty song
    is_empty = sum([sum(channel) for channel in song.values()]) == 0

    if is_empty:
        return {i: [] for i in range(0, 3)}
    else:
        index = 0
        while sum([track[index] for track in song.values()]) == 0:
            index += 1
        return {k: v[index:] for k, v in song.items()}


def strip_end_off_song(song):
    song = {k: v[::-1] for k, v in song.items()}
    song = strip_header_off_song(song)
    return {k: v[::-1] for k, v in song.items()}


def serialize_observation(song, index):
    current_observation = [str(chan_data[index]) for chan_data in song.values()]
    return "|".join(current_observation)


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


def sized_observation_from_index(song, start=0, length=1):
    song_length = len(song[0])
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
