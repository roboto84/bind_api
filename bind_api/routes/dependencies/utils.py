from datetime import date


def is_data_stale(stored_date: date) -> bool:
    if date.today().year > stored_date.year:
        return True
    elif date.today().month > stored_date.month:
        return True
    elif date.today().day > stored_date.day:
        return True
    else:
        return False
