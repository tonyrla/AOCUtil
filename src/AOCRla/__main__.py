import subprocess
from .aoc import AOC
import sys
from argparse import ArgumentParser
from datetime import datetime, timezone



def main():
    now = datetime.now(tz=timezone.utc)
    args = ArgumentParser()
    args.add_argument("-y", "--year", type=int, help="The year to run", default=now.year)
    args.add_argument("-d", "--day", type=int, help="The day to run", default=now.day)
    args.add_argument("-b", "--browser", type=bool, help="Open browser", default=False)
    opts = args.parse_args()
    aoc = AOC(opts.browser, year=opts.year, day=opts.day)
    aoc.get_input_data(year=opts.year, day=opts.day)
    return 0

def run():
    now = datetime.now(tz=timezone.utc)
    args = ArgumentParser()
    args.add_argument("-y", "--year", type=int, help="The year to run", default=now.year)
    args.add_argument("-d", "--day", type=int, help="The day to run", default=now.day)
    opts = args.parse_args()
    aoc = AOC(year=opts.year, day=opts.day)
    aoc.get_input_data(year=opts.year, day=opts.day)

    # run python file:
    p = subprocess.run([sys.executable, f"day{opts.day:02d}.py"])
    return p.returncode

if __name__ == "__main__":
    raise SystemExit(main())
