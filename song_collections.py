import os

training_songs_path = os.path.join('data', 'training_songs')


def songs_in_dir(path):
    songs = []
    for root, dirs, files in os.walk(path):
        for name in [a_file for a_file in files if a_file[-4:] == ".mid"]:
            songs.append(os.path.join(root, name))
    return songs


training_songs = songs_in_dir(os.path.join('data', 'training_songs'))
testing_sogns = songs_in_dir(os.path.join('data', 'testing_songs'))
all_songs = songs_in_dir(os.path.join('data', 'all_songs'))
random_songs = songs_in_dir('attempts')

