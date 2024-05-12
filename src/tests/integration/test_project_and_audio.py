# SPDX-License-Identifier: GPL-3.0-or-later
import unittest
import time
from project import Project
from audio_player import AudioPlayer

TEST_FILE = "src/tests/test_data/test.wav"


class TestProjectAndAudio(unittest.TestCase):
    def setUp(self):
        self.project = Project()
        self.audio = AudioPlayer()
        self.audio.load_file(TEST_FILE)
        self.project.add_marker(1000)

    def test_next_marker_from_audio_timestamp(self):
        time_ms = self.audio.get_time_ms()
        next_time_ms = self.project.get_next_marker_time_ms(time_ms)

        self.assertEqual(next_time_ms, 1000)

        self.audio.goto_s(2)

        time_ms = self.audio.get_time_ms()
        next_time_ms = self.project.get_next_marker_time_ms(time_ms)

        self.assertEqual(next_time_ms, 0)

    def test_jumping_to_next_marker(self):
        time_ms = self.audio.get_time_ms()
        next_time_ms = self.project.get_next_marker_time_ms(time_ms)

        self.audio.play_from_ms(next_time_ms)
        time.sleep(0.1)
        self.audio.pause()

        time_ms = self.audio.get_time_ms()
        self.assertGreater(time_ms, 1000)
