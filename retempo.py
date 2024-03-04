import os, sys, math

import BarryTheChopper

def floatX(s):
    if '/' in s:
        ss = s.split('/')
        return float(ss[0]) / float(ss[1])
    else:
        return float(s)

def pickFromList(ls, prompt):
    while True:
        pick = input(prompt)
        possible = [p for p in ls if pick.rstrip() in ('^'+p)]
        if len(possible) == 0:
            print('Not found!')
        elif len(possible) > 1:
            print('Multiple possibilities:', possible)
        else:
            print(possible[0])
            return possible[0]

def LI(array, index):
    if index == int(index):
        return array[int(index)]
    index0 = int(index)
    index1 = index0 + 1
    frac = index - index0
    return array[index0] * (1 - frac) + array[index1] * frac

fnames = [f for f in os.listdir('./songs') if f.endswith('.wav') or f.endswith('.ogg') or f.endswith('.flac')]

print('\nMUSIC FILES FOUND:')
for f in fnames:
    print(f)
print('---\n')

fname = pickFromList(fnames, 'Input song filename: ')

os.system('vamp\\VampSimpleHost.exe beatroot-vamp:beatroot "songs\\' + fname + '" -o TEMP')

beats = []
fp = open('TEMP', 'r')
for line in fp:
    beats += [float(line.strip().strip(':'))*44100]
fp.close()
    
# Sometimes the algorithm completely fails, and you have to do this the hard way
if 'y' in input('Manual tempo? (Y/N) ').lower():
    bpm = float(input('Enter tempo (BPM): '))
    offsecs = float(input('Enter offset (s): '))
    guessbeat = 44100*60/bpm
    guessoffset = offsecs*44100/guessbeat
    
    # Create a new beat list
    newbeats = []
    beattime = guessoffset * guessbeat
    while beattime < beats[-1]:
        newbeats += [beattime]
        beattime += guessbeat
    beats = newbeats
else:
    # Optional: beat regularization
    # Works only for tracks where tempo is a multiple of 1 BPM and never changes
    if 'y' in input('Use beat regularization? (Y/N) ').lower():
        beatdiffs = [beats[i+1]-beats[i] for i in range(len(beats)-1)]
        
        # Take the average of the 20th through 80th percentile for beat length
        beatdiffs.sort()
        beatdiffs = beatdiffs[int(len(beatdiffs)*0.2):int(len(beatdiffs)*0.8)]
        avgbeat = sum(beatdiffs)/len(beatdiffs)
        avgtempo = 44100*60/avgbeat
        guesstempo = int(avgtempo+0.5)
        guessbeat = 44100*60/guesstempo
        print('Detected tempo is', avgtempo, 'BPM; guessing actual tempo is', guesstempo, 'BPM')
        
        # Figure out the offset using circular mean
        goodbeats = [beats[i] for i in range(1, len(beats)-1) if beats[i+1]-beats[i] in beatdiffs and beats[i]-beats[i-1] in beatdiffs]
        offsets = [math.modf(beat / guessbeat)[0] for beat in goodbeats]
        xs = [math.cos(offset*2*math.pi) for offset in offsets]
        ys = [math.sin(offset*2*math.pi) for offset in offsets]
        xm = sum(xs)/len(xs)
        ym = sum(ys)/len(ys)
        guessoffset = math.atan2(ym, xm)/2/math.pi
        if guessoffset < 0:
            guessoffset += 1
        accordance = math.sqrt(xm*xm + ym*ym)
        print('Detected offset is', str(guessoffset*100) + '%, accordance is', str(accordance*100) + '%')
        
        # Create a new beat list
        newbeats = []
        beattime = guessoffset * guessbeat
        while beattime < beats[-1]:
            newbeats += [beattime]
            beattime += guessbeat
        beats = newbeats

fp = open('labels.txt', 'w+')
for beat in beats:
    fp.write(str(beat/44100) + '\t' + str(beat/44100) + '\t' + 'BEAT\n')
fp.close()

# BEGIN THE CHOPPING!
pnames = [f for f in os.listdir('./patterns') if f.endswith('.ret')]

print('\nPATTERN FILES FOUND:')
for f in pnames:
    print(f)
print('---\n')

pname = pickFromList(pnames, 'Input pattern filename: ')
fp = open('patterns\\' + pname, 'r')
pattern = []
for line in fp:
    words = line.strip().split(' ')
    if len(words) < 2:
        continue
    pattern += [[floatX(words[0]), floatX(words[1])]]
fp.close()

pieces = []
pattern_ind = 0
beat_offset = 0
while True:
    x0 = pattern[pattern_ind][0]
    y0 = pattern[pattern_ind][1]
    x1 = pattern[pattern_ind+1][0]
    y1 = pattern[pattern_ind+1][1]
    if x0 < x1 - 0.0001: # Epsilon to prevent any weird float issues
        start_beats = beat_offset + y0
        end_beats = beat_offset + y1
        if start_beats > len(beats)-1 or end_beats > len(beats)-1:
            break # That's all we can process
        slope = (y1 - y0)/(x1 - x0)
        start_samples = LI(beats, start_beats)
        end_samples = LI(beats, end_beats)
        len_samples = end_samples - start_samples
        pieces += [{'start': start_samples, 'length': len_samples, 'speed': abs(slope)}]
    pattern_ind += 1
    if pattern_ind == len(pattern) - 1:
        beat_offset += y1
        pattern_ind = 0

chops = [[int(piece['start'] + 0.5), int(piece['length'] + 0.5)] for piece in pieces]
BarryTheChopper.chop('songs\\' + fname, 'TEMP.wav', chops)

# Figure out what sample each chop starts at in practice
total_samples = 0
for piece in pieces:
    piece['real_length'] = abs(int(piece['length'] + 0.5))
    piece['real_start'] = total_samples
    total_samples += piece['real_length']

# Run rubberband, but factor out the total ratio!
out_time = 0
for piece in pieces:
    out_time += piece['real_length'] / piece['speed']
total_ratio = out_time / total_samples

fp = open('TEMP', 'w+')
out_time = 0
for piece in pieces:
    in_time = piece['real_start']
    fp.write(str(in_time) + ' ' + str(out_time) + '\n')
    out_time += piece['real_length'] / piece['speed']
fp.write(str(total_samples) + ' ' + str(out_time) + '\n')
fp.close()

os.system('rubberband\\rubberband.exe -t ' + str(total_ratio) + ' -M TEMP TEMP.wav OUT.wav')