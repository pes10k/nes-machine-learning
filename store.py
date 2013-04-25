import os
import sqlite3


def get_connection():
    if not hasattr(get_connection, '_conn'):
        get_connection._conn = sqlite3.connect(os.path.join('data', 'training_counts.sqlite3'))
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
    cur.execute('CREATE TABLE note_counts (observation text, count int)')
    cur.execute('CREATE UNIQUE INDEX filename ON training_files (filename)')
    cur.execute('CREATE UNIQUE INDEX observation ON note_counts (observation)')
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


def count_for_obs(obs, cache=True):
    if cache:
        try:
            if obs in count_for_obs._cache:
                return count_for_obs._cache[obs]
        except:
            count_for_obs._cache = dict()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT count FROM note_counts WHERE observation = ?', (obs,))
    row = cur.fetchone()
    result = row[0] if row else None
    if cache:
        count_for_obs._cache[obs] = result
    return result


def record_obs(obs):
    conn = get_connection()
    cur = conn.cursor()

    current_count = count_for_obs(obs)
    if current_count is None:
        cur.execute('INSERT INTO note_counts (observation, count) VALUES (?, 1)', (obs,))
    else:
        cur.execute('UPDATE note_counts SET count = count + 1 WHERE observation = ?', (obs,))


def commit():
    conn = get_connection()
    conn.commit()
