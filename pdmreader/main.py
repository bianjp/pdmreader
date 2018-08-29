import argparse
import os.path
import readline
import sys

from .command_executor import CommandExecutor
from .parser import PDMParser


def main():
    parser = argparse.ArgumentParser(description='Interactive PDM reader')
    parser.add_argument('file', help='PDM file')
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print("File not found: " + args.file, file=sys.stderr)
        return

    schema = PDMParser(args.file).parse()
    executor = CommandExecutor(schema)

    history_file = os.path.expanduser('~/.pdmreader_history')
    if os.path.exists(history_file):
        readline.read_history_file(history_file)

    try:
        while True:
            command: str = input('>>> ').strip()
            if not command:
                continue
            executor.command(command)
    except Exception as e:
        readline.set_history_length(1000)
        readline.write_history_file(history_file)
        if isinstance(e, EOFError):
            print()
        else:
            raise e
