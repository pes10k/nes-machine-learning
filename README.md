nes-machine-learning
====================

Code needed for building the data and learner for predicting chiptunes using
MIDI representations

Files
-----

    data/
        training/*.mid
            - Midi files used for training the algorithm.  Comprises 2/3rds of
              the midi's we've gathered
        testing/*.mid
            - Midi files used for testing the algorithm.  Comprises 1/3rd of the
              midi's we've gathered
        training_counts.data
            - A serialized set of counts for observations in the training data.
              The file is a pickel'd python dict, with two sub-structures, one a
              list files that have been processed so far, and the other a dict
              of counts, with 1 through 32-wise observations


Installing
----------

Just install python-midi by running:

 1.  `cd contrib/python-midi`
 2.  `python setup.py install`


Related Software
----------------

 *  [nes2midi](http://gigo.retrogames.com/)
    Windows tool for converting [NSF](http://en.wikipedia.org/wiki/NES_Sound_Format) files to [MIDI](http://en.wikipedia.org/wiki/MIDI).  The original software is in Japanese, but there is thankfully an [English translation](http://www.neshq.com/nsf/nsf2mid-0.131-eng.zip) too!
 *  [WINE](http://www.winehq.org/)
    Windows DLL implementation used for running the above software on OSX and Linux. [OSX instructions](http://wiki.winehq.org/MacOSX) are available on the WINE site.
