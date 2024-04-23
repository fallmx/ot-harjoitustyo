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

        self.jump_button = QtWidgets.QPushButton("Jump")
        self.jump_button.setEnabled(False)
        self.jump_button.clicked.connect(self.jump_to_next)
        self.toolbar.addWidget(self.jump_button)

        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        self.playback_bar = PlaybackBar()
        self.playback_bar.setEnabled(False)
        self.playback_bar.slider.sliderReleased.connect(
            self.goto_from_slider_value)
        self.playback_bar.slider.actionTriggered.connect(
            self.playback_bar_moved)
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

    @Slot()
    def jump_to_next(self):
        time_ms = self.audio.get_time_ms()
        next_time_ms = self.project.get_next_marker_time_ms(time_ms)
        self.audio.play_from_ms(next_time_ms)

    @Slot(int)
    def marker_added(self, time_ms: int):
        self.playback_bar.add_marker_widget(time_ms)

    @Slot(str, int)
    def file_loaded(self, path: str, length_s: int):
        self.length = length_s
        self.filename_text.setText(path)
        self.play_button.setEnabled(True)
        self.set_button.setEnabled(True)
        self.jump_button.setEnabled(True)
        self.playback_bar.slider.setMaximum(length_s)
        self.playback_bar.setEnabled(True)

    @Slot(int)
    def playback_bar_moved(self, action: int):
        # QtWidgets.QAbstractSlider.SliderAction.SliderMove
        enum_slider_move = 7

        if action != enum_slider_move:
            slider_pos = self.playback_bar.slider.sliderPosition()
            self.audio.goto_s(slider_pos)

    @Slot()
    def goto_from_slider_value(self):
        slider_value = self.playback_bar.slider.value()
        self.audio.goto_s(slider_value)

    @Slot(int)
    def playback_bar_changed(self, new_time_s: int):
        self.time_text.setText(
            f"{self._to_timestamp(new_time_s)}/{self._to_timestamp(self.length)}")

    @Slot(int)
    def time_changed(self, new_time_s: int):
        if self.playback_bar.slider.isSliderDown() is False:
            self.playback_bar.slider.setValue(new_time_s)

        next_marker_time_ms = self.project.get_next_marker_time_ms(
            new_time_s * 1000)
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

    def _to_timestamp(self, time_seconds: int) -> str:
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
