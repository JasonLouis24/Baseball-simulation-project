"""
Pitching mechanics, count progression, and stolen base attempts.
"""
import random


class PitchingController:
    def __init__(self, game):
        self.game = game

    def pitch(self, team, cpu_team):
        weights = []

        if team == cpu_team:
            pitch_type = input("\n\nThrow a pitch! (1 - fastball, 2 - offspeed): ")

            if pitch_type == "2":
                weights = [39.0, 15.0, 14.5, 12.0, 15.0, 2.0, 2.5]
                print("\nThe pitcher throws an offspeed pitch...\n")
            else:
                weights = [33.0, 20.5, 17.5, 17.0, 9.0, 2.0, 1.0]
                print("\nThe pitcher throws a fastball...\n")

        else:
            input("\n\nPress enter for the pitch: ")

            if random.random() < 0.53:
                weights = [33.0, 20.5, 17.5, 17.0, 9.0, 2.0, 1.0]
                print("\nThe pitcher throws a fastball...\n")
            else:
                weights = [39.0, 15.0, 14.5, 12.0, 15.0, 2.0, 2.5]
                print("\nThe pitcher throws an offspeed pitch...\n")

        pitch_outcomes = [
            "ball",
            "foul",
            "ball in play",
            "called strike",
            "swing and miss",
            "hit by pitch",
            "wild pitch"
        ]

        return random.choices(pitch_outcomes, weights)[0]

    def process_pitch_result(self, result, balls, strikes):
        at_bat_result = ""

        if result == "ball":
            balls += 1
            print(f"The pitch is a ball. Count: {balls}-{strikes}")
        elif result == "foul":
            if strikes < 2:
                strikes += 1
                print(f"Foul ball. Count: {balls}-{strikes}")
            else:
                print(f"Foul ball. Count remains {balls}-{strikes}")
        elif result == "called strike":
            strikes += 1
            print(f"Called strike. Count: {balls}-{strikes}")
        elif result == "swing and miss":
            strikes += 1
            print(f"Swing and a miss! Count: {balls}-{strikes}")
        elif result == "ball in play":
            at_bat_result = "ball in play"

        return balls, strikes, at_bat_result

    def check_steal_attempt(self, team, cpu_team):
        b1, b2, b3 = self.game.state["bases"]

        factor = ""
        if team != cpu_team:
            if b1 or b2 or b3:
                factor = input("Call for steal? (1 - yes, 2 - no): ")

            odds_2b = 0.0
            odds_3b = 0.0

            if factor == "1":
                odds_2b = 1.0
                odds_3b = 1.0
            else:
                odds_2b = 0.08
                odds_3b = 0.02
        else:
            odds_2b = 0.08
            odds_3b = 0.02

        if b1 and not b2:
            if random.random() < odds_2b:
                print(f"{b1} takes off for second...")
                if random.random() < 0.77:
                    self.game.state["bases"][1] = b1
                    self.game.state["bases"][0] = None
                    self.game.display.record_stat(b1, "SB")
                    print(f"Safe! {b1} steals second base.")
                else:
                    self.game.state["bases"][0] = None
                    self.game.state["outs"] += 1
                    self.game.display.record_stat(b1, "CS")
                    print(f"{b1} is caught stealing! {self.game.state['outs']} outs.\n")
        if b2 and not b3:
            if random.random() < odds_3b:
                print(f"{b2} takes off for third...")
                if random.random() < 0.80:
                    self.game.state["bases"][2] = b2
                    self.game.state["bases"][1] = None
                    self.game.display.record_stat(b2, "SB")
                    print(f"Safe! {b2} steals third base.")
                else:
                    self.game.state["bases"][1] = None
                    self.game.state["outs"] += 1
                    self.game.display.record_stat(b2, "CS")
                    print(f"{b2} is caught stealing! {self.game.state['outs']} outs.\n")
