# SPDX-License-Identifier: GPL-3.0-or-later
from PySide6 import QtCore, QtWidgets
import sounddevice as sd
import soundfile as sf

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.filename = ""
        self.playing = False
        self.audio_data = None
        self.sample_rate = None

        self.play_button = QtWidgets.QPushButton("Play")
        self.play_button.setEnabled(False)
        self.filename_text = QtWidgets.QLabel("No audio file loaded",
                                              alignment=QtCore.Qt.AlignCenter)
        self.load_button = QtWidgets.QPushButton("Load audio file")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.play_button)
        self.layout.addWidget(self.filename_text)
        self.layout.addWidget(self.load_button)

        self.play_button.clicked.connect(self.toggle_playback)
        self.load_button.clicked.connect(self.load_audio_file)

    @QtCore.Slot()
    def play(self):
        self.playing = True
        self.play_button.setText("Pause")
        sd.play(self.audio_data, self.sample_rate)
    
    @QtCore.Slot()
    def pause(self):
        self.playing = False
        self.play_button.setText("Play")
        sd.stop()
    
    @QtCore.Slot()
    def toggle_playback(self):
        if self.playing:
            self.pause()
        else:
            self.play()

    @QtCore.Slot()
    def load_audio_file(self):
        self.filename, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                         "Load audio file",
                                                         "/home")
        if self.filename != "":
            self.pause()
            self.filename_text.setText(self.filename)
            self.play_button.setEnabled(True)
            self.audio_data, self.sample_rate = sf.read(self.filename)

def main():
    app = QtWidgets.QApplication([])

    main_window = MainWindow()
    main_window.setWindowTitle("soittokone")
    main_window.resize(500, 500)
    main_window.show()

    app.exec()

if __name__ == "__main__":
    main()
