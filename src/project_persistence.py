# SPDX-License-Identifier: GPL-3.0-or-later
from project import Project

FILE_SIGNATURE = b'\xbb\x5d\xc6\x89\x7e\x06\x4b\xd5'

FILE_FORMAT_VERSION = 1


class InvalidProjectFileError(Exception):
    pass


class UnsupportedProjectFileVersionError(Exception):
    pass


class ProjectPersistence:
    @staticmethod
    def save_project(path: str, project: Project):
        with open(path, "wb") as f:
            f.write(FILE_SIGNATURE)
            f.write(FILE_FORMAT_VERSION.to_bytes(2, "big"))

            audio_path = ""

            if project.audio_path is not None:
                audio_path = project.audio_path

            f.write(f"{audio_path}\0".encode("utf-8"))

            for marker in project.get_markers():
                marker_bytes = marker.time_ms.to_bytes(4, "big")
                f.write(marker_bytes)

    @staticmethod
    def load_project(path: str) -> Project:
        with open(path, "rb") as f:
            beginning = f.read(8)

            if beginning != FILE_SIGNATURE:
                raise InvalidProjectFileError

            loaded_file_format_version = int.from_bytes(f.read(2), "big")

            if loaded_file_format_version == 1:
                project = Project()

                audio_path_bytes = bytes()

                while True:
                    char = f.read(1)

                    if char == b'\x00':
                        break

                    audio_path_bytes += char

                project.audio_path = audio_path_bytes.decode("utf-8")

                while True:
                    marker_bytes = f.read(4)

                    if marker_bytes == b'':
                        break

                    new_marker_ms = int.from_bytes(marker_bytes, "big")

                    project.add_marker(new_marker_ms)

                return project

            raise UnsupportedProjectFileVersionError
