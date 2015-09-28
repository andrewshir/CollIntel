import csv
__author__ = 'Andrew'


class TeamData:
    def __init__(self):
        self.Wins = 0
        self.Draws = 0
        self.Defeats = 0
        self.Scores = 0


def _count_score(teams, rows):
    for row in rows:
        teamH = row[2]
        teamA = row[3]
        result = row[6]

        if teamH not in teams:
            teams[teamH] = TeamData()

        if teamA not in teams:
            teams[teamA] = TeamData()

        if result == "H":
            teams[teamH].Wins += 1
            teams[teamH].Scores += 2
            teams[teamA].Defeats += 1
        elif result == "A":
            teams[teamA].Wins += 1
            teams[teamA].Scores += 2
            teams[teamH].Defeats += 1
        elif result == "D":
            teams[teamA].Draws += 1
            teams[teamH].Draws += 1
            teams[teamA].Scores += 1
            teams[teamH].Scores += 1


def get_data(start_year=1993, end_year=2014):
    allteams = {}
    empty = None

    for index, year in enumerate(range(start_year, end_year + 1)):
        file = "C:\\Users\\Andrew\\Source\\Repos\\CollIntel\\Chapter 2\\football\\%s.csv" % year
        teams = {}

        with open(file, "rb") as f:
            reader = csv.reader(f)
            # skip header
            reader.next()
            _count_score(teams, reader)

        for team in teams:
            if team == "":
                continue

            if team in allteams:
                allteams[team].append(teams[team])
            else:
                list = []
                for y in range(0, index):
                    list.append(empty)
                list.append(teams[team])
                allteams[team] = list

        for team in allteams:
            if len(allteams[team]) <= index:
                allteams[team].append(empty)

    return allteams
