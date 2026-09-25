def check_parrot_trouble_early_morning(is_talking: bool, hour: int) -> bool:
    return is_talking and (hour < 7 or hour > 20)


def check_parrot_trouble_late_night(is_talking: bool, hour: int) -> bool:
    return is_talking and (hour < 7 or hour > 20)


def check_parrot_safe_midday(is_talking: bool, hour: int) -> bool:
    return is_talking and (hour < 7 or hour > 20)


def check_parrot_quiet_early_morning(is_talking: bool, hour: int) -> bool:
    return is_talking and (hour < 7 or hour > 20)


def check_parrot_trouble_boundary_start(is_talking: bool, hour: int) -> bool:
    return is_talking and (hour < 7 or hour > 20)


def check_parrot_trouble_boundary_end(is_talking: bool, hour: int) -> bool:
    return is_talking and (hour < 7 or hour > 20)