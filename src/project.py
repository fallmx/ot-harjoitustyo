# SPDX-License-Identifier: GPL-3.0-or-later
from PySide6.QtCore import QObject, Signal


class Marker:
    """Marker with a timestamp.

    Attributes:
        time_ms: Time in milliseconds of this marker.
        prev: Previous marker in the doubly linked list.
        next: Next marker in the doubly linked list.
    """

    def __init__(self, time_ms: int):
        self.time_ms = time_ms
        self.prev: Marker = None
        self.next: Marker = None

    def __repr__(self):
        p = self.prev and self.prev.time_ms or None
        n = self.next and self.next.time_ms or None
        return f"<Marker {p}-{self.time_ms}-{n}>"


class Project(QObject):
    """Class to hold a marker project.

    Stores markers and audio path. Markers are stored in a doubly linked list.

    Attributes:
        audio_path: Audio path of this project.
    Signals:
        marker_added(int time_ms): When a marker is added.
    """
    marker_added = Signal(int)

    def __init__(self):
        super().__init__()
        self._first_marker: Marker = None
        self._maybe_next: Marker = None
        self.audio_path: str = None

    def get_markers(self):
        """Returns a generator of the markers."""
        marker = self._first_marker

        while marker is not None:
            yield marker
            marker = marker.next

    def _get_last_marker(self) -> Marker | None:
        last = None
        marker = self._first_marker

        while True:
            if marker is None:
                return last

            last = marker
            marker = marker.next

    def _get_next_marker(self, time_ms: int, start_marker: Marker = None) -> Marker | None:
        marker = start_marker or self._first_marker

        while True:
            if marker is None:
                return None

            prev_time_ms = -1

            if marker.prev is not None:
                prev_time_ms = marker.prev.time_ms

            if prev_time_ms >= time_ms:
                return None

            if prev_time_ms < time_ms <= marker.time_ms:
                return marker

            marker = marker.next

    def get_next_marker_time_ms(self, time_ms: int) -> int:
        """Get the next marker time where time_ms<=next_marker_time_ms.

        If no next marker is found, return 0.

        Args:
            time_ms: Time in milliseconds from where the search is started.
        """
        maybe_next = self._get_next_marker(time_ms, self._maybe_next)

        if maybe_next is not None:
            self._maybe_next = maybe_next.next
            return maybe_next.time_ms

        next_marker = self._get_next_marker(time_ms)

        if next_marker is None:
            return 0

        return next_marker.time_ms

    def _link_markers(self, marker1: Marker | None, marker2: Marker | None):
        if marker1 is not None:
            marker1.next = marker2
        if marker2 is not None:
            marker2.prev = marker1

    def add_marker(self, time_ms: int):
        """Add a marker.

        Doesn't add duplicate markers on the same time_ms.

        Args:
            time_ms: Time in milliseconds to add the marker to.
        """
        marker = Marker(time_ms)

        if self._first_marker is None:
            self._first_marker = marker
        else:
            next_marker = self._get_next_marker(time_ms)
            prev_marker = None

            if next_marker is None:
                prev_marker = self._get_last_marker()
            else:
                if next_marker.time_ms == time_ms:
                    return

                prev_marker = next_marker.prev

            self._link_markers(prev_marker, marker)
            self._link_markers(marker, next_marker)

            if time_ms < self._first_marker.time_ms:
                self._first_marker = marker

        self.marker_added.emit(time_ms)
