"""
Player statistics tracking and scoreboard/display methods.
"""


class StatsDisplay:
    def __init__(self, game):
        self.game = game

    def record_stat(self, player_name, metric, amount=1):
        self.game.stats[player_name][metric][0] += amount
        self.game.stats[player_name][metric][1] += amount

    def print_batting_order(self, team, bench=False):
        heading = ""
        roster_dict = None
        if bench == False:
            heading = "Batting Order"
            roster_dict = self.game.lineups
        else:
            heading = "Bench"
            roster_dict = self.game.bench

        print(f"\n----- {team} {heading} -----")

        for i, (player, position) in enumerate(roster_dict[team], start=1):
            print(f"{i}. {player} - {position}")

        print()

    def print_score(self):
        home_team, away_team = self.game.state["home_away"]
        print(f"\n{away_team} - {self.game.state['score'][away_team]}: {home_team} - {self.game.state['score'][home_team]}\n")

    def print_inning_description(self):
        inning = self.game.state["inning"]
        if inning % 10 == 1 and inning != 11:
            inning_in_word = f"{inning}st"
        elif inning % 10 == 2 and inning != 12:
            inning_in_word = f"{inning}nd"
        elif inning % 10 == 3 and inning != 13:
            inning_in_word = f"{inning}rd"
        else:
            inning_in_word = f"{inning}th"

        home_team, away_team = self.game.state["home_away"]
        if self.game.state["top_of_inning"]:
            print(f"\n--------Top of the {inning_in_word}--------\n")
            print(f"{away_team} batting:\n")
            self.print_score()
        else:
            print(f"\n--------Bottom of the {inning_in_word}--------\n")
            print(f"{home_team} batting:\n")
            self.print_score()

    def view_box_score(self, series=False):
        idx = 1 if series else 0
        label = "Series Totals" if series else "Box Score"

        full_batters = {}

        for team in self.game.lineups:
            full_batters[team] = (self.game.lineups[team] + self.game.bench[team] + self.game.removed_players[team])

        for team_name, roster in full_batters.items():
            print(f"\n----- {team_name} {label} -----")
            for player_name, position in roster:
                print(f"{position} {player_name} | ", end="")
                for metric, stat in self.game.stats[player_name].items():
                    print(f"{metric}: {stat[idx]}", end="  ")

                if self.game.stats[player_name]["AB"] == [0, 0]:
                    self.game.stats[player_name]["AB"] = [1, 1]
                print(f"AVG: {self.game.stats[player_name]['H'][1] / self.game.stats[player_name]['AB'][1]:.3f}")
                self.game.stats[player_name]["AB"] = [0, 0]
                print()
            print()

    def view_bases(self):
        b1, b2, b3 = self.game.state["bases"]

        print(f"\n1st base: {b1}\n2nd base: {b2}\n3rd base: {b3}\n")
