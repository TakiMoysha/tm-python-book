import logging
import argparse
import hashlib
import os
from typing import Any, Literal, overload

from datetime import UTC, datetime
import msgspec
from pathlib import Path

# ================================================================================

DIVIDER = ":"

# ================================================================================


@overload
def get_checksum(data: str): ...
@overload
def get_checksum(data: bytes): ...


def get_checksum(data: str | bytes):
    if isinstance(data, str):
        data = data.encode()

    return hashlib.sha256(data).hexdigest()


# ================================================================================


class AppendOnlyLog:
    def __init__(self, file: Path) -> None:
        self.log_file = file
        self._descriptor = None

    def __enter__(self):
        self._descriptor = open(self.log_file, "a+")
        self._descriptor.seek(0)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._descriptor:
            self._descriptor.close()

    def write(self, event_type: str, data: msgspec.Struct):
        timestamp = datetime.now(UTC).isoformat()
        payload = msgspec.msgpack.encode(data)

        row = f"{timestamp}{DIVIDER}{event_type}{DIVIDER}{payload}"
        checksum = get_checksum(row)

        self._descriptor.write(f"{row}{DIVIDER}{checksum}\n")
        self._descriptor.flush()  # dump buffer to disk
        os.fsync(self._descriptor.fileno())  # sync with disk

        return row

    def _parse_log_row(self, log_line: str):
        """
        About converting:
            encoding msgspec.Struct, but decode return json (dict)
        """
        timestamp, event_type, payload, checksum = log_line.strip().split(DIVIDER)

        row = f"{timestamp}{DIVIDER}{event_type}{DIVIDER}{payload}"
        if checksum != get_checksum(row):
            logging.warning(f"checksum mismatch: {log_line}")
            return None

        payload = msgspec.msgpack.decode(payload)

        return payload

    def recover(self):
        self._descriptor.seek(0)
        events = []

        if self._descriptor is None:
            logging.error("bad log file")
            return

        for line in self._descriptor:
            if not line.endswith("\n"):
                logging.warning("line does not end with newline, skipping")
                continue

            try:
                event = self._parse_log_row(line)
            except Exception as err:
                logging.warning(f"failed to parse line: {line}")
                continue

            events.append(event)

        return events


def test_recovery_log():
    class FileSegmentEventInfo(msgspec.Struct):
        event_type: Literal["download"]
        segment_number: int

    class MockFileDownloader:
        @property
        def progress(self):
            return len(self._downloaded_segments) / self._total_segments

        def __init__(self) -> None:
            self._log = AppendOnlyLog(Path(__file__).parent / "test_mock_downloader_log.txt")
            self._downloaded_segments = set()

        def download(self, url, total_segments):
            self._url = url
            self._total_segments = total_segments
            self._downloaded_segments = set()

            with self._log as log:
                events: list[FileSegmentEventInfo] = log.recover()

                for event in events:
                    if event.event_type == "download":
                        self._downloaded_segments.add(event.segment_number)

                print("downloaded segments: ", self._downloaded_segments)

        def _next_segment(self, segment_number):
            print(f"downloading segment {segment_number}")

            with self._log as log:
                log.write(
                    "download",
                    FileSegmentEventInfo(event_type="download", segment_number=segment_number),
                )


def setup(*, log_level: str):
    logging.basicConfig(level=log_level)


def runner():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--level-log",
        help="log level",
        default="WARN",
        choices=["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"],
    )

    args = parser.parse_args()

    setup(log_level=args.level_log)


if __name__ == "__main__":
    runner()
