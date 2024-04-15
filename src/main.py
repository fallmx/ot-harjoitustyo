# SPDX-License-Identifier: GPL-3.0-or-later
from PySide6.QtCore import Slot, Qt
from PySide6 import QtWidgets
from audio_player import AudioPlayer

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.playing = False
        self.audio = AudioPlayer()
        self.length = 0

        self.audio.played.connect(self.played)
        self.audio.paused.connect(self.paused)
        self.audio.file_loaded.connect(self.file_loaded)
        self.audio.time_changed.connect(self.time_changed)

        self.play_button = QtWidgets.QPushButton("Play")
        self.play_button.setEnabled(False)
        self.time_text = QtWidgets.QLabel("0:00/0:00",
                                              alignment=Qt.AlignmentFlag.AlignCenter)
        self.filename_text = QtWidgets.QLabel("No audio file loaded",
                                              alignment=Qt.AlignmentFlag.AlignCenter)
        self.load_button = QtWidgets.QPushButton("Load audio file")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.play_button)
        self.layout.addWidget(self.time_text)
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
    
    @Slot(str, int)
    def file_loaded(self, path: str, length: int):
        self.length = length
        self.filename_text.setText(path)
        self.play_button.setEnabled(True)

    @Slot(int)
    def time_changed(self, new_time: int):
        self.time_text.setText(
            f"{self.to_timestamp(new_time)}/{self.to_timestamp(self.length)}")
    
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
    
    def to_timestamp(self, time_seconds: int) -> str:
        minutes, seconds = divmod(time_seconds, 60)
        return f"{minutes}:{seconds:02}"

def main():
    app = QtWidgets.QApplication([])

    main_window = MainWindow()
    main_window.setWindowTitle("soittokone")
    main_window.resize(500, 500)
    main_window.show()

    app.exec()

if __name__ == "__main__":
    main()
