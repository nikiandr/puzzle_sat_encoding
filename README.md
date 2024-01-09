# puzzle_sat_encoding

SAT encoding of 3 by 3 Sliding Puzzle

## Idea behind the project

Idea behind the project is to generate boolean logic conjunctive form which
describes the game. This way when we check the generated boolean formula for
satisfiability we can prove that the particular game setup is solveable and the
set of the variables which correspond to the solution of the formula can be
translated to the solution of the game.

## Game description and implementation details

See [task file](./task.pdf) for the description of the task and the puzzle
itself.

See [report file](./Project_1_Fordui.pdf) for the detailed description of
implementation and example of work of the solution.

## Usage

The program was developed and tested on the Python 3.11.6 and it doesn't use any
non-standard libraries. It will also probably run on earlier Python 3 versions
but I am not sure about it, do it at your own risk.

Script can be used like this:

```bash
usage: puzzle_sat_encoding.py [-h] starting_field number_of_steps

Generate SAT encoding for a 3x3 sliding puzzle

positional arguments:
  starting_field   List representing starting field of the game
  number_of_steps  Number of steps in which game should be completed

options:
  -h, --help       show this help message and exit
```

Program generate conjunctive form in **limboole** format which means you can
pipe it straight into limboole to generate solution:

```bash
python puzzle_sat_encoding.py | limboole
```

You can also generate code and put it into file for future uses:

```bash
python puzzle_sat_encoding.py > code.limboole
```
