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


def sized_observation_from_index(song, start=0, length=1):
    song_length = len(song[0])
    pre_flow = (start - length) + 1
    frames_left = 0

    # if the requested section flows past the start of the song, pad the
    # returned set with 0's
    if pre_flow < 0:
        frames = ".".join(["0|0|0"] * abs(pre_flow)) + "."
        frames_left = length - abs(pre_flow)
    else:
        frames_left = length
        frames = ""

    frames_indexes = range(start - frames_left, start)
    frames += ".".join([serialize_observation(song, i) for i in frames_indexes])
    return frames
