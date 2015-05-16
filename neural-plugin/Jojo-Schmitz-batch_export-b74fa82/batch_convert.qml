import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Dialogs 1.2 // FileDialog
import QtQuick.Window 2.2
import Qt.labs.folderlistmodel 2.1
import Qt.labs.settings 1.0
import QtQml 2.2
import MuseScore 1.0
import FileIO 1.0

MuseScore {
  menuPath: "Plugins." + qsTr("Batch Convert")
  version: "2.0"
  description: qsTr("This plugin converts mutiple files from various formats"
    + " into various formats")

  MessageDialog {
    id: versionError
    visible: false
    title: qsTr("Unsupported MuseScore Version")
    text: qsTr("This plugin does not work in MuseScore v2.0.0")
    onAccepted: {
      Qt.quit()
      }
    }

  onRun: {
    // check MuseScore version
    if (mscoreMajorVersion == 2 && mscoreMinorVersion == 0
      && mscoreUpdateVersion == 0) {
      window.visible = false
      versionError.open()
      }
    }

  Window {
    id: window
    visible: true
    title: qsTr("Choose Formats")
    modality: Qt.ApplicationModal // behave like a dialog
    color: "lightgrey"

    // center on screen
    width: mainRow.childrenRect.width
    height: mainRow.childrenRect.height
    x: Screen.width / 2  - width / 2
    y: Screen.height / 2 - height / 2

    // Mutally exclusive in/out formats, doesn't work properly
    ExclusiveGroup { id: mscz }
    ExclusiveGroup { id: mscx }
    ExclusiveGroup { id: xml }
    ExclusiveGroup { id: mxl }
    ExclusiveGroup { id: mid }
    ExclusiveGroup { id: pdf }

    RowLayout {
      id: mainRow
      GroupBox {
        id: inFormats
        title: " " + qsTr("Input Formats") + " "
        Layout.alignment: Qt.AlignTop | Qt.AlignLeft
        //flat: true // no effect?!
        //checkable: true // no effect?!
        property var extensions: new Array()
        Column {
          spacing: 1
          CheckBox {
            id: inMscz
            text: "*.mscz"
            checked: true
            //exclusiveGroup: mscz  // doesn't work?!
            onClicked: {
              if (checked && outMscz.checked)
                outMscz.checked = false
              }
            }
          CheckBox {
            id: inMscx
            text: "*.mscx"
            //exclusiveGroup: mscx
            onClicked: {
              if (checked && outMscx.checked)
                outMscx.checked = false
              }
            }
          CheckBox {
            id: inMsc
            text: "*.msc"
            enabled: false // MuseScore < 2.0
            visible: enabled // hide if not enabled
            }
          CheckBox {
            id: inXml
            text: "*.xml"
            //exclusiveGroup: xml
            onClicked: {
              if (checked && outMscz.checked)
                outXml.checked = !checked
              }
            }
          CheckBox {
            id: inMxl
            text: "*.mxl"
            //exclusiveGroup: mxl
            onClicked: {
              if (checked && outMxl.checked)
                outMxl.checked = false
              }
            }
          CheckBox {
            id: inMid
            text: "*.mid"
            //exclusiveGroup: mid
            onClicked: {
              if (checked && outMid.checked)
              outMid.checked = false
              }
            }
          CheckBox {
            id: inPdf
            text: "*.pdf"
            enabled: false // needs OMR, MuseScore > 2.0?
            visible: enabled // hide if not enabled
            //exclusiveGroup: pdf
            onClicked: {
              if (checked && outPdf.checked)
                outPdf.checked = false
              }
            }
          CheckBox {
            id: inMidi
            text: "*.midi"
            }
          CheckBox {
            id: inKar
            text: "*.kar"
            }
          CheckBox {
            id: inCap
            text: "*.cap"
            }
          CheckBox {
            id: inCapx
            text: "*.capx"
            }
          CheckBox {
            id: inBww
            text: "*.bww"
            }
          CheckBox {
            id: inMgu
            text: "*.mgu"
            }
          CheckBox {
            id: inSgu
            text: "*.sgu"
            }
          CheckBox {
            id: inOve
            text: "*.ove"
            }
          CheckBox {
            id: inScw
            text: "*.scw"
            }
          CheckBox {
            id: inGTP
            text: "*.GTP"
            }
          CheckBox {
            id: inGP3
            text: "*.GP3"
            }
          CheckBox {
            id: inGP4
            text: "*.GP4"
            }
          CheckBox {
            id: inGP5
            text: "*.GP5"
            }
          } // Column
        } // inFormats
      ColumnLayout {
        Layout.alignment: Qt.AlignTop | Qt.AlignRight
        RowLayout {
          Label {
            text: " ===> "
            Layout.fillWidth: true // left align (?!)
            }
          GroupBox {
            id: outFormats
            title: " " + qsTr("Output Formats") + " "
            property var extensions: new Array()
            Column {
              spacing: 1
              CheckBox {
                id: outMscz
                text: "*.mscz"
                //exclusiveGroup: mscz
                onClicked: {
                  if (checked && inMscz.checked)
                    inMscz.checked = false
                  }
                }
              CheckBox {
                id: outMscx
                text: "*.mscx"
                //exclusiveGroup: mscx
                onClicked: {
                  if (checked && inMscx.checked)
                    inMscx.checked = false
                  }
                }
              CheckBox {
                id: outXml
                text: "*.xml"
                //exclusiveGroup: xml
                onClicked: {
                  if (checked && inXml.checked)
                    inXml.checked = false
                  }
                }
              CheckBox {
                id: outMxl
                text: "*.mxl"
                //exclusiveGroup: mxl
                onClicked: {
                  if (checked && inMxl.checked)
                    inMxl.checked = false
                  }
                }
              CheckBox {
                id: outMid
                text: "*.mid"
                //exclusiveGroup: mid
                onClicked: {
                  if (checked && inMid.checked)
                    inMid.checked = false
                  }
                }
              CheckBox {
                id: outPdf
                text: "*.pdf"
                checked: true
                //exclusiveGroup: pdf
                onClicked: {
                  if (checked && inPdf.checked)
                    inPdf.checked = false
                  }
                }
              CheckBox {
                id: outPs
                text: "*.ps"
                }
              CheckBox {
                id: outPng
                text: "*.png"
                }
              CheckBox {
                id: outSvg
                text: "*.svg"
                }
              CheckBox {
                id: outLy
                text: "*.ly"
                enabled: false // MuseScore < 2.0, or via xml2ly?
                visible: enabled //  hide if not enabled
                }
              CheckBox {
                id: outWav
                text: "*.wav"
                }
              CheckBox {
                id: outFlac
                text: "*.flac"
                }
              CheckBox {
                id: outOgg
                text: "*.ogg"
                }
              CheckBox { // needs lame_enc.dll
                id: outMp3
                text: "*.mp3"
                }
              } //Column
            } //outFormats
          } // RowLayout
        CheckBox {
          id: exportExcerpts
          text: qsTr("Export linked parts")
          } // exportExcerpts
        CheckBox {
          id: traverseSubdirs
          text: qsTr("Process\nSubdirectories")
          } // traverseSubdirs
        Button {
          id: reset
          text: qsTr("Reset to Defaults")
          onClicked: {
            resetDefaults()
            } // onClicked
          } // reset
        GroupBox {
          id: cancelOk
          Layout.alignment: Qt.AlignBottom | Qt.AlignRight
          Row {
            Button {
              id: ok
              text: qsTr("Ok")
              //isDefault: true // needs more work
              onClicked: {
                window.visible = false
                if (collectInOutFormats())
                  fileDialog.open()
                } // onClicked
              } // ok
            Button {
              id: cancel
              text: qsTr("Cancel")
              onClicked: {
                window.visible = false
                Qt.quit()
                }
              } // Cancel
            } // Row
          } // cancelOk
        } // ColumnLayout
      } // RowLayout
    } // Window

  // remember settings
  Settings {
    category: "BatchConvertPlugin"
    // in options
    property alias inMscz:  inMscz.checked
    property alias inMscx:  inMscx.checked
    property alias inMsc:   inMsc.checked
    property alias inXml:   inXml.checked
    property alias inMxl:   inMxl.checked
    property alias inMid:   inMid.checked
    property alias inPdf:   inPdf.checked
    property alias inMidi:  inMidi.checked
    property alias inKar:   inKar.checked
    property alias inCap:   inCap.checked
    property alias inCapx:  inCapx.checked
    property alias inBww:   inBww.checked
    property alias inMgu:   inMgu.checked
    property alias inSgu:   inSgu.checked
    property alias inOve:   inOve.checked
    property alias inScw:   inScw.checked
    property alias inGTP:   inGTP.checked
    property alias inGTP3:  inGP3.checked
    property alias inGTP4:  inGP4.checked
    property alias inGTP5:  inGP5.checked
    // out options
    property alias outMscz: outMscz.checked
    property alias outMscx: outMscx.checked
    property alias outXml:  outXml.checked
    property alias outMxl:  outMxl.checked
    property alias outMid:  outMid.checked
    property alias outPdf:  outPdf.checked
    property alias outPs:   outPs.checked
    property alias outPng:  outPng.checked
    property alias outSvg:  outSvg.checked
    property alias outLy:   outLy.checked
    property alias outWav:  outWav.checked
    property alias outFlac: outFlac.checked
    property alias outOgg:  outOgg.checked
    property alias outMp3:  outMp3.checked
    // other options
    property alias exportE: exportExcerpts.checked
    property alias travers: traverseSubdirs.checked
    }

  FileDialog {
    id: fileDialog
    title: traverseSubdirs.checked?
      qsTr("Select Startfolder"):
      qsTr("Select Folder")
    selectFolder: true
    onAccepted: {
      work(folder, traverseSubdirs.checked)
      }
    onRejected: {
      console.log(qsTr("No folder selected"))
      Qt.quit()
      }
    } // fileDialog

  function resetDefaults() {
    inMscx.checked = inXml.checked = inMxl.checked = inMid.checked =
      inPdf.checked = inMidi.checked = inKar.checked = inCap.checked =
      inCapx.checked = inBww.checked = inMgu.checked = inSgu.checked =
      inOve.checked = inScw.checked = inGTP.checked = inGP3.checked =
      inGP4.checked = inGP5.checked = false
    outMscz.checked = outMscx.checked = outXml.checked = outMxl.checked =
      outMid.checked = outPdf.checked = outPs.checked = outPng.checked =
      outSvg.checked = outLy.checked = outWav.checked = outFlac.checked =
      outOgg.checked = outMp3.checked = false
    traverseSubdirs.checked = false
    exportExcerpts.checked = false
    // 'uncheck' everything, then 'check' the next few
    inMscz.checked = outPdf.checked = true
    } // resetDefaults

  function collectInOutFormats() {
    if (inMscz.checked) inFormats.extensions.push("mscz")
    if (inMscx.checked) inFormats.extensions.push("mscx")
    if (inXml.checked)  inFormats.extensions.push("xml")
    if (inMxl.checked)  inFormats.extensions.push("mxl")
    if (inMid.checked)  inFormats.extensions.push("mid")
    if (inPdf.checked)  inFormats.extensions.push("pdf")
    if (inMidi.checked) inFormats.extensions.push("midi")
    if (inKar.checked)  inFormats.extensions.push("kar")
    if (inCap.checked)  inFormats.extensions.push("cap")
    if (inCapx.checked) inFormats.extensions.push("capx")
    if (inBww.checked)  inFormats.extensions.push("bww")
    if (inMgu.checked)  inFormats.extensions.push("mgu", "MGU")
    if (inSgu.checked)  inFormats.extensions.push("sgu", "SGU")
    if (inOve.checked)  inFormats.extensions.push("ove")
    if (inScw.checked)  inFormats.extensions.push("scw")
    if (inGTP.checked)  inFormats.extensions.push("GTP")
    if (inGP3.checked)  inFormats.extensions.push("GP3")
    if (inGP4.checked)  inFormats.extensions.push("GP4")
    if (inGP5.checked)  inFormats.extensions.push("GP5")
    if (!inFormats.extensions.length)
      console.log("No input format selected")

    if (outMscz.checked) outFormats.extensions.push("mscz")
    if (outMscx.checked) outFormats.extensions.push("mscx")
    if (outXml.checked)  outFormats.extensions.push("xml")
    if (outMxl.checked)  outFormats.extensions.push("mxl")
    if (outMid.checked)  outFormats.extensions.push("mid")
    if (outPdf.checked)  outFormats.extensions.push("pdf")
    if (outPs.checked)   outFormats.extensions.push("ps")
    if (outPng.checked)  outFormats.extensions.push("png")
    if (outSvg.checked)  outFormats.extensions.push("svg")
    if (outLy.checked)   outFormats.extensions.push("ly")
    if (outWav.checked)  outFormats.extensions.push("wav")
    if (outFlac.checked) outFormats.extensions.push("flac")
    if (outOgg.checked)  outFormats.extensions.push("ogg")
    if (outMp3.checked)  outFormats.extensions.push("mp3")
    if (!outFormats.extensions.length)
      console.log("No output format selected")

    return (inFormats.extensions.length && outFormats.extensions.length)
    } // collectInOutFormats

  // flag for abort request
  property bool abortRequested: false

  // dialog to show progress
  Dialog {
    id: workDialog
    modality: Qt.ApplicationModal
    visible: false
    width: 720
    standardButtons: StandardButton.Abort

    Label {
      id: currentStatus
      width: 600
      text: qsTr("Running...")
      }

    TextArea {
      id: resultText
      width: 700
      height: 250
      anchors {
        top: currentStatus.bottom
        topMargin: 5
        }
      }

    onAccepted: {
      Qt.quit()
      }

    onRejected: {
      abortRequested = true
      Qt.quit()
      }
    }

  function inInputFormats(suffix) {
    var found = false

    for (var i = 0; i < inFormats.extensions.length; i++) {
      if (inFormats.extensions[i] == suffix) {
        found = true
        break
        }
      }
    return found
    }

  // createDefaultFileName
  // remove some special characters in a score title
  // when creating a file name
  function createDefaultFileName(fn) {
    fn = fn.trim()
    fn = fn.replace(/ /g,"_")
    fn = fn.replace(/\n/g,"_")
    fn = fn.replace(/[\\\/:\*\?\"<>|]/g,"_")
    return fn
    }

  // global list of folders to process
  property var folderList
  // global list of files to process
  property var fileList
  // global list of linked parts to process
  property var excerptsList

  // variable to remember current parent score for parts
  property var curBaseScore

  // FolderListModel can be used to search the file system
  FolderListModel {
    id: files
    }

  FileIO {
    id: file
    }

  Timer {
    id: excerptTimer
    interval: 1
    running: false

    // this function processes one linked part and
    // gives control back to QT to update the dialog
    onTriggered: {
      var curScoreInfo = excerptsList.shift()
      var thisScore = curScoreInfo[0].partScore
      var partTitle = curScoreInfo[0].title
      var fileBase = curScoreInfo[1]
      var srcModifiedTime = curScoreInfo[2]

      // create file base for part
      var targetBase = fileBase + "-" + createDefaultFileName(partTitle)

      // write for all target formats
      for (var j = 0; j < outFormats.extensions.length; j++) {
        var targetFile = targetBase + "." + outFormats.extensions[j]

        // get modification time of destination file (if it exists)
        // modifiedTime() will return 0 for non-existing files
        file.source = targetFile

        // if src is newer than existing write this file
        if (srcModifiedTime > file.modifiedTime()) {
          var res = writeScore(thisScore, targetFile, outFormats.extensions[j])

          resultText.append(" -> %1".arg(targetFile))
        } else {
          resultText.append(qsTr("%1 is up to date").arg(targetFile))
          }
        }

      // check if more files
      if (!abortRequested && excerptsList.length > 0) {
        excerptTimer.running = true
      } else {
        // close base score
        closeScore(curBaseScore)
        processTimer.running = true
        }
      }
    }

  Timer {
    id: processTimer
    interval: 1
    running: false

    // this function processes one file and then
    // gives control back to QT to update the dialog
    onTriggered: {
      if (fileList.length == 0) {
        // no more files to process
        workDialog.standardButtons = StandardButton.Ok
        if (!abortRequested) {
          currentStatus.text = qsTr("Done.")
        } else {
	  console.log("abort!")
          }
        return
      }

      var curFileInfo = fileList.shift()
      var shortName = curFileInfo[0]
      var fileName = curFileInfo[1]
      var fileBase = curFileInfo[2]

      // read file
      var thisScore = readScore(fileName,true)

      // make sure we have a valid score
      if (thisScore) {
        // get modification time of source file
        file.source = fileName
        var srcModifiedTime = file.modifiedTime()
        // write for all target formats
        for (var j = 0; j < outFormats.extensions.length; j++) {
          var targetFile = fileBase + "." + outFormats.extensions[j]

          // get modification time of destination file (if it exists)
          // modifiedTime() will return 0 for non-existing files
          file.source = targetFile

          // if src is newer than existing write this file
          if (srcModifiedTime > file.modifiedTime()) {
             var res = writeScore(thisScore, targetFile, outFormats.extensions[j])
             resultText.append("%1 -> %2".arg(fileName).arg(outFormats.extensions[j]))
          } else {
             resultText.append(qsTr("%1.%2 is up to date").arg(fileBase).arg(outFormats.extensions[j]))
             }
          }
        // check if we are supposed to export parts
        if (exportExcerpts.checked) {
          // reset list
          excerptsList = []
          // do we have excertps?
          var excerpts = thisScore.excerpts
          for (var ex = 0; ex < excerpts.length; ex++) {
            if (excerpts[ex].partScore != thisScore) {
              // only list when not base score
              excerptsList.push([excerpts[ex], fileBase, srcModifiedTime])
              }
            }
          // if we have files start timer
          if (excerpts.length > 0) {
            curBaseScore = thisScore // to be able to close this later
            excerptTimer.running = true
            return
            }
          }
        closeScore(thisScore)
      } else {
	resultText.append(qsTr("ERROR reading file %1").arg(shortName))
        }
      
      // next file
      processTimer.running = true
      }
    }

  // This timer contains the function that will be called
  // once the FolderListModel is set.
  Timer {
    id: collectFiles
    interval: 25
    running: false

    // Add all files found by FolderListModel to our list
    onTriggered: {
      // to be able to show what we're doing
      // we must create a list of files to process
      // and then use a timer to do the work
      // otherwise, the dialog window will not update

      for (var i = 0; i < files.count; i++) {

        // if we have a directory, we're supposed to
        // traverse it, so add it to folderList
        if (files.isFolder(i)) {
          folderList.push(files.get(i, "fileURL"))
        } else if (inInputFormats(files.get(i, "fileSuffix"))) {
          // found a file to process
          // set file names for in and out files
          var shortName = files.get(i, "fileName")
          var fileName = files.get(i, "filePath")
          var fileSuffix = files.get(i, "fileSuffix")
          var fileBase = fileName.substring(0,fileName.length - fileSuffix.length -1)
          fileList.push([shortName, fileName, fileBase])
          }
        }

      // if folderList is non-empty we need to redo this for the next folder
      if (folderList.length > 0) {
        files.folder = folderList.shift()
        // restart timer for folder search
        collectFiles.running = true
      } else if (fileList.length > 0) {
        // if we found files, start timer do process them
        processTimer.running = true
      } else {
        // we didn't find any files
        // report this
        resultText.append(qsTr("No files found"))
        workDialog.standardButtons = StandardButton.Ok
        currentStatus.text = qsTr("Done.")
        }
      }
    }

  function work() {
    console.log((traverseSubdirs.checked? "Startfolder: ":"Folder: ")
      + fileDialog.folder)

    // initialize global variables
    fileList = []
    folderList = []

    // set folder and filter in FolderListModel
    files.folder = fileDialog.folder

    if (traverseSubdirs.checked) {
      files.showDirs = true
      files.showFiles = true
    } else {
      // only look for files
      files.showFiles = true
      files.showDirs = false
      }

    // wait for FolderListModel to update
    // therefore we start a timer that will
    // wait for 25 millis and then start working
    collectFiles.running = true
    workDialog.visible = true
    } // work
  } // MuseScore
