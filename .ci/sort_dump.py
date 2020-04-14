#!/usr/bin/env python
import fileinput
import re

CREATE_TABLE_RE = re.compile(r"^CREATE TABLE .*? \($")
CREATE_TYPE_RE = re.compile(r"^CREATE TYPE .*? AS ENUM \($")

END_BLOCK_RE = re.compile(r"^\);$")

SETVAL_RE = re.compile(r"^SELECT pg_catalog.setval\('.*?', .*?\);$")


class Sorter:
    def __init__(self):
        self.inside_block = False
        self.buffer = []

    def process_line(self, line: str):
        if self.inside_block:
            self.process_line_inside_block(line)
            return

        if SETVAL_RE.fullmatch(line):
            # skip lines that reset the sequence object's counter value
            return

        if CREATE_TABLE_RE.fullmatch(line) or CREATE_TYPE_RE.fullmatch(line):
            self.inside_block = True

        self.print(line)

    def process_line_inside_block(self, line: str):
        if END_BLOCK_RE.fullmatch(line):
            self.print_buffer()
            self.inside_block = False
            self.print(line)
            return

        self.buffer.append(line)

    def print_buffer(self):
        self.buffer.sort()
        for line in self.buffer:
            self.print(line.rstrip(", "))
        self.buffer.clear()

    @classmethod
    def print(cls, line: str):
        print(line)


def main():
    sorter = Sorter()

    with fileinput.input() as file:
        for line in file:
            sorter.process_line(line.rstrip("\n"))


if __name__ == "__main__":
    main()
