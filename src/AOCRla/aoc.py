import hashlib
import inspect
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import requests
from loguru import logger

class _Helper():
    ...


class AOC(_Helper):
    def __del__(self):
        self._ANSWERS_FILE.write_text(json.dumps(self._answers_obj, indent=4)+"\n")

    def __init__(self, open_browser: bool = False, block_init: bool = False, year: int|None = None, day: int|None = None):
        if year is not None:
            self.YEAR = year
        if day is not None:
            self.DAY = day

        print(year, day)
        logger.remove()
        logger.add(sys.stdout, level=os.environ.get('AOC_LOG_LEVEL', 'INFO'))
        self.logger = logger

        self.__filep = self._get_filepath()
        self.CACHE_DIR = Path(Path.cwd() / 'inputs')
        self._COOKIE_FILE = Path(Path.cwd() / 'data' / '.secret_session_cookie')
        self._ANSWERS_FILE = Path(Path.cwd() / 'data' / 'answers.json')
        self._SPAM_BLOCKER_FILE = Path(self.__filep.parent / 'data' / 'spam_blocker')
        
        self._setup_answers_cache()

        if not block_init:
            self._scrape_day_and_year_from_filepath()
            
            self._cur_year = datetime.now().year

            self._verify_init_data()
            self._setup_session()

        if open_browser:
            import webbrowser
            webbrowser.open(f'https://adventofcode.com/{self.YEAR}/day/{self.DAY}')

    def _get_filepath(self):
        """ Set the filepath of the file that called this function. """
        frame = inspect.stack()[2]
        modulef = inspect.getmodule(frame[0]).__file__
        if not isinstance(modulef, str):
            raise TypeError('Module file is not a string')
        return Path(modulef).resolve()

    def _scrape_day_and_year_from_filepath(self):
        if self.__filep.stem == '__main__':
            return
        self.DAY = self._get_day_from_file(self.__filep)
        self.YEAR = self._get_year_from_path(self.__filep)

    def _verify_init_data(self):
        if self.DAY < 1 or self.DAY > 25 or self.YEAR < 2015 or self.YEAR > self._cur_year:
            raise SystemExit(f'{self.YEAR} / {self.DAY} is not a valid Advent of Code date!')

        if not self._COOKIE_FILE.exists():
            raise FileNotFoundError(f'{self._COOKIE_FILE.__str__()} does not exist, login to www.adventofcode.com and save your session cookie to this file')

    def _setup_answers_cache(self):
        if not self._ANSWERS_FILE.exists():
            self._ANSWERS_FILE.write_text('{}')

        self._answers_obj = json.loads(self._ANSWERS_FILE.read_text())

    def _setup_session(self):
        self._session = requests.Session()
        self._session.cookies.set("session", self._COOKIE_FILE.read_text().strip(), domain="adventofcode.com")
        
        # To prevent the ban.
        self._session.headers.update({'User-Agent': 'https://github.com/tonyrla/AOCUtil'})


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

    def get_input_data(self, year = None, day = None):
        if not self.CACHE_DIR.exists():
            self.CACHE_DIR.mkdir()

        if year is None and day is None:
            input_file = self.CACHE_DIR / f'{self.YEAR}_{self.DAY:02d}.txt'
        elif year is not None and day is not None:
            self.year = year
            self.day = day
            input_file = self.CACHE_DIR / f'{year}_{day:02d}.txt'
        elif year is not None:
            self.year = year
            input_file = self.CACHE_DIR / f'{year}_{self.DAY:02d}.txt'
        elif day is not None:
            self.day = day
            input_file = self.CACHE_DIR / f'{self.YEAR}_{day:02d}.txt'

        input_file = self.CACHE_DIR / f'{self.YEAR}_{self.DAY:02d}.txt'
        if not input_file.exists():
            self._download_input_data(input_file)
            self._set_hash(input_file)
            self.logger.info(f'Input data for AOC {self.YEAR} day {self.DAY} saved to {input_file}')
            return input_file.read_text()
        else:
            self.logger.warning(f'Using cached input data for {self.YEAR} day {self.DAY}')
            self._set_hash(input_file)
            return input_file.read_text()

    def get_input_data_as_list(self):
        """ Returns a list of input data, where each element is a row of input data.

        Example input:
            A Y\nB Y\nB Z\nB X\n\nC X\nC Y\n
        Returns:
            ['A Y', 'B Y', 'B Z', 'B X', '', 'C X', 'C Y']
        """

        return self.get_input_data().splitlines()
     
    def get_input_data_as_splitlist(self, t: Any=str):
        """ Returns a list of lists, where each sublist is a row of input data.
        
        Example input:
            A Y\nB Y\nB Z\nB X\n\nC X\nC Y\n
            Returns:
            [['A', 'Y'], ['B', 'Y'], ['B', 'Z'], ['B', 'X'], [], ['C', 'X'], ['C', 'Y']]
            t=ord returns:
            [[65, 89], [66, 89], [66, 90], [66, 88], [], [67, 88], [67, 89]]
        """
        return [list(map(lambda s: t(s), x.split())) for x in self.get_input_data().splitlines()]

    def get_input_data_as_int_list(self):
        """ Returns a list of input data, where each element is a row of input data.

        Example input:
            1\n2\n3\n4\n\n5\n
        Returns:
            [1, 2, 3, 4, 5]
        """

        return [int(x) for x in self.get_input_data_as_list() if x != '']
    
    def get_input_data_as_grid(self, t: Any=str):
        """ Returns a grid, where each sublist is a row of input data.

        Example input:
            A Y\nB Y\nB Z\nB X\n\nC X\nC Y\n
        Returns:
            [['A', ' ', 'Y'], ['B', ' ', 'Y'], ['B', ' ', 'Z'], ['B', ' ', 'X'], [], ['C', ' ', 'X'], ['C', ' ', 'Y']]
        t=ord returns:
            [[65, 32, 89], [66, 32, 89], [66, 32, 90], [66, 32, 88], [], [67, 32, 88], [67, 32, 89]]
        """
        return [list(map(lambda s: t(s), x)) for x in self.get_input_data_as_list()]

    def get_input_data_sublist(self,t: Any=str):
        """Returns a list of lists, where each sublist is a block of input data separated by blank lines.

        Example input:
            A Y\nB Y\nB Z\nB X\n\nC X\nC Y\n
        Returns:
            [['A Y', 'B Y', 'B Z', 'B X'], ['C X', 'C Y']]
        t=ord returns:
            [[65, 89], [66, 89], [66, 90], [66, 88], [], [67, 88], [67, 89]]
        """
        for lst in [list(map(lambda s: t(s), x.split())) for x in self.get_input_data().splitlines()]:
            yield lst


    def _set_hash(self, input_file: Path) -> str:
        self._input_hash = hashlib.md5(input_file.read_bytes()).hexdigest()

    def _download_input_data(self, input_file: Path):
        r = self._session.get(f'https://adventofcode.com/{self.YEAR}/day/{self.DAY}/input')
        r.raise_for_status()
        with open(input_file, 'wb') as f:
            f.write(r.content)
        self.logger.info(f'Downloaded input data for AOC {self.YEAR} day {self.DAY}')

    def post_answer(self, part: int, answer: Any) -> bool:
        self.logger.info(f'Posting answer for part {part}: {answer}')
        
        if not self.spamblocker_released():
            time = self._SPAM_BLOCKER_FILE.read_text()
            now = datetime.now()
            time_to_datetime = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            delta = time_to_datetime-now
            self.logger.warning(f'Spamblocker is active for {delta}, not posting answer')
            raise SystemExit(1)
        else:
            if self._SPAM_BLOCKER_FILE.exists():
                self.logger.warning('Spamblocker released, deleting file')
                self._SPAM_BLOCKER_FILE.unlink()
        
        if f'{self._input_hash}_{part}' in self._answers_obj:
            result = self._answers_obj[f'{self._input_hash}_{part}']
            t = type(result)
            result = t(answer) == result
            self.logger.warning('Answer already posted, checking against cache :' + (' Correct!' if result else ' Incorrect!'))
            return result
        # else:
            # TODO: 
            # if self._SPAM_BLOCKER_FILE.exists():
            # open, check if time is up and delete, if not, return False


        if not self._COOKIE_FILE.exists():
            raise FileNotFoundError(f'{self._COOKIE_FILE.__str__()} does not exist, login to www.adventofcode.com and save your session cookie to this file')

        r = self._session.post(f'https://adventofcode.com/{self.YEAR}/day/{self.DAY}/answer', data={'level': part, 'answer': str(answer)})
        r.raise_for_status()

        if self._parse_response(r.text):
            self.logger.info(f'Posted the correct answer for AOC {self.YEAR} day {self.DAY} part {part}')
            self._answers_obj[f'{self._input_hash}_{part}'] = str(answer)
            return True
        else:
            self.logger.info(f'Posted the wrong answer for AOC {self.YEAR} day {self.DAY} part {part}, please wait a while and try again.')
            return False

    def spamblocker_released(self):
        if self._SPAM_BLOCKER_FILE.exists():
            with open(self._SPAM_BLOCKER_FILE, 'r') as f:
                block = datetime.strptime(f.read(), "%Y-%m-%d %H:%M:%S")
                now = datetime.now()
                if now > block:
                    return True
                else:
                    return False
        return True

    def _create_spamblocker_file(self, matches: str):
        with open(self._SPAM_BLOCKER_FILE, 'w') as f:
            now = datetime.now()
            mins,_,secs=matches.rpartition("m ")
            if not mins:
                mins = 0
            block = now + timedelta(minutes=int(mins), seconds=int(secs.replace("s","")))
            f.write(block.strftime("%Y-%m-%d %H:%M:%S"))

    def _parse_response(self, response: str) -> bool:
        if "That's not the right answer" in response:
            return False
        elif "You gave an answer too recently" in response:
            regex = re.compile(r"(\d+)m?\s+(\d+)s")
            try:
                matches = regex.search(response).group().strip()
            except AttributeError:
                matches = None
            if matches:
                self._create_spamblocker_file(matches)
                raise SystemExit(f'You gave an answer too recently, try again in {matches}')
            else:
                self._create_spamblocker_file("30s")
                raise SystemExit('You gave an answer too recently, try again later')
        elif "That's the right answer" in response:
            return True
        elif "Did you already complete it?" in response:
            self.logger.info('You already completed this puzzle.')
            return True

        raise Exception(f'Unknown response: {response}')

def generate():
    TEMPLATE = Path("./TEMPLATE_DAY.py").resolve()
    if not TEMPLATE.exists():
        print(f"Template file does not exist {TEMPLATE}, creating a new one")
        TEMPLATE.write_text("""import sys
from AOCRla.aoc import AOC

class puzzle(AOC):
    def __init__(self, open_browser: bool = False):
        super().__init__(open_browser=open_browser)
        self.input = self.get_input_data()

    def part1(self) -> int|None:
        pass

    def part2(self) -> int|None:
        pass

    def part1_oneliner(self) -> int|None:
        # [ line for line in open(f'./inputs/{self.YEAR}_{self.DAY}.txt').read().strip().split('\\n')]
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
