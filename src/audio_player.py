# SPDX-License-Identifier: GPL-3.0-or-later
import numpy
from PySide6.QtCore import QObject, Signal
import sounddevice as sd
import soundfile as sf

class AudioPlayer(QObject):
    played = Signal()
    paused = Signal()
    file_loaded = Signal(str, int)
    time_changed = Signal(int)

    def __init__(self):
        super().__init__()
        self.data: numpy.ndarray = None
        self.samplerate: int = None

        self.stream: sd.OutputStream = None
        self.sample = 0
        self.finished = False

        self._last_time_seconds = 0

    def time_seconds(self) -> int:
        return self.sample // self.samplerate

    def finished_callback(self):
        if self.finished:
            self.init_stream()
            
        self.paused.emit()
    
    def init_stream(self):
        def callback(outdata: numpy.ndarray,
                     frames: int,
                     time,
                     status):
            chunksize = min(len(self.data) - self.sample, frames)
            outdata[:chunksize] = self.data[self.sample:self.sample + chunksize]

            self.sample += chunksize

            current_time = self.time_seconds()

            if current_time != self._last_time_seconds:
                self._last_time_seconds = current_time
                self.time_changed.emit(current_time)

            if chunksize < frames:
                outdata[chunksize:] = 0
                self.finished = True
                raise sd.CallbackStop()

        self.stream = sd.OutputStream(
            samplerate=self.samplerate,
            channels=2,
            callback=callback,
            finished_callback=self.finished_callback
        )
    
    def load_file(self, path: str):
        if self.stream is not None:
            self.stream.abort()

        self.data, self.samplerate = sf.read(path, always_2d=True)
        self.init_stream()
        length = len(self.data) // self.samplerate
        self.file_loaded.emit(path, length)
        self.goto(0)
    
    def goto(self, sample: int):
        if self.stream is not None:
            self.sample = min(len(self.data) - 1, sample)
            self.finished = False
            self.time_changed.emit(self.time_seconds())
    
    def play(self):
        if self.stream is not None and self.stream.active == False:
            if self.finished:
                self.goto(0)

            self.stream.start()
            self.played.emit()

    def pause(self):
        if self.stream is not None and self.stream.active == True:
            self.stream.stop()
