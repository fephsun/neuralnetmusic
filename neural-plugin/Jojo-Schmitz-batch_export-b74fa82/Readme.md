This Plugin for MuseScore will go through a specified folder and in its default settings exports PDF versions of all ".mscz" files for which no up-to-date version already exists. To use the plugin, you must first install it according to the instructions in [the 1.x Handbook](http://musescore.org/en/en/node/10129), or the [2.x Handbook](http://musescore.org/en/node/36051), then:

1. Select "Batch Export" from the Plugins menu
2. Select the in- and output format(s), or just use the default (\*.mscz to \*.pdf)
3. Decide whether or nor you want to also work on subdirectories of the one you'll select in the next step and check/uncheck the corresponding box
4. Browse to the folder containing the files you wish to export
5. Select "Choose"
6. Confirm the dialog box that shows which files have been converted

A couple of notes to be aware of:

- You may need to have a score already open in order for the Plugins menu to be active. Fixed in MuseScore 2.0+
- In MuseScore 2.0.1+ make sure you don't have a score open, that you want the plugin to process, because it won't be able to load it then.
- The scores for which files were exported may be left open in tabs. If so, you'd need to close them manually. Fixed with MuseScore 1.2+
- These open tabs will be labeled "untitled". Fixed in MuseScore 2.0+ and not an issue anymore with MuseScore 1.2+, see above
- The 2.0 version of this plugin needs at least 2.0.1
- If you're on MacOS X and the file dialog for step 4 does not show up, try using the Mac version of the plugin which is in the branch 'mac'.
- All files processed by the plugin for MuseScore 2.0+ will be listed in the 'Recent File' menu.

These issues are fixed with the above mentioned versions, and without re-installing the plugin.

This plugin now comes with translations of the dialogs into German, French (thanks to lasconic) and Spanish (thanks to jorgk), for all other language settings in MuseScore, it remains English. More translations are welcome, just contact us for including them.

The idea for this plugin stems from a [question in the forum](https://musescore.org/en/node/12452). See also [this discussion about the 2.0 version](https://musescore.org/en/node/55616)
