import json


def json_update(data_name:str, increase: int = 1):
    with open('daily_stats.json', 'r') as file:
        daily_data = json.load(file)

    daily_data[f'{data_name}'] += increase

    with open('daily_stats.json', 'w') as file:
        json.dump(daily_data, file)