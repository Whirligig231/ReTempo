# ReTempo

### Automated processing of songs to change rhythms

ReTempo is a Python script that takes in a sound file and alters it, changing rhythms in various ways. Examples include:

* adding (or removing) a swing rhythm;
* removing every other beat;
* switching beats with each other;
* and more!

It does this through the combination of three tools:

* The first is **[BeatRoot](https://code.soundsoftware.ac.uk/projects/beatroot-vamp)**, a [Vamp plugin](https://www.vamp-plugins.org/) that detects beats in music. This is used to give the program an idea of where the beats are.
* The second is **Barry the Choppper**, a custom piece of software that takes audio files and can remove, reverse, and rearrange pieces of an audio file. This is used to apply transformations such as removing every other beat.
* Lastly, **[Rubber Band](https://github.com/breakfastquay/rubberband)** is used to perform stretching and squishing operations on the audio.

At the moment, ReTempo is Windows-only, though the code is probably cross-platform; I simply don't have \*nix executables on hand for its dependencies.

ReTempo is copyright (c) 2024 Whirligig Studios and is released under the GNU GPL v2; see COPYING.txt for more details.

## How to Use

1. Ensure that you have [Python 3](https://www.python.org/downloads/) installed. Any relatively recent version should work.
2. Download ReTempo and place it into a directory.
3. You will need to add the `vamp/` directory within ReTempo to your `VAMP_PATH` environment variable. Alternatively, if you have some Vamp plugins already installed, you can put `vamp/beatroot-vamp.dll` into your Vamp plugins directory (if it's not there already).
4. Convert any music file(s) you want to use to OGG format and place them in the `songs/` directory.
5. Using Python 3, run `retempo.py`.
6. You will first be prompted to enter a song name. Enter any part of the name of one of the music files presented. Filenames are matched by substring checking, so you can enter any substring as long as it is unambiguous. **NOTE:** You may have a little bit of trouble if one file's name is a suffix of another (e.g. `song.ogg` and `mysong.ogg`). In this case, you can use the character `^` at the beginning of your input to indicate that the remainder of your input must be a prefix of the filename instead of a substring. (So in this case, `^song.ogg` would be unambiguous.)
7. ReTempo will use BeatRoot to perform beat detection. It will then ask if you want to override the results and provide a manual tempo. If so, enter Y; you will be prompted for the tempo in BPM and the time of the first beat. If not, enter N.
8. If you said no to manual tempo, you will next be asked if you want the beats to be regularized (i.e. averaged out). This is usually not necessary, but sometimes (especially if songs have quiet sections) BeatRoot can get confused about where a beat is. Enter Y or N as appropriate. **NOTE:** Beat regularization assumes that the song has an unchanging tempo and that its tempo is a multiple of 1 BPM. If these assumptions are not true, it will fail.
9. ReTempo will next print a list of pattern files. As with song files, you should enter a substring of the filename you want.
10. ReTempo will first run Barry the Chopper, then Rubber Band. Each program will provide a percentage progress printout. Note that Rubber Band will probably print a large number of "extreme increment" warnings; it is safe to ignore these, as all it is saying is that this kind of micro-scale tempo changing is unreliable. I have found that it still produces listenable results.
11. The final output will be placed in `OUT.wav`. You can safely ignore or delete `labels.txt`, `TEMP`, and `TEMP.wav`; they are intermediate files. If you want to keep your output, you should copy it elsewhere (and probably rename it, and probably even convert it to a less hefty file format), because `OUT.wav` will be overwritten the next time the script is run.

## But what's a .ret file?

The .ret format is text-based. Each file contains several (x, y) pairs, with a space in each pair and newlines separating them. The individual values can be written as either decimals or fractions. The first pair should always be `0 0`.

A pair (x, y) means: "the time x beats into the output corresponds to the time y beats into the input." Between these pairs, the timeline is interpolated linearly. Consider the following example:

    0 0
	2 1
	2 2
	3 1
	4 2

After a song is processed with this file, first, the first beat will play, but at half tempo (because 2 beats into the output is 1 beat into the input). Then, the playhead immediately skips a beat to be 2 beats into the input. The second beat is played backwards, and then it is played forwards. A total of 4 beats have gone by in the output, but only 2 beats of input have played: the first beat at half speed, then the second beat backwards, then the second beat forwards. This file is available as `readme_example.ret` if you want to try it out.

After the end of a pattern file, the pattern will repeat itself for the remainder of the song's detected beats. So in the above example, after 4 beats of output (2 beats of input) have gone by, the same pattern will be used to produce the next 4 beats, etc.
