# SPDX-License-Identifier: GPL-3.0-or-later
from PySide6.QtCore import Slot, Qt
from PySide6 import QtWidgets
from audio_player import AudioPlayer

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.playing = False
        self.audio = AudioPlayer()

        self.audio.played.connect(self.played)
        self.audio.paused.connect(self.paused)
        self.audio.file_loaded.connect(self.file_loaded)

        self.play_button = QtWidgets.QPushButton("Play")
        self.play_button.setEnabled(False)
        self.filename_text = QtWidgets.QLabel("No audio file loaded",
                                              alignment=Qt.AlignCenter)
        self.load_button = QtWidgets.QPushButton("Load audio file")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.play_button)
        self.layout.addWidget(self.filename_text)
        self.layout.addWidget(self.load_button)

        self.play_button.clicked.connect(self.toggle_playback)
        self.load_button.clicked.connect(self.load_audio_file)

    @Slot()
    def played(self):
        self.playing = True
        self.play_button.setText("Pause")
    
    @Slot()
    def paused(self):
        self.playing = False
        self.play_button.setText("Play")
    
    @Slot(str)
    def file_loaded(self, path):
        self.filename_text.setText(path)
        self.play_button.setEnabled(True)
    
    @Slot()
    def toggle_playback(self):
        if self.playing:
            self.audio.pause()
        else:
            self.audio.play()

    @Slot()
    def load_audio_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                         "Load audio file",
                                                         "/home")
        if path != "":
            self.audio.load_file(path)

def main():
    app = QtWidgets.QApplication([])

    main_window = MainWindow()
    main_window.setWindowTitle("soittokone")
    main_window.resize(500, 500)
    main_window.show()

    app.exec()

if __name__ == "__main__":
    main()
