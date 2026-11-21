import random


class FieldingController:
    """
    This class determines the result of a ball hit in play

    Handles balls in play outcomes, hit resolution, basic outs, double plays, and errors.

    Attributes: 

    game: The game class needed for the flow and calculation of the result
    
    """
    def __init__(self, game):
        self.game = game

    def get_in_play_result(self):
        in_play_outcomes = ["ground ball", "fly ball", "line drive", "pop fly"]
        weights = [44, 24, 21, 11]

        outcome = random.choices(in_play_outcomes, weights)[0]
        print(f"The batter hits a {outcome}...")

        outcome_dict = {
            "fly ball": {"out": 63.5, "single": 4.5, "double": 5.5, "triple": 0.5, "home run": 26.0},
            "ground ball": {"out": 78.0, "single": 18.5, "double": 3.3, "triple": 0.2, "home run": 0.0},
            "pop fly": {"out": 99.5, "single": 0.5, "double": 0.0, "triple": 0.0, "home run": 0.0},
            "line drive": {"out": 31.5, "single": 39.0, "double": 21.5, "triple": 1.5, "home run": 6.5},
        }

        result_type = list(outcome_dict[outcome].keys())
        result_weight = list(outcome_dict[outcome].values())

        in_play_result = random.choices(result_type, result_weight)[0]
        return in_play_result, outcome

    def get_defender_name(self, target_position):
        # Helper function that returns the name and position of a requested fielder
        for name, pos in self.game.lineups[self.game.state["fielding_team"]]:
            if pos == target_position:
                return name, pos

    def get_fielder_and_location(self, batting_team, in_play_result, outcome):
        # randomly assigns a fielding position and name, used in the result for a ball in play

        home_team, away_team = self.game.state["home_away"]
        self.game.state["fielding_team"] = home_team if batting_team == away_team else away_team

        out_location_weights = {
            "ground ball": (["1B", "2B", "3B", "SS", "C"], [22, 24, 22, 24, 3]),
            "fly ball":    (["LF", "CF", "RF"], [32, 36, 32]),
            "line drive":  (["1B", "2B", "3B", "SS", "LF", "CF", "RF"], [12, 15, 12, 15, 15, 16, 15]),
            "pop fly":     (["1B", "2B", "3B", "SS", "2B", "C"], [20, 20, 20, 20, 10, 10])
        }

        hit_location_weights = {
            "ground ball": (["LF", "CF", "RF"], [34, 32, 34]),
            "fly ball":    (["LF", "CF", "RF"], [32, 36, 32]),
            "line drive":  (["LF", "CF", "RF", "1B", "3B"], [30, 34, 30, 3, 3]),
            "pop fly":     (["LF", "CF", "RF", "2B", "SS"], [25, 25, 25, 12.5, 12.5])
        }

        position, weight = out_location_weights[outcome] if in_play_result == "out" else hit_location_weights[outcome]
        chosen_position = random.choices(position, weight)[0]

        fielder_name, fielder_position = self.get_defender_name(chosen_position)

        return fielder_position, fielder_name

    def in_play(self, team):
    
        """ 
        Handles logic related to errors and hits, 
        In those areas, it tracks bases, calculates runner advancement, updates stats and prints result
        """
        in_play_result, outcome = self.get_in_play_result()

        batter = self.game.batter_index[team]
        player, position = self.game.lineups[team][batter]

        pos, fielder_name = self.get_fielder_and_location(
            team, in_play_result, outcome
        )

        # Calculates if an error occurs on a given ball in play

        error_type, error_chance, target_pos = self.get_error_profile(pos, outcome)

        if random.random() < error_chance:
            self.handle_error(team, player, outcome, pos, fielder_name, error_type, target_pos)
            return

        # Specifically tracks different cases of an out using specialized functions
        if in_play_result == "out":
            if outcome == "ground ball":
                self.handle_ground_ball_dp(team, player, in_play_result, outcome)
            elif outcome == "line drive":
                self.handle_lineout_gp(team, player, in_play_result, outcome)
            elif outcome == "fly ball":
                self.handle_fly_ball(team, player, in_play_result, outcome)
            else:
                self.handle_popup(team, player, in_play_result, outcome)
            return in_play_result

        b1, b2, b3 = self.game.state["bases"]
        self.game.state["bases"] = [None, None, None]
        self.game.display.record_stat(player, "AB")

        if in_play_result == "single":
            self.game.display.record_stat(player, "H")
            self.game.display.record_stat(player, "1B")
            print(f"{player} singles on a {outcome} to {pos} {fielder_name}.")

            if b3:
                self.game.display.record_stat(player, "RBI")
                self.game.state["score"][team] += 1
                print(f"{b3} scores.")
                self.game.display.print_score()

            if b2:
                if random.random() < 0.96:
                    self.game.display.record_stat(player, "RBI")
                    self.game.state["score"][team] += 1
                    print(f"{b2} scores.")
                    self.game.display.print_score()
                else:
                    self.game.state["outs"] += 1
                    print(f"{b2} is out, trying for home!")

            if b1:
                if pos != "LF":
                    if random.random() < 0.75:
                        self.game.state["bases"][1] = b1
                        print(f"{b1} to second.")
                    else:
                        self.game.state["bases"][2] = b1
                        print(f"{b1} to third.")
                else:
                    self.game.state["bases"][1] = b1
                    print(f"{b1} to second.")

            self.game.state["bases"][0] = player
            print(f"{player} to first.")

        elif in_play_result == "double":
            self.game.display.record_stat(player, "H")
            self.game.display.record_stat(player, "2B")
            print(f"{player} doubles on a {outcome} to {pos} {fielder_name}.")

            rbis = 0
            for runner in [b2, b3]:
                if runner:
                    rbis += 1
                    self.game.state["score"][team] += 1
                    print(f"{runner} scores.")
                    self.game.display.print_score()

            if b1:
                adv_outcome = random.choices(["scores", "third", "out"], [41, 56, 3])[0]
                if adv_outcome == "scores":
                    rbis += 1
                    self.game.state["score"][team] += 1
                    print(f"{b1} scores.")
                    self.game.display.print_score()
                elif adv_outcome == "third":
                    self.game.state["bases"][2] = b1
                    print(f"{b1} to third.")
                else:
                    self.game.state["outs"] += 1
                    print(f"{b1} is out.")

            self.game.display.record_stat(player, "RBI", rbis)
            self.game.state["bases"][1] = player
            print(f"{player} to second.")

        elif in_play_result == "triple":
            self.game.display.record_stat(player, "H")
            self.game.display.record_stat(player, "3B")
            print(f"{player} triples on a {outcome} to {pos} {fielder_name}.")

            rbis = 0
            for runner in [b1, b2, b3]:
                if runner:
                    rbis += 1
                    self.game.state["score"][team] += 1
                    print(f"{runner} scores.")
                    self.game.display.print_score()

            self.game.display.record_stat(player, "RBI", rbis)
            self.game.state["bases"][2] = player
            print(f"{player} to third.")

        elif in_play_result == "home run":
            self.game.display.record_stat(player, "H")
            self.game.display.record_stat(player, "HR")
            print(f"{player} hits a home run!")

            rbis = 1
            self.game.state["score"][team] += 1
            print(f"{player} scores.")
            self.game.display.print_score()
            for runner in [b1, b2, b3]:
                if runner:
                    rbis += 1
                    self.game.state["score"][team] += 1
                    print(f"{runner} scores.")
                    self.game.display.print_score()
            self.game.display.record_stat(player, "RBI", rbis)

        return in_play_result

    def handle_ground_ball_dp(self, team, batter, in_play_result, outcome):
        """
        Tracks Double play, fielder's choice, and routine groundout oppurtunities
        Uses specialized fielder positing to make logic model real world situations
        
        """
        pos, fielder_name = self.get_fielder_and_location(team, in_play_result, outcome)
        b1, b2, b3 = self.game.state["bases"]
        first_b_name, first_b_pos = self.get_defender_name("1B")

        # 1. Double Play
        if self.game.state["outs"] < 2 and b1 and pos in ["1B", "2B", "3B", "SS"] and random.random() < 0.45:
            self.game.display.record_stat(batter, "AB")

            # Determine whether the double play uses two or three fielders
            can_two_fielders = pos in ["1B", "2B", "SS"]
            can_three_fielders = True

            chosen_dp = "three_fielders"

            # A double play with only two fielders has a large chance of occuring if the 1B is involved
            if can_two_fielders and can_three_fielders:
                two_fielder_chance = 0.25 if pos == "1B" else 0.10

                if random.random() < two_fielder_chance:
                    chosen_dp = "two_fielders"

            # Handle runners advancing and scoring
            run_scored = False

            if b3:
                run_scored = True
                self.game.state["score"][team] += 1
                self.game.display.record_stat(batter, "RBI")
                self.game.display.print_score()

            self.game.state["outs"] += 2

            self.game.state["bases"] = [None, None, b2]

            run_message = f"{b3} scores. " if run_scored else ""
            advance_message = f"{b2} to third. " if b2 else ""

            # Establishes the middle part of the message based on the number and name/position of the fielders involved
            if chosen_dp == "two_fielders":
                if pos == "1B":
                    ss_name, ss_pos = self.get_defender_name("SS")
                    dp_comment = f"{pos} {fielder_name} to {ss_pos} {ss_name}. "
                else:
                    dp_comment = f"{pos} {fielder_name} to {first_b_pos} {first_b_name}. "

            else:
                dp_three_fielders_name, dp_three_fielders_pos = self.get_defender_name("2B") if pos == "3B" else self.get_defender_name("SS")
                dp_comment = f"{pos} {fielder_name} to {dp_three_fielders_pos} {dp_three_fielders_name} to {first_b_pos} {first_b_name}. "

            print(f"{batter} grounds into a double play, {dp_comment}{run_message}{advance_message}{b1} out at second. {self.game.state['outs']} outs.")

        # 2. Fielder's choice logic
        # Requires at least a runner on first and less than two outs (two outs will be a routine ground ball)
        elif self.game.state["outs"] < 2 and b1:
            self.game.state["outs"] += 1
            self.game.display.record_stat(batter, "AB")

            # Bases loaded: Lead runner is b3, throw goes home to force them out
            if b1 and b2 and b3:
                c_name, c_pos = self.get_defender_name("C")
                self.game.state["bases"] = [batter, b1, b2]
                print(
                    f"{batter} reaches on a fielder's choice, {pos} {fielder_name} to {c_pos} {c_name}. "
                    f"{b3} out at home. {self.game.state['outs']} out(s)."
                )

            # Runners on 1st and 2nd: Lead runner is b2, throw goes to 3rd to force them out
            elif b1 and b2 and not b3:
                covering_name, covering_pos = self.get_defender_name("3B")
                self.game.state["bases"] = [batter, b1, None]
                print(
                    f"{batter} reaches on a fielder's choice, {pos} {fielder_name} to {covering_pos} {covering_name}. "
                    f"{b2} out at third. {self.game.state['outs']} out(s)."
                )

            # Runners on 1st and 3rd: Throw goes to 2nd to force b1; b3 scores on the play
            elif b1 and b3 and not b2:
                covering_pos = "2B" if pos in ["3B", "SS", "P", "C"] else "SS"
                covering_name, covering_pos = self.get_defender_name(covering_pos)

                self.game.state["score"][team] += 1
                self.game.display.record_stat(batter, "RBI")
                self.game.display.print_score()
                self.game.state["bases"] = [batter, None, None]

                print(
                    f"{batter} reaches on a fielder's choice, {pos} {fielder_name} to {covering_pos} {covering_name}. "
                    f"{b3} scores. {b1} out at second. {self.game.state['outs']} out(s)."
                )

            # Runner on 1st only: Lead runner is b1, throw goes to 2nd to force them out
            else:
                covering_pos = "2B" if pos in ["3B", "SS", "P", "C"] else "SS"
                covering_name, covering_pos = self.get_defender_name(covering_pos)
                self.game.state["bases"] = [batter, None, None]

                print(
                    f"{batter} reaches on a fielder's choice, {pos} {fielder_name} to {covering_pos} {covering_name}. "
                    f"{b1} out at second. {self.game.state['outs']} out(s)."
                )

        # 3. Routine groundout
        else:
            self.game.state["outs"] += 1
            self.game.display.record_stat(batter, "AB")

            if pos == "1B":
                out_message = f"{batter} grounds out to {pos} {fielder_name}."
            else:
                out_message = f"{batter} grounds out, {pos} {fielder_name} to {first_b_pos} {first_b_name}."

            if self.game.state["outs"] < 3:
                messages = [out_message]

                if b3:
                    messages.append(f"{b3} holds at third.")

                if b2:
                    messages.append(f"{b2} holds at second.")

                if b1 and not b2:
                    b2 = b1
                    b1 = None
                    messages.append(f"{b2} advances to second.")

                self.game.state["bases"] = [b1, b2, b3]
                print(" ".join(messages) + f" {self.game.state['outs']} out(s).")
            else:
                print(f"{out_message} {self.game.state['outs']} outs.")

    def handle_lineout_gp(self, team, batter, in_play_result, outcome):
        """
        Handles the result of a lineout and the stipulations of a lineout double play
        Tracks to see if the double play is unassisted or assisted
        Some fielders can only throw to certain bases to get an out in time, this checks to see what throws are possible
        
        """
        pos, fielder_name = self.get_fielder_and_location(team, in_play_result, outcome)

        fielders_index = {
            "1B": 0,
            "2B": 1,
            "SS": 1,
            "3B": 2
        }

        # Sets up the bases for potential throw targets for a DP
        valid_throw_targets = {
            "LF": [2],
            "CF": [2],
            "RF": [1, 2],
            "3B": [1],
            "SS": [0, 1, 2],
            "2B": [0, 1, 2],
            "1B": [1, 2]
        }

        base_names = ["first", "second", "third"]

        # 1. Check if a DP with two fielders is possible
        can_dp_two_fielders = False
        if pos in fielders_index and self.game.state["bases"][fielders_index[pos]] is not None and self.game.state["outs"] < 2:
            can_dp_two_fielders = True

        # 2. Check if a DP with three fielders is possible
        possible_targets = []
        if pos in valid_throw_targets and self.game.state["outs"] < 2:
            for idx in valid_throw_targets[pos]:
                if self.game.state["bases"][idx] != None:
                    if pos == "RF" and idx == 1:
                        if self.game.state["bases"][2] == None:
                            possible_targets.append(idx)
                    else:
                        possible_targets.append(idx)

        can_dp_three_fielders = len(possible_targets) > 0

        # 3. Choose between dp_two_fielders and dp_three_fielders
        chosen_dp = None
        if can_dp_two_fielders and can_dp_three_fielders:
            if random.random() < 0.7:
                chosen_dp = "dp_two_fielders"
            else:
                chosen_dp = "dp_three_fielders"
        elif can_dp_two_fielders:
            chosen_dp = "dp_two_fielders"
        elif can_dp_three_fielders:
            chosen_dp = "dp_three_fielders"

        # 4. Run the chosen play
        if chosen_dp == "dp_two_fielders":
            base_idx = fielders_index[pos]
            base_str = base_names[base_idx]

            self.game.state["outs"] += 2
            self.game.display.record_stat(batter, "AB")

            print(f"{batter} lines into a double play. Both outs recorded by {fielder_name}. {self.game.state['bases'][base_idx]} out at {base_str}. {self.game.state['outs']} outs.")
            self.game.state["bases"][base_idx] = None

        elif chosen_dp == "dp_three_fielders":
            target_base_idx = random.choice(possible_targets)
            base_str = base_names[target_base_idx]

            # Find out which fielder is is covering the base
            if target_base_idx == 0:
                covering_pos = "1B"
            elif target_base_idx == 1:
                if pos == "2B":
                    covering_pos = "SS"
                else:
                    covering_pos = "2B"
            else:
                covering_pos = "3B"

            covering_fielder, covering_pos = self.get_defender_name(covering_pos)

            self.game.state["outs"] += 2
            self.game.display.record_stat(batter, "AB")

            print(f"{batter} lines into a double play, {pos} {fielder_name} to {covering_pos} {covering_fielder}. {self.game.state['bases'][target_base_idx]} out at {base_str}. {self.game.state['outs']} outs.")
            self.game.state["bases"][target_base_idx] = None

        else:
            # Standard 1-out lineout if no double play was possible
            self.game.state["outs"] += 1
            self.game.display.record_stat(batter, "AB")
            print(f"{batter} lines out to {pos} {fielder_name}. {self.game.state['outs']} outs.")

    def handle_fly_ball(self, team, batter, in_play_result, outcome):
        # Standard logic for sacrifice flies and regular fly outs

        pos, fielder_name = self.get_fielder_and_location(team, in_play_result, outcome)
        self.game.state["outs"] += 1  

        b1, b2, b3 = self.game.state["bases"]
        run_scored = False

        messages = [f"{batter} flies out to {pos} {fielder_name}."]

        # Determines if run scores from third or not
        if b3 is not None and self.game.state["outs"] < 3:
            if random.random() < 0.9:
                messages.append(f"{b3} tags and scores.")
                self.game.state["score"][team] += 1
                self.game.display.print_score()
                b3 = None
                run_scored = True
            else:
                messages.append(f"{b3} is thrown out at the plate!")
                self.game.state["outs"] += 1
                b3 = None

        # Determines if runner takes third from second
        if b2 is not None and b3 is None and self.game.state["outs"] < 3:
            if random.random() < 0.8:
                messages.append(f"{b2} tags up and takes third.")
                b3 = b2
                b2 = None
            else:
                messages.append(f"{b2} is thrown out trying to take third!")
                self.game.state["outs"] += 1
                b2 = None

        if run_scored:
            messages[0] = f"{batter} is out on a sacrifice fly to {pos} {fielder_name}"
            self.game.display.record_stat(batter, "RBI")

        self.game.state["bases"] = [b1, b2, b3]

        for msg in messages:
            print(msg)

    def handle_popup(self, team, batter, in_play_result, outcome):
        # Records out on a pop up and print information

        pos, fielder_name = self.get_fielder_and_location(team, in_play_result, outcome)
        self.game.state["outs"] += 1
        print(f"{batter} pops out to {pos} {fielder_name}. {self.game.state['outs']} outs.")

    def get_error_profile(self, pos, outcome):
        """
        Determines likelihood of an error made by each position, classifies errors into fielding and throwing errors
        An error made by an outfielder can yield more bases on average
        Returns the type, chance, and who recieves the throw if throwing error
        """
        outfield = ["LF", "CF", "RF"]

        # 1. Ground balls
        if outcome == "ground ball":
            if pos == "1B":
                chance = 0.01
            elif pos == "2B" or pos == "C":
                chance = 0.02 if pos == "2B" else 0.01
            else:  
                chance = 0.03

            if random.random() < 0.65:
                return "fielding", chance, None

            return "throwing", chance, "1B"

        # 2. Outfield plays
        if pos in outfield:
            if pos == "CF":
                chance = 0.008
            else:
                chance = 0.01

            cutoff = "SS" if random.random() < 0.5 else "2B"

            if random.random() < 0.75:
                return "fielding", chance, None

            return "throwing", chance, cutoff

        # 3. Pop flies
        if outcome == "pop fly":
            return "fielding", 0.015, None

        # 4. Line drives
        if outcome == "line drive":
            return "fielding", 0.005, None

    def handle_error(self, team, batter, outcome, pos, fielder_name, error_type, target_pos):
        # prints the error message based on the error profile, increments the error statistic

        self.game.display.record_stat(fielder_name, "E")

        # Outfielders can give up 1-3 bases; infielders 1-2 bases
        if pos in ["LF", "CF", "RF"]:
            bases_gained = random.choices([1, 2, 3], weights=[55, 30, 15])[0]
        else:
            bases_gained = random.choices([1, 2], weights=[75, 25])[0]

        if error_type == "throwing" and target_pos:
            target_name, _ = self.get_defender_name(target_pos)
            print(f"Throwing error! {pos} {fielder_name} throws wild toward {target_pos} {target_name} on a {outcome}.")
        else:
            if outcome in ["pop fly", "line drive", "fly ball"]:
                print(f"Fielding error! {pos} {fielder_name} drops the {outcome}!")
            else:
                print(f"Fielding error! {pos} {fielder_name} boots the {outcome}!")

        self.advance_on_error(team, batter, bases_gained)

    def advance_on_error(self, team, batter, bases_gained):
        """
        Defines the core logic for how runners advance on an error 
        Advances and scores runners based on the number of bases gained
        """
        b1, b2, b3 = self.game.state["bases"]
        self.game.state["bases"] = [None, None, None]

        # Everyone advances 1 base
        if bases_gained == 1:
            if b3:
                self.game.state["score"][team] += 1
                print(f"{b3} scores.")
                self.game.display.print_score()
            if b2:
                self.game.state["bases"][2] = b2
                print(f"{b2} to third.")
            if b1:
                self.game.state["bases"][1] = b1
                print(f"{b1} to second.")

            self.game.state["bases"][0] = batter
            print(f"{batter} reaches first.")

        # Everyone advances 2 bases
        elif bases_gained == 2:
            for runner in [b3, b2]:
                if runner:
                    self.game.state["score"][team] += 1
                    print(f"{runner} scores.")
                    self.game.display.print_score()
            if b1:
                self.game.state["bases"][2] = b1
                print(f"{b1} to third.")

            self.game.state["bases"][1] = batter
            print(f"{batter} reaches second.")

        # Everyone advances 3 bases
        elif bases_gained == 3:
            for runner in [b3, b2, b1]:
                if runner:
                    self.game.state["score"][team] += 1
                    print(f"{runner} scores.")
                    self.game.display.print_score()

            self.game.state["bases"][2] = batter
            print(f"{batter} reaches third.")
