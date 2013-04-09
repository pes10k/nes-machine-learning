CS491 – First Progress Report
=============================

Authors
-------
Xiang Huo and Peter Snyder

TL;DR
-----
Our NES/NSF music training and synthesis project is progressing well.  After some setbacks with our initial dataset and our conclusion that our originally planned model was too simple, we have made new plans for the next weeks for work and our back on track.

Materials
---------
Our training data and training code is being managed in our public [GitHub repo](
https://github.com/snyderp/nes-machine-learning).  Other tools that we are using, but which are not included in the code of the repository, are mentioned in the README.md file in the repo’s root.

Dataset Setbacks
----------------
Our initial plan was to use the large number of readily available MIDI versions of original NES game sound tracks online for our training and testing data sets.  Our assumption was that these MIDI files were straight conversions from the original NSF data that hobbyists and archivists had performed using the available, free tools, similarly to how many people share direct encodings of compressed music from CDs.

Once we started working with these files though, we found that this was not that case, and that a large, and not easily distinguishable, number of these MIDI files included alterations form the original recording. Some of these alterations were fan embellishment, others were amateur manual transcriptions, and still more were imperfect extractions using tools that introduced flaws or otherwise did not preserve the exact structure of the original NSF audio data.

Because of these findings, we have decided to treat all third party data as unreliable, and to perform our own direct extractions from the NSF data. The tools we have chosen are reliable and accurate, but are also old and Windows based and do not lend themselves to automation. As a result, performing these conversions and generating the needed training data has been far more time consuming that we expected.  We have a good procedure established now though, and are on the way to having sufficient data to work with.

Description of Data
-------------------
For the purposes of our project, MIDI data is made up of several types of information:
 *  **Instruments**: A description of how a synthesized tone should be generated. This includes details like wave forms, effects, and other descriptions of what should generate the waveform.
 *  **Events**: Records of changes in the what an instrument is doing, such as a note started playing, or the volume of the tracked changed.
 *  **Channels**: Pairs of instruments and events.  MIDI recordings can have up to 16 channels, simultaneously recorded and performing events.
 *  **MetaEvents**: Descriptions that effect the all channels, such as the tempo that events should be processed at.

MIDI data does not directly include any timing information, such as "event x should occur 32 seconds into the song." Instead, MIDI uses an atomic measure of a "tick" for sequencing. It is then left to the client to calculate the time the event should occur at by combining the tick the event occurred at with along with the tempo of the containing channel at the time the event occurred. Since we are not interested in "tempo" generation, and because NES songs have a fixed tempo for the length of the song, we discard this tempo information. We instead rely on MIDI ticks to give us a normalized way of measuring melody flow through a song.

MIDI data also does not include any information about the frequencies that notes should be played at. It instead uses a number between 0 and 127 to encode a note, C in octave 0 through G 10 octaves above. Events also do not directly including timing information, but instead include a record of how many ticks have occurred. This 0 note does not occur in any of our data (and would generally be inaudible to humans), so we overload 0 to denote no note occurring in our training records.  When a note is playing, we simply record the original MIDI note. Since there is a simple mapping between MIDI notes and frequency, these simpler, smaller, integer numbers are easier for us to work with without loosing any information.

HMM Based Difficulties: Old and Busted
--------------------------------------
Our initial plan was to use an HMM-based approach, using a long tail of 16-32 previous observations in each song (MIDI ticks, in our data set) to predict each subsequent set of notes (i.e. the notes being played on each of the three instruments any given time).  While this approach has not been fruitless, we expect it will not be sufficient to produce interesting or, concerning our music problem domain, pleasant sounding results.  While we have not completely given up on this approach, we are, in parallel to generating more training data, also working on a new model.

Dynamic Bayesian Modeling: The New Hotness
------------------------------------------
The new model we’re working on, and the approach we expect we will stick with for the rest of the project, will be a dynamic bayesian approach. Where the HMM model limited us to predicting the note being performed on each of the three channels at each time observation as a fixed set, our new model will allow us to be more sophisticated and the connections between notes played on different channels within the same time observation.

This model will attempt to identify lead melody in the song, and then, at each time observation / MIDI-tick, and predict the notes being played on the background instruments given what the lead instrument is playing.
 One large difficulty with this approach is the question of how to identify which track / instrument in the song is playing the lead melody. It is our understanding that this problem is an ongoing, frontier area of research in automatic music synthesis and digital signal processing. We are considering finding a fundamental solution to this problem beyond the scope of our project. Instead, we plan to rely on a useful-but-imperfect heuristic of how melodies are often laid out in NSF audio, and in NES soundtracks.  Specifically, we plan to treat the first pulse channel as the lead melody, and then to treat the remaining, second pulse track, along with the square wave track, as the background, harmonizing tracks.

This strategy has obvious deficiencies, such as the fact that the main pulse track does not always carry the lead melody, or that many songs include multiple, counter melodies that often do not harmonize the way different instruments in slower genres of music harmonize.  However, even acknowledging these imperfections, we still expect that our Dynamic Bayesian model will do a better job predicting that our previous HMM approach.
