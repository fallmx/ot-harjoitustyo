# SPDX-License-Identifier: GPL-3.0-or-later
import unittest
from project import Project
from project_persistence import ProjectPersistence


class TestProjectPersistence(unittest.TestCase):
    def test_saving_and_loading(self):
        project = Project()
        project.audio_path = "/audio.mp3"
        project.add_marker(100)
        project.add_marker(200)
        project.add_marker(500)
        ProjectPersistence.save_project("src/tests/test.skproj", project)
        loaded = ProjectPersistence.load_project("src/tests/test.skproj")

        self.assertEqual(loaded.audio_path, "/audio.mp3")

        test1 = loaded.get_next_marker_time_ms(0)
        self.assertEqual(test1, 100)

        test2 = loaded.get_next_marker_time_ms(150)
        self.assertEqual(test2, 200)

        test3 = loaded.get_next_marker_time_ms(500)
        self.assertEqual(test3, 500)
