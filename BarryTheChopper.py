import soundfile
import math

TRANSITION = 500

def getSampleRate(fname):
    data, samplerate = soundfile.read(fname)
    return samplerate
    
# N.B. MUST use .wav for output, as .ogg output is broken in the library!
def chop(fname, ofname, chops):
    print('BARRY THE CHOPPER')
    print('Reading sound file ...')
    data, samplerate = soundfile.read(fname)
    outdata = []
    transition_loc = None
    transition_direction = None
    print('Chopping ...')
    for i in range(len(chops)):
        chop = chops[i]
        pct = int(i*100/len(chops))
        print('\r' + str(pct) + '% ', end=' ')
        if chop[1] == 0:
            continue
        for i in range(abs(chop[1])):
            sample = None
            if chop[1] >= 0:
                sample = data[chop[0]+i]
            else:
                sample = data[chop[0]-i]
            if transition_loc is not None and i < TRANSITION:
                sample = sample.copy()
                sample *= i / TRANSITION
                oldsample = data[transition_loc+i*transition_direction].copy()
                oldsample *= 1 - i / TRANSITION
                sample += oldsample
            outdata += [sample]
        transition_loc = chop[0] + chop[1]
        transition_direction = (1 if chop[1] >= 0 else -1)
        if (transition_loc < TRANSITION and transition_direction == -1) or (transition_loc > len(data) - TRANSITION and transition_direction == 1):
            transition_loc = None
            transition_direction = None
    print('\rWriting sound file ...')
    soundfile.write(ofname, outdata, samplerate)