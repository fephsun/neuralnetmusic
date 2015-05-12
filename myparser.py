import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
import cPickle

continuous = True

def read(filename, outMtx=None, speed=1.0):
    # speed controls how much to expand or contract the piano roll.
    # So, speed=2 will make a quarter note in the xml equal to an
    # eighth note on the piano roll.
    _, maxLen = outMtx.shape
    tree = ET.parse(filename)
    allNotes = tree.getroot()

    beatCounter = {}    # Number of quarter notes.
    lastCounter = 0     # A hack to deal with annoying chord semantics.
    durPer16th = 1.0

    for part in allNotes.iter('part'):
        partId = part.get('id')
        for measure in part.iter('measure'):

            # Attributes are sandwiched in a stupid place.
            attr = measure.find('attributes')
            if attr is not None and attr.findtext('divisions') is not None:
                durPer16th = float(attr.findtext('divisions')) / 4.0

            for note in measure.iter('note'):
                # Get part.
                voice = note.findtext('voice')
                staff = note.findtext('staff')
                if (partId, voice, staff) not in beatCounter:
                    beatCounter[(partId, voice, staff)] = 0
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
                if thisTime == int(thisTime):
                    # Don't log notes that are on a 32nd offbeat.
                    if outMtx is not None:
                        if continuous:
                            for i in range(max(int(dur), 1)):
                                if thisTime + i < maxLen:
                                    outMtx[pitchNum, thisTime + i] = 1
                        else:
                            if thisTime < maxLen:
                                outMtx[pitchNum, thisTime] = 1
                # Deal with chord semantics.
                # In a chord, every note after the first is marked with <chord />
                if not inChord:
                    lastCounter = beatCounter[(partId, voice, staff)]
                    beatCounter[(partId, voice, staff)] += dur

            # At the end of each measure, check for beat length consistency.
            # We only support 4/4 time right now.
            if int(measure.get('number')) * 16 / speed not in beatCounter.values():
                print filename
                print beatCounter
                print measure.get('number')
                assert False

    return outMtx, max(beatCounter.values())

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

def fileToData(path):
    _, length = read(path, None)
    length = int(length / 16) + 1    # Length in measures
    outMtx = np.zeros([88, length*16])
    outMtx, _ = read(path, outMtx)
    print length

    print "Writing outputs"
    windowSize = 4
    nWindows = length - windowSize + 1
    finalData = np.zeros([nWindows, 88*16*windowSize])
    for i in range(nWindows):
        thisSlice = outMtx[:, i*16:i*16+windowSize*16]
        finalData[i, :] = thisSlice.reshape([88*16*windowSize])
        if i == 0:
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
        './chorales/6408.xml',
        './chorales/6507.xml',
        './chorales/6707.xml',
        './chorales/30200.xml',
        './chorales/34000.xml',
        './chorales/40100.xml',
    ]

    total = None
    for f in chorales:
        thisData = fileToData(f)
        if total is None:
            total = thisData
        else:
            total = np.concatenate((total, thisData), axis=0)
    print total.shape
    cPickle.dump(total, open('bach_data2.pickle', 'wb'))

if __name__ == '__main__':
    main()