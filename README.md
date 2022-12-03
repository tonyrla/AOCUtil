# AOCUtil
Input downloader for Advent of Code

## Usage
### Session cookie to fetch inputs and submit answers
*  Get your session cookie from [Advent of Code](https://adventofcode.com/) and save it in [./data/.secret_session_cookie](./data/.secret_session_cookie)
*  Inputs are cached to ./inputs, a session cookie lasts for a month, and that's how long the inputs are valid.
*  Inputs and answers are fetched and submitted by parsing the folder structure and filenames, so make sure they are named correctly.
   * `20\d{2}` for the year. Yes, you can break this. Do you have to?
   * `[^0-9]` for the day from the filename. `666_superclever_day01` is not the intended usage <3
   * `aoc2022/day01.py`, `aoc/python/2022/day01.py` etc.

To generate the puzzle .py files for every day:
```bash
python -m AOCRla.aoc
```

To run a specific day's puzzle:
```bash
python ./dayXX.py
```

To open a web browser with the correct puzzle selected, add anything after the python file:
```bash
python ./day01.py  asdf
```

## Submitting answers
```python
    part1 = p.part1()
    part2 = p.part2()

    p.post_answer(1, part1)
    p.post_answer(2, part2)
```






## Output examples:
```python
    print(p.get_input_data()) 
    # A Y
    # B Y
    # B Z
    # B X
    # 
    # C X
    # C Y
```
```python
    # defaults to str
    for sub in p.get_input_data_sublist():
        print(sub)                                  
        # ['A', 'Y'], ['B', 'Y'], ['B', 'Z'], ['B', 'X'], [], ['C', 'X'], ['C', 'Y']
    print (next(p.get_input_data_sublist()))        
    # ['A', 'Y']

    # Type to ord
    for sub in p.get_input_data_sublist(ord):
        print(sub)                                  
        # [65, 89], [66, 89], [66, 90], [66, 88], [], [67, 88], [67, 89]
    print (next(p.get_input_data_sublist(ord)))     
    # [65, 89]
```
```python
    print(p.get_input_data_as_grid(ord))            
    # [[65, 32, 89], [66, 32, 89], [66, 32, 90], [66, 32, 88], [], [67, 32, 88], [67, 32, 89]]
    print(p.get_input_data_as_grid())               
    # [['A', ' ', 'Y'], ['B', ' ', 'Y'], ['B', ' ', 'Z'], ['B', ' ', 'X'], [], ['C', ' ', 'X'], ['C', ' ', 'Y']]
```
```python
    print(p.get_input_data_as_splitlist())          
    # [['A', 'Y'], ['B', 'Y'], ['B', 'Z'], ['B', 'X'], [], ['C', 'X'], ['C', 'Y']]
    print(p.get_input_data_as_splitlist(ord))       
    # [[65, 89], [66, 89], [66, 90], [66, 88], [], [67, 88], [67, 89]]
```

```python
   print(p.get_input_data_as_int_list())               
   # [1, 2, 3, 4, 5]
```