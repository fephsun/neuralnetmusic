//=============================================================================
//  HalfTime plugin
//
//  This plugin created by underquark July 2012
//  It is a shamelessly modified version of a plugin created by lasconic called "Retrograde"


function init()
{
}


function addChord(cursor, duration)
{
      var chord     = new Chord();
      chord.tickLen = duration;
      cursor.add(chord);
      cursor.next();
      return chord;
}

function addNote(chord, pitch)
{
      var note      = new Note();
      note.pitch    = pitch;
      chord.addNote(note);
}

function addRest(cursor, duration)
{
     var rest = new Rest();
     rest.tickLen = duration;
     cursor.add(rest);
     cursor.next();
}

function run()
{
      if (typeof curScore === 'undefined')	
            return; 
      var chordArray = [];
      var cursor       = new Cursor(curScore);
      var selectionEnd = new Cursor(curScore);

      cursor.goToSelectionStart();
      selectionEnd.goToSelectionEnd();
      var startStaff = cursor.staff;
      var endStaff   = selectionEnd.staff;

      for (var staff = startStaff; staff < endStaff; ++staff)
      {
            cursor.goToSelectionStart();
            cursor.voice = 0;
            cursor.staff = staff;
            
            while (cursor.tick() < selectionEnd.tick())
            {
                if (cursor.isChord())
                {
                      var chord = cursor.chord();
                      chordArray.push(chord);
                } else if (cursor.isRest())
                {
                      var rest = cursor.rest();                    
                      chordArray.push(rest.tickLen);
                }
                cursor.next();
            }    
      }
            
      var score   = new Score();
      score.name  = "DoubleTime";
      score.title = "DoubleTime";
	   score.appendPart();
      score.keysig = curScore.keysig;
		score.appendMeasures(200);
      var newCursor = new Cursor(score);
      newCursor.staff = 0;
      newCursor.voice = 0;
      newCursor.rewind();
      
      for (var i = 0; i<chordArray.length; i++)
      {
            var chord = chordArray[i];
            if (typeof chord === 'object')
            {
                var newChord = addChord(newCursor, chord.tickLen * 2);
                var n     = chord.notes;
                for (var j = 0; j < n; j++)
					{
                      var note = chord.note(j);
                      addNote(newChord, note.pitch);
               }
            } else
            {
                //add rest if it's not a chord
                var tickLen = chord;
                addRest(newCursor, tickLen * 2);
            }
      }

}

var mscorePlugin =
{
      menu: 'Plugins.DoubleTime',
      init: init,
      run:  run
}

mscorePlugin;
