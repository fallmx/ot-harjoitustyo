# SPDX-License-Identifier: GPL-3.0-or-later
import unittest
import time
from audio_player import AudioPlayer

TEST_FILE = "src/tests/test_data/test.wav"
TEST_FILE_SAMPLES = 160195


class TestAudioPlayer(unittest.TestCase):
    def setUp(self):
        self.player = AudioPlayer()
        self.player.load_file(TEST_FILE)

    def test_load_works(self):
        sample_amount = len(self.player._data)
        self.assertEqual(sample_amount, TEST_FILE_SAMPLES)

    def test_playing_works(self):
        self.player.play()
        time.sleep(0.1)
        self.player.pause()

        self.assertGreater(self.player._sample, 0)
