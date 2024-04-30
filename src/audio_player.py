# SPDX-License-Identifier: GPL-3.0-or-later
import numpy
from PySide6.QtCore import QObject, Signal
import sounddevice as sd
import soundfile as sf


class AudioPlayer(QObject):
    """Class to play audio files.
    
    Signals:
        played: When playback is started.
        paused: When playback is paused.
        file_loaded: When a file is succesfully loaded.
        time_changed: When the current second of playback changes.
    """
    played = Signal()
    paused = Signal()
    file_loaded = Signal(str, int)
    time_changed = Signal(int)

    def __init__(self):
        super().__init__()
        self._data: numpy.ndarray = None
        self._samplerate: int = None

        self._stream: sd.OutputStream = None
        self._sample = 0
        self._stopped = False
        self._stop_sample: int = None

        self._last_time_seconds = 0

    def get_time_s(self) -> int:
        """Current playback time in seconds."""
        return self._sample // self._samplerate

    def get_time_ms(self) -> int:
        """Current playback time in milliseconds."""
        return self._sample * 1000 // self._samplerate

    def stop_at_time_ms(self, time_ms: int):
        """Set a stop point for playback.
        
        Args:
            time_ms: Time in milliseconds on which playback should stop.
        """
        self._stop_sample = self._samplerate * time_ms // 1000

    def _finished_callback(self):
        """Reinitializes stream so playback can continue."""
        if self._stopped:
            self._init_stream()
            self._stopped = False

        self.paused.emit()

    def _get_sample_boundary(self):
        """Return nearest sample on which playback should be stopped.
        
        Playback should be stopped on a stop point or end of file.
        """
        if self._stop_sample is not None and self._sample < self._stop_sample:
            return self._stop_sample

        return len(self._data)

    def _init_stream(self):
        """Initializes an audio stream based on data from the loaded file.
        
        File needs decoded into self._data and this needs to be called before playing.
        """
        def callback(outdata: numpy.ndarray,
                     frames: int,
                     _time,
                     _status):
            chunksize = min(self._get_sample_boundary() - self._sample, frames)
            outdata[:chunksize] = self._data[self._sample:self._sample + chunksize]

            self._sample += chunksize

            current_time = self.get_time_s()

            if current_time != self._last_time_seconds:
                self._last_time_seconds = current_time
                self.time_changed.emit(current_time)

            if chunksize < frames:
                outdata[chunksize:] = 0
                self._stopped = True
                raise sd.CallbackStop()

        self._stream = sd.OutputStream(
            samplerate=self._samplerate,
            channels=2,
            callback=callback,
            finished_callback=self._finished_callback
        )

    def load_file(self, path: str):
        """Load and decode file into memory.
        
        Args:
            path: File to load.
        """
        if self._stream is not None:
            self._stream.abort()

        self._data, self._samplerate = sf.read(path, always_2d=True)
        self._init_stream()
        length = len(self._data) // self._samplerate
        self.file_loaded.emit(path, length)
        self._goto(0)

    def _goto(self, sample: int):
        """Set playback next sample.
        
        Sets sample where the audio playback thread will fetch data from next.

        Args:
            sample: Sample to set.
        """
        if self._stream is not None:
            self._sample = sample
            self.time_changed.emit(self.get_time_s())

    def goto_s(self, time_s: int):
        """Set playback.
        
        Args:
            time_s: Time in seconds to set playback to.
        """
        sample = self._samplerate * time_s
        self._goto(sample)

    def play_from_ms(self, time_ms: int):
        """Jump to playing from timestamp.
        
        Args:
            time_ms: Time in milliseconds to jump to.
        """
        sample = self._samplerate * time_ms // 1000
        self._goto(sample)
        self.play()

    def play(self):
        """Start playback from current time."""
        if self._stream is not None and self._stream.active is False:
            if self._sample == len(self._data):
                self._sample = 0

            self._stream.start()
            self.played.emit()

    def pause(self):
        """Pause playback."""
        if self._stream is not None and self._stream.active is True:
            self._stream.stop()
