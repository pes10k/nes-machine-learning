import os
import sqlite3
import math
import utils
from utils import trim_song, sized_observation_from_index, parse_song

min_smoothed_prob = 1.0 / 128
min_smoothed_prob_log = math.log(min_smoothed_prob)


def score(file_path, cache=None, obs=1000):
    song = utils.parse_song(file_path)
    song = utils.trim_song(song, length=2500)
    song_len = len(song[0])

    # I don't know of any reliable way to normalize the log-likelyhood
    # for different length probabilities, so we're just going to limit
    # things to a fixed number of observations to normalize the lenght
    # of observations per file, intestead of normalizing the probabilities
    # of different length songs
    if song_len < obs:
        print " !! %s is too short (%d)" % (file_path, song_len)
        return None

    scores = []

    for x in range(0, obs):
        frame = utils.sized_observation_from_index(song, start=x, length=2)
        frame_1, frame_2 = frame.split(".")
        frame_1_chan_1, frame_1_chan_2, frame_1_chan_3 = frame_1.split("|")
        frame_2_chan_1, frame_2_chan_2, frame_2_chan_3 = frame_2.split("|")

        frame_1_chan_2_count = cross_obs_count(frame_1_chan_2, 2)
        frame_1_chan_3_count = cross_obs_count(frame_1_chan_3, 3)
        frame_2_chan_1_count = inner_obs_count(frame_2_chan_1)

        f1_c1_to_f2_c1_num = cross_obs_count(frame_1_chan_1, 1, frame_2_chan_1, 1)
        if f1_c1_to_f2_c1_num is not None:
            f1_c1_to_f2_c1_prob = math.log(float(f1_c1_to_f2_c1_num + 1) / (cross_obs_count(frame_1_chan_1, 1) + 128), 10)
        else:
            f1_c1_to_f2_c1_prob = min_smoothed_prob_log

        f1_c2_to_f2_c1_num = cross_obs_count(frame_1_chan_2, 2, frame_2_chan_1, 1)
        if f1_c2_to_f2_c1_num is not None:
            f1_c2_to_f2_c1_prob = math.log(float(f1_c2_to_f2_c1_num + 1) / (frame_1_chan_2_count + 128), 10)
        else:
            f1_c2_to_f2_c1_prob = min_smoothed_prob_log

        f1_c3_to_f2_c1_num = cross_obs_count(frame_1_chan_3, 3, frame_2_chan_1, 1)
        if f1_c3_to_f2_c1_num is not None:
            f1_c3_to_f2_c1_prob = math.log(float(f1_c3_to_f2_c1_num + 1) / (frame_1_chan_3_count + 128), 10)
        else:
            f1_c3_to_f2_c1_prob = min_smoothed_prob_log

        f1_c2_to_f2_c2_num = cross_obs_count(frame_1_chan_2, 2, frame_2_chan_2, 2)
        if f1_c2_to_f2_c2_num is not None:
            f1_c2_to_f2_c2_prob = math.log(float(f1_c2_to_f2_c2_num + 1) / (frame_1_chan_2_count + 128), 10)
        else:
            f1_c2_to_f2_c2_prob = min_smoothed_prob_log

        f1_c3_to_f2_c3_num = cross_obs_count(frame_1_chan_3, 3, frame_2_chan_3, 3)
        if f1_c3_to_f2_c3_num is not None:
            f1_c3_to_f2_c3_prob = math.log(float(f1_c3_to_f2_c3_num + 1) / (frame_1_chan_3_count + 128), 10)
        else:
            f1_c3_to_f2_c3_prob = min_smoothed_prob_log

        f2_c1_to_f2_c2_num = inner_obs_count(frame_2_chan_1, frame_2_chan_2, 2)
        if f2_c1_to_f2_c2_num is not None:
            f2_c1_to_f2_c2_prob = math.log(float(f2_c1_to_f2_c2_num + 1) / (frame_2_chan_1_count + 128), 10)
        else:
            f2_c1_to_f2_c2_prob = min_smoothed_prob_log

        f2_c1_to_f2_c3_num = inner_obs_count(frame_2_chan_1, frame_2_chan_3, 3)
        if f2_c1_to_f2_c3_num is not None:
            f2_c1_to_f2_c3_prob = math.log(float(f2_c1_to_f2_c3_num + 1) / (frame_2_chan_1_count + 128), 10)
        else:
            f2_c1_to_f2_c3_prob = min_smoothed_prob_log

        scores.append(f1_c1_to_f2_c1_prob + f1_c2_to_f2_c1_prob + f1_c3_to_f2_c1_prob + f1_c2_to_f2_c2_prob + f1_c3_to_f2_c3_prob + f2_c1_to_f2_c2_prob + f2_c1_to_f2_c3_prob)
    return sum(scores)

#
# Data Store Related Methods
#


def get_connection():
    if not hasattr(get_connection, '_conn'):
        get_connection._conn = sqlite3.connect(os.path.join('data', 'bayes_training_counts.sqlite3'))
        # Do a test check, just so we can create the tables if needed
        cur = get_connection._conn.cursor()
        try:
            cur.execute('SELECT COUNT(*) FROM cross_obs_counts WHERE obs_1 = "DOES NOT EXIST"')
        except sqlite3.OperationalError:
            setup()
    return get_connection._conn


def setup():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('CREATE TABLE training_files (filename text)')
    cur.execute('CREATE UNIQUE INDEX filename ON training_files (filename)')

    cur.execute('CREATE TABLE inner_obs_counts (obs_1 int, obs_2 int, chan_2 int, count int)')
    cur.execute('CREATE INDEX obs_1 ON inner_obs_counts (obs_1)')
    cur.execute('CREATE UNIQUE INDEX obs_1_obs_2_chan_2 ON inner_obs_counts (obs_1, obs_2, chan_2)')

    cur.execute('CREATE TABLE cross_obs_counts (obs_1 int, chan_1 int, obs_2 int, chan_2 int, count int)')
    cur.execute('CREATE INDEX obs_1_chan_1 ON cross_obs_counts (obs_1, chan_1)')
    cur.execute('CREATE UNIQUE INDEX obs_1_chan_1_obs_2_chan_2 ON cross_obs_counts (obs_1, chan_1, obs_2, chan_2)')
    commit()


def has_file_been_recorded(filename):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) AS count FROM training_files WHERE filename = ?', (filename,))
    row = cur.fetchone()
    return row[0] > 0


def record_file(filename):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO training_files (filename) VALUES (?)', (filename,))


def inner_obs_count(obs_1, obs_2=None, chan_2=None):
    conn = get_connection()
    cur = conn.cursor()
    if obs_2 and chan_2:
        cur.execute('SELECT count FROM inner_obs_counts WHERE obs_1 = ? AND obs_2 = ? AND chan_2 = ? LIMIT 1', (obs_1, obs_2, chan_2))
    else:
        cur.execute('SELECT SUM(count) FROM inner_obs_counts WHERE obs_1 = ?', (obs_1,))
    row = cur.fetchone()
    return row[0] if row else None


def record_inner_obs_count(obs_1, obs_2, chan_2):
    conn = get_connection()
    cur = conn.cursor()
    current_count = inner_obs_count(obs_1, obs_2, chan_2)

    if current_count is None:
        cur.execute('INSERT INTO inner_obs_counts (obs_1, obs_2, chan_2, count) VALUES (?, ?, ?, 1)', (obs_1, obs_2, chan_2))
    else:
        cur.execute('UPDATE inner_obs_counts SET count = count + 1 WHERE obs_1 = ? AND obs_2 = ? AND chan_2 = ?', (obs_1, obs_2, chan_2))


def cross_obs_count(obs_1, chan_1, obs_2=None, chan_2=None):
    conn = get_connection()
    cur = conn.cursor()
    if obs_2 and chan_2:
        cur.execute('SELECT count FROM cross_obs_counts WHERE obs_1 = ? AND chan_1 = ? AND obs_2 = ? AND chan_2 = ? LIMIT 1', (obs_1, chan_1, obs_2, chan_2))
    else:
        cur.execute('SELECT SUM(count) AS count FROM cross_obs_counts WHERE obs_1 = ? AND chan_1 = ?', (obs_1, chan_1))
    row = cur.fetchone()
    return row[0] if row else None


def record_cross_obs_count(obs_1, chan_1, obs_2, chan_2):
    conn = get_connection()
    cur = conn.cursor()

    current_count = cross_obs_count(obs_1, chan_1, obs_2, chan_2)
    if current_count is None:
        cur.execute('INSERT INTO cross_obs_counts (obs_1, chan_1, obs_2, chan_2, count) VALUES (?, ?, ?, ?, 1)', (obs_1, chan_1, obs_2, chan_2,))
    else:
        cur.execute('UPDATE cross_obs_counts SET count = count + 1 WHERE obs_1 = ? AND chan_1 = ? AND obs_2 = ? AND chan_2 = ?', (obs_1, chan_1, obs_2, chan_2,))


def commit():
    conn = get_connection()
    conn.commit()


def train_on_files(files):

    for a_file in files:
        if has_file_been_recorded(a_file):
            print "Not recalculating counts for %s" % (a_file,)
            continue
        else:
            print "Beginning to calculate counts for %s" % (a_file,)
            record_file(a_file)

        song = parse_song(a_file)
        song = trim_song(song, length=2500)
        song_len = len(song[0])

        if song_len < 100:
            print "Song is too short for consideration.  May be a sound effect or something trivial.  Ignoring."
            continue

        for x in range(0, song_len):
            frame = sized_observation_from_index(song, start=x, length=2)
            frame_1, frame_2 = frame.split(".")
            frame_1_chan_1, frame_1_chan_2, frame_1_chan_3 = frame_1.split("|")
            frame_2_chan_1, frame_2_chan_2, frame_2_chan_3 = frame_2.split("|")

            # We treat channel one as the most important one, so first
            # record the counts of all channels in frame 1 transitioning
            # into channel 1 in frame 2
            record_cross_obs_count(frame_1_chan_1, 1, frame_2_chan_1, 1)
            record_cross_obs_count(frame_1_chan_2, 2, frame_2_chan_1, 1)
            record_cross_obs_count(frame_1_chan_3, 3, frame_2_chan_1, 1)

            # Now also record the remaining channels trainsitioning to
            # themselves in the next channel
            record_cross_obs_count(frame_1_chan_2, 2, frame_2_chan_2, 2)
            record_cross_obs_count(frame_1_chan_3, 3, frame_2_chan_3, 3)

            # Last, record the transitioning from the assumed "melody" in the
            # new frame to the assumed "background" channels in the new
            # frame
            record_inner_obs_count(frame_2_chan_1, frame_2_chan_2, 2)
            record_inner_obs_count(frame_2_chan_1, frame_2_chan_3, 3)

        commit()
        print "finished calculating counts from %s" % (a_file,)


if __name__ == "__main__":

    data_dir = os.path.join("data", "training_songs")
    training_files = []
    for root, dirs, files in os.walk(data_dir):
        for name in [a_file for a_file in files if a_file[-4:] == ".mid"]:
            training_files.append(os.path.join(root, name))

    train_on_files(training_files)
