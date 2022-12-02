import hashlib
import inspect
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

class AOC():
    def __del__(self):
        self._ANSWERS_FILE.write_text(json.dumps(self._answers_obj, indent=4))

    def __init__(self, open_browser: bool = False):
        frame = inspect.stack()[1]
        modulef = inspect.getmodule(frame[0]).__file__
        if not isinstance(modulef, str):
            raise TypeError('Module file is not a string')
        filep = Path(modulef).resolve()
        self.DAY = self._get_day_from_file(filep)
        self.YEAR = self._get_year_from_path(filep)
        self.CACHE_DIR = Path(filep.parent / 'inputs')
        self._COOKIE_FILE = Path(filep.parent / 'data' / '.secret_session_cookie')
        self._ANSWERS_FILE = Path(filep.parent / 'data' / 'answers.json')

        if not self._ANSWERS_FILE.exists():
            self._ANSWERS_FILE.write_text('{}')

        self._answers_obj = json.loads(self._ANSWERS_FILE.read_text())

        self._cur_year = datetime.now().year
        if self.DAY < 1 or self.DAY > 25 or self.YEAR < 2015 or self.YEAR > self._cur_year:
            raise SystemExit(f'{self.YEAR} / {self.DAY} is not a valid Advent of Code date!')

        if not self._COOKIE_FILE.exists():
            raise FileNotFoundError(f'{self._COOKIE_FILE.__str__()} does not exist, login to www.adventofcode.com and save your session cookie to this file')
        self._session = requests.Session()
        self._session.cookies.set("session", self._COOKIE_FILE.read_text().strip(), domain="adventofcode.com")
        
        # To prevent the ban.
        self._session.headers.update({'User-Agent': 'https://github.com/tonyrla/AOCUtil'})
        if open_browser:
            import webbrowser
            webbrowser.open(f'https://adventofcode.com/{self.YEAR}/day/{self.DAY}')

    def _get_day_from_file(self, file: Path):
        try:
            return int(re.sub('[^0-9]', '', file.stem))
        except ValueError:
            raise SystemExit(f'Could not determine day from file {file.stem}')

    def _get_year_from_path(self, file: Path):
        try:
            return int(re.search(r'(20\d{2})', file.__str__()).group(1))
        except ValueError:
            raise SystemExit(f'Could not determine year from path: {file}')

    def get_input_data(self):
        if not self.CACHE_DIR.exists():
            self.CACHE_DIR.mkdir()

        input_file = self.CACHE_DIR / f'{self.YEAR}_{self.DAY:02d}.txt'
        if not input_file.exists():
            self._download_input_data(input_file)
            self._set_hash(input_file)
            return input_file.read_text()
        else:
            print(f'Using cached input data for {self.YEAR} day {self.DAY}')
            self._set_hash(input_file)
            return input_file.read_text()

    def _set_hash(self, input_file: Path) -> str:
        self._input_hash = hashlib.md5(input_file.read_bytes()).hexdigest()

    def _download_input_data(self, input_file: Path):
        r = self._session.get(f'https://adventofcode.com/{self.YEAR}/day/{self.DAY}/input')
        r.raise_for_status()
        with open(input_file, 'wb') as f:
            f.write(r.content)
        print(f'Downloaded input data for AOC {self.YEAR} day {self.DAY}')

    def post_answer(self, part: int, answer: Any) -> bool:
        print(f'Posting answer for part {part}: {answer}')
        
        if f'{self._input_hash}_{part}' in self._answers_obj:
            print('Answer already posted')
            return True

        if not self._COOKIE_FILE.exists():
            raise FileNotFoundError(f'{self._COOKIE_FILE.__str__()} does not exist, login to www.adventofcode.com and save your session cookie to this file')

        r = self._session.post(f'https://adventofcode.com/{self.YEAR}/day/{self.DAY}/answer', data={'level': part, 'answer': str(answer)})
        r.raise_for_status()

        if self._parse_response(r.text):
            print(f'Posted the correct answer for AOC {self.YEAR} day {self.DAY} part {part}')
            self._answers_obj[f'{self._input_hash}_{part}'] = str(answer)
            return True
        else:
            print(f'Posted the wrong answer for AOC {self.YEAR} day {self.DAY} part {part}, please wait a while and try again.')
            return False

    def _parse_response(self, response: str) -> bool:
        if "That's not the right answer" in response:
            return False
        elif "You gave an answer too recently" in response:
            matches = re.compile(r'([\w ]+) left to wait').findall(response)
            if matches:
                raise SystemExit(f'You gave an answer too recently, try again in {matches[0]}')
            else:
                raise SystemExit('You gave an answer too recently, try again later')
        elif "That's the right answer" in response:
            return True
        elif "Did you already complete it?" in response:
            print('You already completed this puzzle.')
            return True

        raise Exception(f'Unknown response: {response}')

def generate():
    TEMPLATE = Path("./TEMPLATE_DAY.py").resolve()
    if not TEMPLATE.exists():
        print(f"Template file does not exist {TEMPLATE}, creating a new one")
        TEMPLATE.write_text(f"""import sys
from AOCRla import AOC

class puzzle(AOC):
    def __init__(self, open_browser: bool = False):
        super().__init__(open_browser=open_browser)
        self.input = self.get_input_data()

    def part1(self) -> int|None:
        pass

    def part2(self) -> int|None:
        pass

    def part1_oneliner(self) -> int|None:
        # Path('./inputs/<year>_<day>.txt').read_text().splitlines()
        pass

    def part2_oneliner(self) -> int|None:
        pass

if __name__ == '__main__':
    use_browser = False

    raise SystemExit("This day's puzzle not implemented yet")

    if len(sys.argv) > 1:
        use_browser = True
    p = puzzle(open_browser=use_browser)

    part1 = p.part1()
    # p.post_answer(1, part1)

    # part2 = p.part2()
    # p.post_answer(2, part2)

""")
    else:
        print(f"Template file exists {TEMPLATE}")
    for day in range(1, 26):
        file = Path(f'./day{day:02d}.py').resolve()
        if file.exists():
            continue
        # Copy template file as new file
        file.write_text(TEMPLATE.read_text())
    TEMPLATE.unlink()

if __name__ == '__main__':
    print(f'Generating new day files...{Path.cwd()}')
    generate()
