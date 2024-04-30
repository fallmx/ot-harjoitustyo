# SPDX-License-Identifier: GPL-3.0-or-later
import unittest
from project import Project


class TestProject(unittest.TestCase):
    def setUp(self):
        self.project = Project()

    def test_empty_project_returns_zero_as_next_marker_time(self):
        next_time_ms = self.project.get_next_marker_time_ms(50)
        self.assertEqual(next_time_ms, 0)

    def test_adding_one_marker_works(self):
        self.project.add_marker(1000)

        next_time_ms = self.project.get_next_marker_time_ms(500)
        self.assertEqual(next_time_ms, 1000)

    def test_adding_many_markers_works(self):
        self.project.add_marker(1000)
        self.project.add_marker(2000)

        first_time_ms = self.project.get_next_marker_time_ms(500)
        self.assertEqual(first_time_ms, 1000)

        second_time_ms = self.project.get_next_marker_time_ms(1500)
        self.assertEqual(second_time_ms, 2000)

    def test_get_last_marker(self):
        none = self.project._get_last_marker()

        self.assertIsNone(none)

        self.project.add_marker(1000)
        self.project.add_marker(2000)

        last = self.project._get_last_marker()

        last_time_ms = last.time_ms
        self.assertEqual(last_time_ms, 2000)
