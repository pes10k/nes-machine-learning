nes-machine-learning
====================

Code needed for building the data and learner for predicting chiptunes using
MIDI representations

Files
-----

    data/
        raw/*
            - All of the MIDI files that have been generated and collected so
              far
        all_songs/*
            - A subset of the *raw* directory that only includes songs that
              have been manually labeled as "songs", as opposed to empty
              tracks, sound effects or other background songs.
        training_songs/*
            - A subset of the *all_songs* directory, approx 2/3 of it,
              containing songs that should be used to generate and train
              the algorithm with.
        testing_songs/*
            - A subset of the *all_songs* directory, containing the approx
              1/3 of the songs that are not in the *training_songs* directory,
              that should be used for testing the accuracy of the algorithm
        training_counts.sqlite3
            - The generated sqlite3 database of transition counts (generated
              with the *training.py* file) based off the *training_songs*
              directory


Installing
----------

install python-midi by running:

 1.  `cd contrib/python-midi`
 2.  `python setup.py install`

install MIDIUtil by running:

 1.	 `cd contrib/MIDIUtil`
 2.  `python setup.py install`

You'll also want to generate some training counts.  You can do so with:

 1.  `python training.py`


Related Software
----------------

 *  [nes2midi](http://gigo.retrogames.com/)
    Windows tool for converting [NSF](http://en.wikipedia.org/wiki/NES_Sound_Format) files to [MIDI](http://en.wikipedia.org/wiki/MIDI).  The original software is in Japanese, but there is thankfully an [English translation](http://www.neshq.com/nsf/nsf2mid-0.131-eng.zip) too!
 *  [WINE](http://www.winehq.org/)
    Windows DLL implementation used for running the above software on OSX and Linux. [OSX instructions](http://wiki.winehq.org/MacOSX) are available on the WINE site.
