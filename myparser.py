import xml.etree.ElementTree as ET
import math
import numpy as np
import subprocess
from PIL import Image
import cPickle
import cStringIO

def read(filename, noteAdder, speed=1.0):
    # speed controls how much to expand or contract the piano roll.
    # So, speed=2 will make a quarter note in the xml equal to an
    # eighth note on the piano roll.
    tree = ET.parse(filename)
    allNotes = tree.getroot()

    beatCounter = {}    # Number of 16th notes.
    lastCounter = 0     # Records the beat of the last thing we processed.
    durPer16th = 1.0    # We read this value from the xml - this is just a default
    beatsPerMeasure=4   # see above

    for part in allNotes.iter('part'):
        partId = part.get('id')
        for measure in part.iter('measure'):
            # SKIP implicit measures.
            if measure.get('implicit') is not None:
                continue

            # Attributes are sandwiched in a stupid place - in any measure.
            # Usually, the first measure will have attributes, but other measures
            # may have more attributes, especially if the attributes change in
            # the middle of a piece (different time signature, etc.).
            attr = measure.find('attributes')
            if attr is not None and attr.findtext('divisions') is not None:
                durPer16th = float(attr.findtext('divisions')) / 4.0
            if attr is not None and attr.findtext('time') is not None:
                timeTree = attr.find('time')
                beatsPerMeasure = int(timeTree.findtext('beats'))
                print str(beatsPerMeasure) + ' beats per measure'

            for note in measure.iter('note'):
                # Get part.
                voice = note.findtext('voice')
                staff = note.findtext('staff')
                if (partId, voice, staff) not in beatCounter:
                    beatCounter[(partId, voice, staff)] = 0
                # In a chord, every note after the first is marked with <chord />
                # Chords need special treatment - you can't increment the beat
                # when in the middle of a chord.
                inChord = (note.find('chord') is not None)

                try:
                    dur = float(note.findtext('duration')) / durPer16th / speed
                except TypeError:
                    # Notes without duration are grace notes.  Skip them.
                    continue
                pitch = note.find('pitch')
                if pitch is None:
                    # rest.
                    beatCounter[(partId, voice, staff)] += dur
                    continue

                # Read off the pitch
                pitchNum = pitchGetter(
                    pitch.findtext('step'),
                    int(pitch.findtext('octave')),
                    int(pitch.findtext('alter', default=0)),
                )

                if inChord:
                    thisTime = lastCounter
                else:
                    thisTime = beatCounter[(partId, voice, staff)]
                noteAdder(thisTime, pitchNum, dur)
                # Deal with chord semantics.
                if not inChord:
                    lastCounter = beatCounter[(partId, voice, staff)]
                    beatCounter[(partId, voice, staff)] += dur

            # At the end of each measure, check for beat length consistency.
            # Sometimes, music will put three beats in a 4/4 measure.  In that
            # case, we crash.  You should go into the piece and fix the problem
            # manually, before re-running.
            if int(measure.get('number')) * 4 * beatsPerMeasure / speed \
                != beatCounter[(partId, voice, staff)]:
                print filename
                print beatCounter
                print (partId, voice, staff)
                print measure.get('number')
                assert False

# Counts the number of ticks in the music.  (Ticks = 16th notes, unless you
# change that setting.)
class CountingNoteAdder(object):
    def __init__(self):
        self.maxLen = 0

    def handle(self, time, pitch, dur):
        self.maxLen = max(self.maxLen, time + dur)

class LegatoNoteAdder(object):
    def __init__(self, maxLen, transpose=0):
        self.maxLen = maxLen
        self.mtx = np.zeros([88, maxLen])
        self.transpose = transpose

    def handle(self, time, pitch, dur):
        if time != int(time):
            return
        rounded_dur = math.ceil(dur)
        if time + rounded_dur >= self.maxLen:
            return
        self.mtx[pitch + self.transpose, time:time+rounded_dur] = 1

def pitchGetter(letter, octave, offset):
    basePitch = {
        'C': 0,
        'D': 2,
        'E': 4,
        'F': 5,
        'G': 7,
        'A': 9,
        'B': 11,
    }
    return octave * 12 + offset + basePitch[letter]

def fileToData(path, transpose=0, windowSize=4):
    counter = CountingNoteAdder()
    read(path, counter.handle)
    maxLen = int(math.ceil(counter.maxLen / 16) * 16)
    print maxLen
    noteMaker = LegatoNoteAdder(maxLen, transpose)
    read(path, noteMaker.handle)
    outMtx = noteMaker.mtx

    print "Writing outputs"
    nWindows = maxLen / 16 - windowSize
    finalData = np.zeros([nWindows, 88*16*windowSize])
    for i in range(nWindows):
        thisSlice = outMtx[:, i*16:i*16+windowSize*16]
        finalData[i, :] = thisSlice.reshape([88*16*windowSize])
        if i == 1:
            outIm = Image.fromarray(thisSlice.astype('uint8')*255)
            outIm.save('test.png')
    return finalData

def fileToSerialData(path):
    counter = CountingNoteAdder()
    read(path, counter.handle)
    maxLen = int(math.ceil(counter.maxLen / 64) * 64)
    print maxLen
    noteMaker = LegatoNoteAdder(maxLen, 0)
    read(path, noteMaker.handle)
    return noteMaker.mtx    

def main():
    joplin = [
        './joplin/searchlight.xml',
        './joplin/strenous.xml',
        './joplin/maple_leaf.xml',
        './joplin/entertainer.xml',
        './joplin/syncopations.xml',
        './joplin/cleopha.xml',
        './joplin/winners.xml',
        './joplin/winners_2.xml',
        './joplin/alabama.xml',
    ]

    total = None
    for f in joplin:
        # You can transpose all the music to multiple keys, to increase the amount
        # of training data.  But, this makes training much slower and harder.  (Right
        # now, everything is in C major.)
        for transpose in range(1):
            thisData = fileToData(f, transpose)
            if total is None:
                total = thisData
            else:
                total = np.concatenate((total, thisData), axis=0)
    print "Average notes per column:"
    print np.sum(total) / total.shape[0] / 64
    cPickle.dump(total, open('test_data.pickle', 'wb'), protocol=cPickle.HIGHEST_PROTOCOL)

def make_kaldi(filename, offset):
    joplin = [
        './joplin/searchlight.xml',
        './joplin/strenous.xml',
        './joplin/maple_leaf.xml',
        './joplin/entertainer.xml',
        './joplin/syncopations.xml',
        './joplin/cleopha.xml',
        './joplin/winners.xml',
        './joplin/winners_2.xml',
        './joplin/alabama.xml',
    ]
    total = None
    totalOut = ''
    count_file = open(filename + '.counts', 'wb')
    for f in joplin:
        if offset > 0:
            thisData = fileToSerialData(f)[:, :-offset]
            thisData = np.concatenate((np.zeros((88, offset)), thisData), axis=1)
        else:
            thisData = fileToSerialData(f)
        f_safe = ''.join(filter(str.isalnum, f))
        count_file.write(f_safe + ' ' + str(thisData.shape[1]) + '\n')

        stringio = cStringIO.StringIO()
        np.savetxt(stringio, thisData.T, fmt='%.2f')
        totalOut = totalOut + f_safe + ' [ ' + stringio.getvalue() + ' ]\n'
    count_file.close()

    outFile = open(filename + '.txt', 'wb')
    outFile.write(totalOut)
    outFile.close()

    scpFile = open(filename + '.feats', 'wb')
    scpFile.write('scp:{0}.scp\n'.format(filename))
    scpFile.close()

    subprocess.call('../kaldi/src/featbin/copy-feats --compress ' +
        'ark:{0}.txt ark,scp:$PWD/{0}.ark,{0}.scp'
        .format(filename), shell=True)

def make_keras():
    data = {}
    joplin = [
        './joplin/searchlight.xml',
        './joplin/strenous.xml',
        './joplin/maple_leaf.xml',
        './joplin/entertainer.xml',
        './joplin/syncopations.xml',
        './joplin/cleopha.xml',
        './joplin/winners.xml',
        './joplin/winners_2.xml',
        './joplin/alabama.xml',
    ]
    for f in joplin:
        data[f] = fileToSerialData(f)
    cPickle.dump(data, open('keras_data.pickle', 'wb'), protocol=cPickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    # make_kaldi('in_feats', 0)
    make_keras()
