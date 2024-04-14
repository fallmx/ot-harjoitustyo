import numpy
from PySide6.QtCore import QObject, Signal
import sounddevice as sd
import soundfile as sf

class AudioPlayer(QObject):
    played = Signal()
    paused = Signal()
    file_loaded = Signal(str)

    def __init__(self):
        super().__init__()
        self.data: numpy.ndarray = None
        self.samplerate: int = None

        self.stream: sd.OutputStream = None
        self.sample = 0

        self.finished = False

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

            if chunksize < frames:
                outdata[chunksize:] = 0
                self.finished = True
                raise sd.CallbackStop()
            
            self.sample += chunksize

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
        self.sample = 0
        self.init_stream()
        self.file_loaded.emit(path)
    
    def play(self):
        if self.stream is not None and self.stream.active == False:
            if self.finished:
                self.sample = 0
                self.finished = False

            self.stream.start()
            self.played.emit()

    def pause(self):
        if self.stream is not None and self.stream.active == True:
            self.stream.stop()
