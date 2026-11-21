class StatsDisplay:
    """
    Player statistics tracking and scoreboard/display methods.

    Tracks a list of statistics for each player (and puts it into a box score format), and prints the current score, inning, and lineups

    Attributes:

    game: The game class
    """
    def __init__(self, game):
        self.game = game

    def record_stat(self, player_name, metric, amount=1):
        # records game and series totals
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

        # Prints the number of the spot each batter is in, followed by their name and position
        for i, (player, position) in enumerate(roster_dict[team], start=1):
            print(f"{i}. {player} - {position}")

        print()

    def print_score(self):
        home_team, away_team = self.game.state["home_away"]
        print(f"\n{away_team} - {self.game.state['score'][away_team]}: {home_team} - {self.game.state['score'][home_team]}\n")

    def print_inning_description(self):
        # Dynamically tracks the current inning and the team batting
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

                hits = self.game.stats[player_name]["H"][idx]
                at_bats = self.game.stats[player_name]["AB"][idx]
                avg = (hits / at_bats) if at_bats > 0 else 0.0
                print(f"AVG: {avg:.3f}")
            print()

    def view_bases(self):
        b1, b2, b3 = self.game.state["bases"]

        print(f"\n1st base: {b1}\n2nd base: {b2}\n3rd base: {b3}\n")

    def series_mvp(self, team):

        eligible_players = (self.game.lineups[team] + self.game.bench[team] + self.game.removed_players[team])

        score_dict = {}
        for player, _pos in eligible_players:
            score = 0
            for metric, stat in self.game.stats[player].items():
                series_total = stat[1]
                if metric in ["H", "SB", "W"]:
                    score += (1 * series_total)
                elif metric == "RBI":
                    score += (2 * series_total)
                elif metric in ["CS", "SO", "E"]:
                    score -= (1 * series_total)
            score_dict[player] = score

        mvp = max(score_dict, key=score_dict.get)
        print(f"\n-----{mvp} takes home the World Series MVP Award!-----\n")
                
