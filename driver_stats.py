import datetime
from collections import defaultdict
from dateutil.parser import parse

import requests
import xmltodict
import seaborn as sns
import matplotlib.pyplot as plt


def get_schedule(year: int) -> dict[int, tuple[str, datetime.date]]:
    url = f"http://ergast.com/api/f1/{year}"
    response = requests.request("GET", url)
    data = xmltodict.parse(response.text)

    schedule: dict[int, tuple[str, datetime.date]] = {}
    events = data['MRData']['RaceTable']['Race']

    for race in events:
        event_number = int(race['@round'])
        name = race['Circuit']['@circuitId']
        date = parse(race['Date']).date()
        schedule[event_number] = name, date

    return schedule


def get_results(year: int, max_round: int) -> dict[dict[str, list[int]]]:
    result: dict[dict[str, list[int]]] = defaultdict(list)
    for event in range(max_round):
        response = requests.request("GET", f'http://ergast.com/api/f1/{year}/{event + 1}/driverStandings')
        data = xmltodict.parse(response.text)

        standings = data['MRData']['StandingsTable']['StandingsList']['DriverStanding']

        for driver in standings:
            name = driver['Driver']['@driverId']
            points = driver['@points']
            result[name].append(int(points))
    return result


def plot(result: dict[dict[str, list[int]]], rounds: list[str]) -> None:
    for name, points in result.items():
        if len(points) != len(rounds):
            print(name)
            continue

        sns.lineplot(x=rounds, y=points, label=name)

    plt.show()


def main():
    year = 2022

    schedule = get_schedule(year)

    races_run: list[str] = []
    for index, (name, date) in schedule.items():
        if date < datetime.date.today():
            races_run.append(name)

    result = get_results(year, len(races_run))
    plot(result, races_run)

    print(schedule)


if __name__ == '__main__':
    main()
