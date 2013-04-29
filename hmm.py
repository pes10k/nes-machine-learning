import os
import sqlite3
import math
import utils
from utils import trim_song, sized_observation_from_index, parse_song, serialize_observation


num_possible_prev_states = 128 ** 3


def score_transition(song_chunk, new_frame, smooth=True, cache=None):
    num_frames = utils.song_length(song_chunk)
    prev_frames = ["|".join([str(song_chunk[0][i]), str(song_chunk[1][i]), str(song_chunk[2][i])]) for i in range(0, num_frames)]

    denominator_obs = ".".join(prev_frames)
    numerator_obs = denominator_obs + "." + "|".join([str(n) for n in new_frame])

    if cache is not None:
        if numerator_obs in cache:
            numerator_count = cache[numerator_obs]
        else:
            numerator_count = count_for_obs(numerator_obs) or 0
            numerator_count += 1 if smooth else 0
            cache[numerator_obs] = numerator_count

        if denominator_obs in cache:
            denominator_count = cache[denominator_obs]
        else:
            denominator_count = count_for_obs(denominator_obs) or 0
            denominator_count += num_possible_prev_states if smooth else 0
            cache[denominator_obs] = denominator_count
    else:
        numerator_count = count_for_obs(numerator_obs) or 0
        numerator_count += 1 if smooth else 0
        denominator_count = count_for_obs(denominator_obs) or 0
        denominator_count += num_possible_prev_states if smooth else 0

    return None if numerator_count == 0 and not smooth else math.log(float(numerator_count) / denominator_count, 10)


def score(data, hmm_depth=3, cache=None, obs=1000, smooth=True, check_len=True):
    song = data if isinstance(data, list) else utils.parse_song(data)
    song = utils.trim_song(song, length=2500)
    song_len = len(song[0])

    # I don't know of any reliable way to normalize the log-likelyhood
    # for different length probabilities, so we're just going to limit
    # things to a fixed number of observations to normalize the lenght
    # of observations per file, intestead of normalizing the probabilities
    # of different length songs
    if check_len and song_len < obs:
        print " !! %s is too short (%d)" % (data, song_len)
        return None

    scores = []

    for x in range(0, obs):
        frame = utils.sized_observation_from_index(song, start=x, length=hmm_depth)
        frame_obs = frame.split(".")
        top_frame = frame_obs[-1].split("|")
        song_chunk = [[], [], []]
        for a_frame in frame_obs[:-1]:
            note_1, note_2, note_3 = a_frame.split("|")
            song_chunk[0].append(note_1)
            song_chunk[1].append(note_2)
            song_chunk[2].append(note_3)
        scores.append(score_transition(song_chunk, top_frame, smooth, cache))

    return sum(scores)


def get_scorer(hmm_depth, cache=None):
    return lambda file_path: score(file_path, hmm_depth, cache)

#
# Data Store Related Methods
#


def get_connection():
    if not hasattr(get_connection, '_conn'):
        get_connection._conn = sqlite3.connect(os.path.join('data', 'hmm_training_counts.sqlite3'))
        # Do a test check, just so we can create the tables if needed
        cur = get_connection._conn.cursor()
        try:
            cur.execute('SELECT COUNT(*) FROM note_counts WHERE observation = "DOES NOT EXIST"')
        except sqlite3.OperationalError:
            setup()
    return get_connection._conn


def setup():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('CREATE TABLE training_files (filename text)')
    cur.execute('CREATE TABLE note_counts (observation text, count int, num_frames int, has_start tinyint)')
    cur.execute('CREATE UNIQUE INDEX filename ON training_files (filename)')
    cur.execute('CREATE UNIQUE INDEX observation ON note_counts (observation)')
    cur.execute('CREATE INDEX num_frames ON note_counts (num_frames)')
    cur.execute('CREATE INDEX has_start ON note_counts (has_start)')
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


def count_for_obs(obs):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT count FROM note_counts WHERE observation = ?', (obs,))
    row = cur.fetchone()
    return row[0] if row else None


def record_obs(obs):
    conn = get_connection()
    cur = conn.cursor()

    current_count = count_for_obs(obs)
    if current_count is None:
        cur.execute('INSERT INTO note_counts (observation, count, num_frames, has_start) VALUES (?, 1, ?, ?)', (obs, obs.count(".") + 1, 1 if "S" in obs else 0))
    else:
        cur.execute('UPDATE note_counts SET count = count + 1 WHERE observation = ?', (obs,))


def all_observations(cutoff=1, include_starts=False):
    conn = get_connection()
    cur = conn.cursor()
    query = 'SELECT observation FROM note_counts WHERE num_frames = 1 AND count >= ?'
    if not include_starts:
        query += ' AND has_start = 0'
    cur.execute(query, (cutoff,))
    return [row[0] for row in cur.fetchall()]


def commit():
    conn = get_connection()
    conn.commit()


#
# Training Functions
#

def train_on_files(files, max_hmm_order=8):

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

        if song_len < 10:
            print "Song is too short for consideration.  May be a sound effect or something trivial.  Ignoring."
            continue

        record_obs('S|S|S')
        for x in range(0, song_len):
            for y in range(0, max_hmm_order + 1):
                if y > 0:
                    frame = sized_observation_from_index(song, start=x, length=y)
                    record_obs(frame)
                else:
                    frame = serialize_observation(song, x)
        commit()
        print "finished calculating counts from %s" % (a_file,)


if __name__ == "__main__":

    from song_collections import training_songs
    train_on_files(training_songs)
