# Generate limboole code for the SAT encoding of game from task
#
# Field is numbered 1 to 9, left to right, up to bottom.
# Empty field corresponds to value 0, others - to value 1 through 8.
# State variables:
# For each field - 9 variables which encode which of the values 0 through 8 is on the field.
# Naming - s{t}_f{i}_n{j}, where {i} - field number, {j} - stone number, {t} - number of state (time).
# In total 81 state variables.
#
# End state would be [1, 2, 3, 4, 5, 6, 7, 8, 0]


import argparse
from typing import List
from itertools import product, combinations

# constants
POSSIBLE_MOVES = [
    (1, 2),
    (1, 4),
    (2, 1),
    (2, 5),
    (2, 3),
    (3, 2),
    (3, 6),
    (4, 1),
    (4, 5),
    (4, 7),
    (5, 2),
    (5, 6),
    (5, 8),
    (5, 4),
    (6, 3),
    (6, 5),
    (6, 9),
    (7, 4),
    (7, 8),
    (8, 7),
    (8, 5),
    (8, 9),
    (9, 8),
    (9, 6),
]


def generate_state_program(state: List[int], step: int = 0) -> List[str]:
    # Generates limboole state program from list
    result = list()

    def generate_prefixes(val: bool):
        return "" if val else "!"

    for field in range(1, 10):
        cur_field_line = ""
        for stone in range(9):
            cur_variable = f"s{step}_f{field}_n{stone}"
            cur_field_line += (
                generate_prefixes(state[field - 1] == stone) + cur_variable + " & "
            )
        # remove last conjunction from the line
        cur_field_line = cur_field_line[:-3]
        result.append(cur_field_line)
    return result


def generate_action_changes(step: int) -> List[str]:
    # Generates action changes (action -> (prerequisites & results))
    # for specific time step
    result = list()
    for ip, ipp in POSSIBLE_MOVES:
        for j in range(1, 9):
            left_side = "mv{step}_s{j}_p{ip}{ipp}"
            precondition = "(s{step}_f{ip}_n{j} & s{step}_f{ipp}_n0)"
            effect = "(s{step1}_f{ipp}_n{j} & s{step1}_f{ip}_n0)"
            action_change = f"({left_side} -> ({precondition} & {effect}))".format(
                step=step, step1=step + 1, ip=ip, ipp=ipp, j=j
            )
            result.append(action_change)
    return result


def generate_one_action_condition(step: int) -> List[str]:
    # Generates condition that guaranties
    # that one and only one action performs at each step
    result = list()
    action_configs = product(POSSIBLE_MOVES, range(1, 9))
    action_config_names = list(
        map(lambda inp: f"mv{step}_s{inp[1]}_p{inp[0][0]}{inp[0][1]}", action_configs)
    )
    # clause for at least one action performed
    atleast_one_clause = " | ".join(action_config_names.copy())
    result.append("(" + atleast_one_clause + ")")
    # clause for <2 actions performed
    action_combos = combinations(action_config_names, r=2)
    lessthen_two_clause = " & ".join(
        map(lambda c: f"(!{c[0]} | !{c[1]})", action_combos)
    )
    result.append("(" + lessthen_two_clause + ")")
    return result


def generate_frame_axioms(step: int) -> List[str]:
    result = list()
    # handling frame axioms for s{t}_f{i}_n0
    # case of zero is unique and should be handled differently
    for pos, stone in product(range(1, 9), range(0, 8)):
        # generate states receiving and getting rid of specific value
        left_side_out = "(s{step}_f{pos}_n{stone} & !s{step1}_f{pos}_n{stone})".format(
            step=step, step1=step + 1, pos=pos, stone=stone
        )
        left_side_to = "(!s{step}_f{pos}_n{stone} & s{step1}_f{pos}_n{stone})".format(
            step=step, step1=step + 1, pos=pos, stone=stone
        )
        # choose actions which go into and from the position
        actions_to_pos = filter(lambda move: move[1] == pos, POSSIBLE_MOVES)
        actions_out_pos = filter(lambda move: move[0] == pos, POSSIBLE_MOVES)
        if stone == 0:
            action_confs_to = product(actions_to_pos, range(1, 9))
            action_config_names_to = list(
                map(
                    lambda inp: f"mv{step}_s{inp[1]}_p{inp[0][0]}{inp[0][1]}",
                    action_confs_to,
                )
            )
            possible_actions_to = " | ".join(action_config_names_to)
            res_out = f"({left_side_out} -> ({possible_actions_to}))"
            action_confs_out = product(actions_out_pos, range(1, 9))
            action_config_names_out = list(
                map(
                    lambda inp: f"mv{step}_s{inp[1]}_p{inp[0][0]}{inp[0][1]}",
                    action_confs_out,
                )
            )
            possible_actions_out = " | ".join(action_config_names_out)
            res_to = f"({left_side_to} -> ({possible_actions_out}))"
        else:
            action_config_names_to = list(
                map(lambda inp: f"mv{step}_s{stone}_p{inp[0]}{inp[1]}", actions_to_pos)
            )
            possible_actions_to = " | ".join(action_config_names_to)
            res_to = f"({left_side_to} -> ({possible_actions_to}))"
            action_config_names_out = list(
                map(lambda inp: f"mv{step}_s{stone}_p{inp[0]}{inp[1]}", actions_out_pos)
            )
            possible_actions_out = " | ".join(action_config_names_out)
            res_out = f"({left_side_out} -> ({possible_actions_out}))"
        result.append(res_to)
        result.append(res_out)
    return result


def print_program(program: List[str]):
    print(" &\n".join(program.copy()))


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser(
        prog="puzzle_sat_encoding", description="Generate SAT encoding for a game"
    )
    parser.add_argument(
        "starting_field", help="List representing starting field of the game"
    )
    parser.add_argument(
        "number_of_steps",
        help="Number of steps in which game should be completed",
        type=int,
    )
    args = parser.parse_args()
    # generate starting state part of a program
    starting_field = list(map(int, args.starting_field.strip("][").split(", ")))
    program = generate_state_program(starting_field)
    program.insert(0, "% Initial State")
    # generate end state
    end_state = generate_state_program(
        [1, 2, 3, 4, 5, 6, 7, 8, 0], step=args.number_of_steps
    )
    end_state.insert(0, "% End State")
    program.extend(end_state)
    # generate changes of action for each step
    program.append("% Changes of action")
    for step in range(args.number_of_steps):
        action_change = generate_action_changes(step=step)
        action_change.insert(0, f"% Step {step + 1}")
        program.extend(action_change)
    # generate one action conditions
    program.append("% One and only action conditions")
    for step in range(args.number_of_steps):
        action_cond = generate_one_action_condition(step=step)
        action_cond.insert(0, f"% Step {step + 1}")
        program.extend(action_cond)
    # generate frame axioms
    program.append("% Frame axioms")
    for step in range(args.number_of_steps):
        action_cond = generate_frame_axioms(step=step)
        action_cond.insert(0, f"% Step {step + 1}")
        program.extend(action_cond)
    print_program(program)
