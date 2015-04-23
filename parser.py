import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
import cPickle

def read(filename, outMtx=None):
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
                    dur = float(note.findtext('duration')) / durPer16th
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
                        for i in range(max(int(dur), 1)):
                            outMtx[pitchNum, thisTime + i] = 1

                # Deal with chord semantics.
                # In a chord, every note after the first is marked with <chord />
                if not inChord:
                    lastCounter = beatCounter[(partId, voice, staff)]
                    beatCounter[(partId, voice, staff)] += dur

            # At the end of each measure, check for beat length consistency.
            # We only support 4/4 time right now.
            if int(measure.get('number')) * 16 not in beatCounter.values():
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
    minor = [
        './chorales/0408.xml',
        './chorales/0507.xml',
        './chorales/0707.xml',
        './chorales/1007.xml',
        './chorales/1405.xml',
        './chorales/1606.xml',
        './chorales/1805.xml',
        './chorales/2606.xml',
        './chorales/2806.xml',
    ]
    major = [
        './chorales/0806.xml',
        './chorales/0907.xml',
        './chorales/1207.xml',
        './chorales/1306.xml',
        './chorales/2007.xml',
        './chorales/2506.xml',
        './chorales/3006.xml',
        './chorales/30200.xml',
        './chorales/34000.xml',
        './chorales/40100.xml',
    ]

    mozart = [
        './training/k545.xml'
    ]

    total = None
    for f in minor + major + mozart:
        thisData = fileToData(f)
        if total is None:
            total = thisData
        else:
            total = np.concatenate((total, thisData), axis=0)
    print total.shape
    cPickle.dump(total, open('bach_data.pickle', 'wb'))

main()