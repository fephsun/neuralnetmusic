import xml.etree.ElementTree as ET
import math
import numpy as np
from PIL import Image
import cPickle

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

def fileToData(path, transpose=0):
    counter = CountingNoteAdder()
    read(path, counter.handle)
    maxLen = int(math.ceil(counter.maxLen / 16) * 16)
    print maxLen
    noteMaker = LegatoNoteAdder(maxLen, transpose)
    read(path, noteMaker.handle)
    outMtx = noteMaker.mtx

    print "Writing outputs"
    windowSize = 4
    nWindows = maxLen / 16 - windowSize
    finalData = np.zeros([nWindows, 88*16*windowSize])
    for i in range(nWindows):
        thisSlice = outMtx[:, i*16:i*16+windowSize*16]
        finalData[i, :] = thisSlice.reshape([88*16*windowSize])
        if i == 1:
            outIm = Image.fromarray(thisSlice.astype('uint8')*255)
            outIm.save('test.png')
    return finalData

def main():
    chorales = [
        './chorales/0408.xml',
        './chorales/0507.xml',
        './chorales/0707.xml',
        './chorales/0806.xml',
        './chorales/0907.xml',
        './chorales/1007.xml',
        './chorales/1207.xml',
        './chorales/1306.xml',
        './chorales/1405.xml',
        './chorales/1606.xml',
        './chorales/1805.xml',
        './chorales/2007.xml',
        './chorales/2506.xml',
        './chorales/2606.xml',
        './chorales/2806.xml',
        './chorales/3006.xml',
        './chorales/3706.xml',
        './chorales/3907.xml',
        './chorales/4003.xml',
        './chorales/4006.xml',
        './chorales/4008.xml',
        './chorales/4207.xml',
        './chorales/4407.xml',
        './chorales/4507.xml',
        './chorales/4803.xml',
        './chorales/4807.xml',
        './chorales/5505.xml',
        './chorales/5605.xml',
        './chorales/6005.xml',
        './chorales/6206.xml',
        './chorales/6408.xml',
        './chorales/6507.xml',
        './chorales/6707.xml',
        './chorales/7206.xml',
        './chorales/7305.xml',
        './chorales/7706.xml',
        './chorales/8107.xml',
        './chorales/9906.xml',
        './chorales/10406.xml',
        './chorales/12406.xml',
        './chorales/13306.xml',
        './chorales/14007.xml',
        './chorales/14406.xml',
        './chorales/30200.xml',
        './chorales/34000.xml',
        './chorales/40100.xml',
    ]

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
        for transpose in range(-6, 6):
            thisData = fileToData(f, transpose)
            if total is None:
                total = thisData
            else:
                total = np.concatenate((total, thisData), axis=0)
    print total.shape
    # cPickle.dump(total, open('test_data.pickle', 'wb'), protocol=cPickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    main()