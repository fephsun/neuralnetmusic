//=============================================================================
//  MuseScore
//  Linux Music Score Editor
//  $Id:$
//
//  Test plugin
//
//  Copyright (C)2009 Werner Schweer and others
//
//  This program is free software; you can redistribute it and/or modify
//  it under the terms of the GNU General Public License version 2.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program; if not, write to the Free Software
//  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
//=============================================================================


//
// error handling is mostly omitted!
//

//---------------------------------------------------------
//    init
//---------------------------------------------------------

function init() {
    };

var form;
var projectRoot = 'C:\\Users\\Felix\\Documents\\21M.359\\Final Project\\';
var tempLoc = 'C:\\Users\\Felix\\Documents\\21M.359\\Final Project\\temp\\';

function copyChord(oldChord) {
    var chord = new Chord();
    chord.tickLen = oldChord.tickLen;
    for (var i = 0; i < oldChord.notes; i++) {
        var note = new Note();
        note.pitch = oldChord.note(i).pitch;
        note.tied = oldChord.note(i).tied;
        chord.addNote(note);
    }
    return chord
}

function copyThing(source, target) {
    if (source.isChord()) {
        target.add(copyChord(source.chord()));
        target.next();
    } else if (source.isRest()) {
        var newRest = new Rest();
        newRest.tickLen = source.rest().tickLen;
        target.add(newRest);
        target.next();
    }
    source.next();
}

function run() {
    // Get user settings via dialog box.
    var loader = new QUiLoader(null);
    var file   = new QFile(pluginPath + "/neural-plugin.ui");
    file.open(QIODevice.OpenMode(QIODevice.ReadOnly, QIODevice.Text));
    form = loader.load(file, null);
    form.buttonBox.accepted.connect(accept);
    form.learnRateBox.setText("0.05");
    form.nIterBox.setText("200");
    form.thresholdBox.setText("0.6");
    form.show();
};

//---------------------------------------------------------
//    accept
//    called when user presses "Accept" button
//---------------------------------------------------------

function accept() {
    
    // Read off some notes, starting from where the cursor is.
    // Set up cursors for reading the score.
    var origScore = curScore;
    var cursor = new Cursor(origScore);
    var selectionEnd = new Cursor(origScore);
    selectionEnd.goToSelectionEnd();
    cursor.goToSelectionStart();

    var startStaff = cursor.staff;
    var endStaff = selectionEnd.staff;
    cursor.voice = 0;
    var tempScore = new Score();
    tempScore.appendPart();
    tempScore.appendPart();
    tempScore.appendPart();
    tempScore.appendMeasures(8);  // Fix me.
    tempScore.keysig = origScore.keysig;
    var writeCursor = new Cursor(tempScore);
    writeCursor.staff = 0;
    writeCursor.voice = 0;
    writeCursor.rewind();

    // Right now, we read the first voice from each staff.
    // Maybe change this in the future to multi-voice?
    for (var staff = startStaff; staff < endStaff; staff++) {
        cursor.goToSelectionStart();
        cursor.staff = staff;
        writeCursor.rewind();
        while (cursor.tick() < selectionEnd.tick()) {
            copyThing(cursor, writeCursor);
        }
        // tempScore.appendPart()
        writeCursor.staff += 1;
        writeCursor.voice = 0;
    }
    // Save, load, save.  Because musescore is buggy and can't save xml directly.
    tempScore.save(tempLoc + 'test.mscz', 'mscz')
    tempScore.close()

    tempScore = new Score();
    tempScore.load(tempLoc + 'test.mscz')
    tempScore.save(tempLoc + 'test.xml', 'xml')
    tempScore.close()

    // Run the neural net via qprocess.
    var process = new QProcess();
    process.setStandardOutputFile(tempLoc + "stdout.txt");
    process.setStandardErrorFile(tempLoc + "stderr.txt");
    var args = new Array();
    args[0] = projectRoot + 'DBN.py';
    args[1] = tempLoc + 'test.xml';
    args[2] = form.learnRateBox.text;
    args[3] = form.nIterBox.text;
    args[4] = form.thresholdBox.text;
    process.start('python', args);
    process.waitForStarted();
    process.waitForFinished();

    // Load the result.
    tempScore = new Score();
    tempScore.load(projectRoot + 'test.midi');
    tempScore.save(projectRoot + 'test.mscz', 'mscz');
    tempScore.close();
    tempScore = new Score();
    tempScore.load(projectRoot + 'test.mscz');
    cursor.goToSelectionStart();
    while (origScore.staves < 2) {
        origScore.appendPart();
    }
    var loader = new QUiLoader(null);
    var file   = new QFile(pluginPath + "/output-window.ui");
    file.open(QIODevice.OpenMode(QIODevice.ReadOnly, QIODevice.Text));
    outForm = loader.load(file, null);
    var scoreFile = new QFile(tempLoc + "stdout.txt");
    scoreFile.open(QIODevice.OpenMode(QIODevice.ReadOnly, QIODevice.Text));
    outForm.textOut.setText(scoreFile.readAll());
    outForm.show();
}

var mscorePlugin = {
    menu: 'Plugins.Neural Autocomplete',
    init: init,
    run:  run
    };

mscorePlugin;

