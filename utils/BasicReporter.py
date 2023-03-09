from typing import List

from tudelft_utilities_logging.Reporter import Reporter
import logging


class BasicReporter(Reporter):
    """
        This Reporter (logger) print only Warnings and Errors.
    """
    logs: List[str]
    file_path: str

    def __init__(self, file_path: str = "tournament_log.txt"):
        self.file_path = file_path
        self.logs = []

    def log(self, level:int, msg:str, thrown:BaseException=None):
        if level >= logging.WARNING:
            print(logging.getLevelName(level), ":", msg)

        self.logs.append(msg)

    def save_log(self):
        with open(self.file_path, "w") as f:
            f.write("\n".join(self.logs))
