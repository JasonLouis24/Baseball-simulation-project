"""
Core BaseballGame class and at-bat, inning, game, and series flow.
"""
from rosters import LINEUPS, BENCH
from stats import StatsDisplay
from pitching import PitchingController
from fielding import FieldingController
from management import TeamManager


class BaseballGame:
    def __init__(self, user_team, cpu_team):
        self.state = {
            "game": 1,
            "top_of_inning": True,
            "inning": 1,
            "outs": 0,
            "bases": [None, None, None],
            "score": {
                user_team: 0,
                cpu_team: 0
            },
            "home_away": [user_team, cpu_team],
            "fielding_team": "",
            "pitch_type": 0
        }

        self.lineups = {
            team: [player[:] for player in roster]
            for team, roster in LINEUPS.items()
        }
        self.bench = {
            team: [player[:] for player in roster]
            for team, roster in BENCH.items()
        }

        self.removed_players = {
            "MIL": [],
            "TB": []
        }

        # Initialize player stats keyed by player name: [game_stat, series_stat]
        self.stats = {}
        for team_name, roster in self.lineups.items():
            full_roster = self.lineups[team_name] + self.bench[team_name]
            for player_name, position in full_roster:
                self.stats[player_name] = {
                    "AB": [0, 0],   # At Bats
                    "H": [0, 0],    # Hits
                    "1B": [0, 0],   # Singles
                    "2B": [0, 0],   # Doubles
                    "3B": [0, 0],   # Triples
                    "HR": [0, 0],   # Home Runs
                    "RBI": [0, 0],  # Runs Batted In
                    "BB": [0, 0],   # Walks
                    "SO": [0, 0],   # Strikeouts
                    "SB": [0, 0],   # Stolen Bases
                    "CS": [0, 0],   # Caught Stealing
                    "E": [0, 0]     # Errors
                }

        self.batter_index = {
            "MIL": 0,
            "TB": 0
        }

        self.display = StatsDisplay(self)
        self.pitching = PitchingController(self)
        self.fielding = FieldingController(self)
        self.manager = TeamManager(self)

    def at_bat(self, team, cpu_team, user_team):
        b1, b2, b3 = self.state["bases"]

        batter = self.batter_index[team]
        player, position = self.lineups[team][batter]

        option = input("\n\n---Enter main menu? (1 - yes, 2 - no)---: ")

        if option == "1":
            self.manager.menu(user_team)

        avg = 0.0

        hits_float = float(self.stats[player]["H"][1])
        ab_float = self.stats[player]["AB"][1]

        if self.stats[player]["AB"][1] != 0:
            avg = hits_float / ab_float
        else:
            avg = hits_float

        print(f"\n\n----Now batting: {position} {player} ({self.stats[player]['H'][0]} - {self.stats[player]['AB'][0]}, {avg:.3f} AVG)----")

        balls = 0
        strikes = 0

        while balls < 4 and strikes < 3:
            self.pitching.check_steal_attempt(team, cpu_team)

            if self.state["outs"] >= 3:
                break

            result = self.pitching.pitch(team, cpu_team)

            balls, strikes, at_bat_result = self.pitching.process_pitch_result(result, balls, strikes)

            if at_bat_result == "ball in play":
                self.fielding.in_play(team)
                break

            if result == "hit by pitch":
                print(f"{player} is hit by the pitch!")

                if b1 and b2 and b3:
                    self.state["score"][team] += 1
                    self.display.record_stat(player, "RBI")
                    print(f"{b3} scores.")
                    self.display.print_score()
                    self.state["bases"][2] = b2
                    self.state["bases"][1] = b1

                elif b1 and b2:
                    self.state["bases"][2] = b2
                    self.state["bases"][1] = b1

                elif b1:
                    self.state["bases"][1] = b1

                self.state["bases"][0] = player
                break

            if result == "wild pitch" and b1 or b2 or b3:
                print("Wild pitch!")

                if b3:
                    self.state["score"][team] += 1
                    print(f"{b3} scores.")
                    self.display.print_score()

                if b2:
                    self.state["bases"][2] = b2
                    print(f"{b2} advances to third.")

                if b1:
                    self.state["bases"][1] = b1
                    print(f"{b1} advances to second.")

                self.state["bases"][0] = None

                balls += 1
                print(f"Count: {balls}-{strikes}")

            if balls == 4:
                print(f"{player} walks.")
                self.display.record_stat(player, "BB")

                if b1 and b2 and b3:
                    self.state["score"][team] += 1
                    self.display.record_stat(player, "RBI")
                    print(f"{b3} scores.")
                    self.display.print_score()
                    self.state["bases"][2] = b2
                    self.state["bases"][1] = b1
                elif b1 and b2:
                    self.state["bases"][2] = b2
                    self.state["bases"][1] = b1
                elif b1:
                    self.state["bases"][1] = b1

                self.state["bases"][0] = player
                break

            if strikes == 3:
                self.display.record_stat(player, "AB")
                self.display.record_stat(player, "SO")
                self.state["outs"] += 1
                print(f"{player} is out on strikes. {self.state['outs']} outs.")
                break

        self.batter_index[team] = (batter + 1) % 9

    def play_half_inning(self, team, cpu_team, user_team):
        self.state["bases"] = [None, None, None]
        self.state["outs"] = 0

        home_team, away_team = self.state["home_away"]

        while self.state["outs"] < 3:
            self.at_bat(team, cpu_team, user_team)

            if not self.state["top_of_inning"] and self.state["inning"] >= 9:
                if self.state["score"][home_team] > self.state["score"][away_team]:
                    break

    def play_full_game(self, cpu_team, user_team):
        away_team = self.state["home_away"][1]
        home_team = self.state["home_away"][0]

        for team in self.state["home_away"]:
            self.display.print_batting_order(team, False)

        while self.state["inning"] <= 9 or self.state["score"][away_team] == self.state["score"][home_team]:
            # Top of the inning (Away team bats)
            self.state["top_of_inning"] = True
            self.display.print_inning_description()
            self.play_half_inning(away_team, cpu_team, user_team)

            if self.state["inning"] >= 9:
                if self.state["score"][home_team] > self.state["score"][away_team]:
                    break

            # Bottom of the inning (Home team bats)
            self.state["top_of_inning"] = False
            self.display.print_inning_description()
            self.play_half_inning(home_team, cpu_team, user_team)

            self.state["inning"] += 1

        print("\n----- GAME OVER -----")
        print(f"Final Score -> {home_team}: {self.state['score'][home_team]}, {away_team}: {self.state['score'][away_team]}")

    def play_full_series(self, cpu_team, user_team):
        wins = {
            "MIL": 0,
            "TB": 0
        }

        total_gp = 0

        while wins["MIL"] != 4 and wins["TB"] != 4:
            self.state["inning"] = 1
            self.state["outs"] = 0
            self.state["bases"] = [None, None, None]
            self.state["top_of_inning"] = True

            away_team = self.state["home_away"][1]
            home_team = self.state["home_away"][0]

            self.play_full_game(cpu_team, user_team)
            if self.state["score"][home_team] > self.state["score"][away_team]:
                wins[home_team] += 1
            else:
                wins[away_team] += 1

            print(f"{away_team}: {wins[away_team]}, {home_team}: {wins[home_team]}")

            for team in self.state["score"]:
                self.state["score"][team] = 0

            for player in self.stats:
                for metric in self.stats[player]:
                    self.stats[player][metric][0] = 0

            total_gp += 1

            if total_gp == 2:
                self.state["home_away"] = ["TB", "MIL"]

            if total_gp == 5:
                self.state["home_away"] = ["TB", "MIL"]

        if wins["MIL"] > wins["TB"]:
            print("\n------------\nTHE MILUAKEE BREWERS HAVE WON THE WORLD SERIES!\n---------")
        else:
            print("\n------------\nTHE TAMPA BAY RAYS HAVE WON THE WORLD SERIES!\n---------")
