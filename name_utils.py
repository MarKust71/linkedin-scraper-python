# name_utils.py

def split_name(full_name: str) -> tuple[str, str]:
    """
    Dzieli pełne imię i nazwisko na imię i nazwisko.
    :param full_name:
    :return:
    """
    parts = full_name.strip().split()
    if len(parts) > 1:
        return ' '.join(parts[:-1]), parts[-1]
    else:
        return parts[0], ''
