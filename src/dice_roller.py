import random


def roll_d20():
    return random.randint(1, 20)


def roll_advantage():
    return max(roll_d20(), roll_d20())


def roll_disadvantage():
    return min(roll_d20(), roll_d20())


def roll_save(roll: str, stats: dict, quiet: bool = False) -> bool:
    components = roll.split()
    # AS long as the check includes something like 12 strength we will attempt a roll
    for i in range(len(components)):
        try:
            num = int(components[i])
            stat_name = stats[components[i+1].lower()]
            modifier = get_modifier(stat_name)
            if not quiet:
                print(f"Rolling {stat_name} save ... ")
            save_roll = roll_d20() + modifier
            if save_roll >= num:
                if not quiet:
                    print(f"Success, roll: {save_roll}")
                    return True
            else:
                if not quiet:
                    print(f"Failure, roll: {save_roll}")
                    return False
        except ValueError:
            pass


def roll_dice(roll: str):
    # Split the expression into individual components
    components = roll.split()

    total = 0

    for i in range(len(components)):
        component = components[i]
        if 'd' in component:
            num_dice, num_sides = map(int, component.split('d'))
            rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
            total += sum(rolls)
        elif component.startswith('+'):
            total += int(components[i + 1])
        elif component.startswith('-'):
            total -= int(components[i + 1])
        elif component == 'x':
            total *= int(components[i + 1])
        elif not isinstance(int(component), int):
            print(f"Component not understood {component}")
    return total


def get_modifier(score: int):
    if score < 0 or score > 30:
        raise ValueError("Score must be between 0 and 30")

    modifiers = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    return modifiers[score // 2]
