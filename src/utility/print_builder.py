import datetime


def better_print(text: str, time_diff: int = None):
    now = datetime.datetime.now()
    time = f'[{now.hour:02}:{now.minute:02}:{now.second:02}] '
    execution_time = ''
    if time_diff:
        execution_time = f' | {time_diff} ms'
    print(time + text + execution_time)