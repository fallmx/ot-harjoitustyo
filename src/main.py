# SPDX-License-Identifier: GPL-3.0-or-later
from os import getcwd
from PySide6.QtCore import Slot, Qt
from PySide6 import QtWidgets, QtGui
from audio_player import AudioPlayer
from project import Project
from project_persistence import ProjectPersistence


class PlaybackBar(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.slider = QtWidgets.QSlider(orientation=Qt.Orientation.Horizontal)
        self.slider.setTickInterval(1)

        self.vlayout = QtWidgets.QVBoxLayout(self)
        self.vlayout.addWidget(self.slider)

        self.marker_text = QtWidgets.QLabel()

        self.vlayout.addWidget(self.marker_text)
        self.vlayout.addStretch()

        self.setLayout(self.vlayout)

    def add_marker_widget(self, time_ms: int):
        seconds, milliseconds = divmod(time_ms, 1000)
        new_marker_text = f"{seconds}.{milliseconds} s"
        self.marker_text.setText(
            f"{self.marker_text.text()} {new_marker_text}")


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.audio = AudioPlayer()
        self.project = Project()

        self.project_path: str = None

        self.playing = False
        self.length = 0

        self.audio.played.connect(self.played)
        self.audio.paused.connect(self.paused)
        self.audio.file_loaded.connect(self.file_loaded)
        self.audio.time_changed.connect(self.time_changed)
        self.project.marker_added.connect(self.marker_added)

        self.menubar = QtWidgets.QMenuBar()

        self.file_menu = self.menubar.addMenu("File")

        self.open_project = QtGui.QAction("Open...")
        self.open_project.triggered.connect(self.project_opened)

        self.save_project = QtGui.QAction("Save")
        self.save_project.triggered.connect(self.project_saved)

        self.save_project_as = QtGui.QAction("Save as...")
        self.save_project_as.triggered.connect(self.project_saved_as)

        self.file_menu.addAction(self.open_project)
        self.file_menu.addAction(self.save_project)
        self.file_menu.addAction(self.save_project_as)

        self.setMenuBar(self.menubar)

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

    def set_project_path(self, path):
        self.project_path = path
        self.setWindowTitle(f"{path} - soittokone")

    @Slot()
    def project_opened(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                        "Open project file",
                                                        getcwd(),
                                                        "soittokone project file (*.skproj)")
        opened_project = ProjectPersistence.load_project(path)
        self.audio.load_file(opened_project.audio_path)

        self.project = opened_project
        self.project.marker_added.connect(self.marker_added)
        self.set_project_path(path)

        self.playback_bar.marker_text.setText("")

        for marker in self.project.get_markers():
            self.playback_bar.add_marker_widget(marker.time_ms)

    @Slot()
    def project_saved(self):
        if self.project_path is None:
            self.project_saved_as()
        else:
            ProjectPersistence.save_project(self.project_path, self.project)

    @Slot()
    def project_saved_as(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self,
                                                        "Save project file as",
                                                        getcwd() + "/untitled.skproj",
                                                        "soittokone project file (*.skproj)")

        if path != "":
            ProjectPersistence.save_project(path, self.project)
            self.set_project_path(path)

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
        self.project.audio_path = path
        self.filename_text.setText(path)
        self.play_button.setEnabled(True)
        self.set_button.setEnabled(True)
        self.jump_button.setEnabled(True)
        self.playback_bar.slider.setMaximum(length_s)
        self.playback_bar.setEnabled(True)
        self.time_changed(length_s)

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
                                                        getcwd())
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
