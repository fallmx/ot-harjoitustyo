# SPDX-License-Identifier: GPL-3.0-or-later
from PySide6.QtCore import Slot, Qt
from PySide6 import QtWidgets
from audio_player import AudioPlayer
from project import Project


class PlaybackBar(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.slider = QtWidgets.QSlider(orientation=Qt.Orientation.Horizontal)
        self.slider.setTickInterval(1)

        self.vlayout = QtWidgets.QVBoxLayout(self)
        self.vlayout.addWidget(self.slider)

        self.marker_widget = QtWidgets.QWidget()
        self.marker_layout = QtWidgets.QHBoxLayout(self)
        self.marker_widget.setLayout(self.marker_layout)

        self.vlayout.addWidget(self.marker_widget)
        self.vlayout.addStretch()

        self.setLayout(self.vlayout)

    def add_marker_widget(self, time_ms: int):
        marker = QtWidgets.QLabel(f"{time_ms // 1000} s")
        self.marker_layout.addWidget(marker)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.audio = AudioPlayer()
        self.project = Project()

        self.playing = False
        self.length = 0

        self.audio.played.connect(self.played)
        self.audio.paused.connect(self.paused)
        self.audio.file_loaded.connect(self.file_loaded)
        self.audio.time_changed.connect(self.time_changed)
        self.project.marker_added.connect(self.marker_added)

        self.toolbar = QtWidgets.QToolBar("Test")
        self.toolbar.setFloatable(False)
        self.toolbar.setMovable(False)

        self.play_button = QtWidgets.QPushButton("Play")
        self.play_button.setEnabled(False)
        self.play_button.clicked.connect(self.toggle_playback)
        self.toolbar.addWidget(self.play_button)

        self.toolbar.addSeparator()

        self.set_button = QtWidgets.QPushButton("Set")
        self.set_button.setEnabled(False)
        self.set_button.clicked.connect(self.set_marker)
        self.toolbar.addWidget(self.set_button)

        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        self.playback_bar = PlaybackBar()
        self.playback_bar.setEnabled(False)
        self.playback_bar.slider.valueChanged.connect(
            self.playback_bar_changed)

        self.time_text = QtWidgets.QLabel("0:00/0:00",
                                          alignment=Qt.AlignmentFlag.AlignCenter)
        self.filename_text = QtWidgets.QLabel("No audio file loaded",
                                              alignment=Qt.AlignmentFlag.AlignCenter)
        self.load_button = QtWidgets.QPushButton("Load audio file")

        self.load_button.clicked.connect(self.load_audio_file)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        central_layout = QtWidgets.QVBoxLayout(self)
        central_layout.addWidget(self.playback_bar)
        central_layout.addWidget(self.time_text)
        central_layout.addStretch()
        central_layout.addWidget(self.filename_text)
        central_layout.addWidget(self.load_button)
        central_widget.setLayout(central_layout)

    @Slot()
    def played(self):
        self.playing = True
        self.play_button.setText("Pause")

    @Slot()
    def paused(self):
        self.playing = False
        self.play_button.setText("Play")

    @Slot()
    def set_marker(self):
        time_ms = self.audio.get_time_ms()
        self.project.add_marker(time_ms)

    @Slot(int)
    def marker_added(self, time_ms: int):
        self.playback_bar.add_marker_widget(time_ms)

    @Slot(str, int)
    def file_loaded(self, path: str, length: int):
        self.length = length
        self.filename_text.setText(path)
        self.play_button.setEnabled(True)
        self.set_button.setEnabled(True)
        self.playback_bar.slider.setMaximum(length)
        self.playback_bar.setEnabled(True)

    @Slot(int)
    def playback_bar_changed(self, new_time: int):
        self.audio.goto_s(new_time)

    @Slot(int)
    def time_changed(self, new_time: int):
        self.time_text.setText(
            f"{self.to_timestamp(new_time)}/{self.to_timestamp(self.length)}")

        if self.playback_bar.slider.isSliderDown() is False:
            self.playback_bar.slider.setValue(new_time)

        next_marker_time_ms = self.project.get_next_marker_time_ms(
            new_time * 1000)
        self.audio.stop_at_time_ms(next_marker_time_ms)

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
    main_window.resize(1000, 100)
    main_window.show()

    app.exec()


if __name__ == "__main__":
    main()
