import datetime


def print_with_timestamp(text_after: str):
    now = datetime.datetime.now()
    time = f'[{now.hour:02}:{now.minute:02}:{now.second:02}] '
    print(time + text_after)