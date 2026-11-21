from stats import StatsDisplay

class TeamManager:
    """
    This class defines the functions pertaining to roster management (i.e. substitutions, defensive switches) and in-game menu to access different functions. 

    Attributes:

    game: The game class
    """ 
    def __init__(self, game):
        self.game = game
        self.display = StatsDisplay(self.game)

    def substitute_player(self, team, player_out_idx, player_in_idx, beginning_game=False):
        """
        Takes a player from the bench and inserts them into the lineup (occupied by the outgoing player).
        During normal play, forbids a player already taken out from re-entering.
        At the beginning of the game (beginning_game=True), players can be swapped freely without locking them out.
        """
        outgoing_player = self.game.lineups[team][player_out_idx - 1]

        # Only block re-entry after the game has started
        if not beginning_game and outgoing_player[0] in self.game.removed_players[team]:
            print(f"\n{outgoing_player[0]} has already played and cannot re-enter!\n")
            return

        outgoing_player = self.game.lineups[team].pop(player_out_idx - 1)
        incoming_player = self.game.bench[team].pop(player_in_idx - 1)

        player_out, out_pos = outgoing_player
        player_in, in_pos = incoming_player

        incoming_player[1] = out_pos

        if not beginning_game:
            self.game.removed_players[team].append(player_out)

        self.game.lineups[team].insert(player_out_idx - 1, incoming_player)
        self.game.bench[team].append(outgoing_player)

        print(f"\n{player_out} has been subbed out for {player_in}, now playing {out_pos}.\n")

    def move_batting_order(self, team, player1_idx, player_2_idx):
        # swaps the position of two selected players in the batting order
        player1 = self.game.lineups[team][player1_idx - 1]
        player2 = self.game.lineups[team][player_2_idx - 1]

        player1_name, pos1 = player1
        player2_name, pos2 = player2

        self.game.lineups[team][player1_idx - 1], self.game.lineups[team][player_2_idx - 1] = player2, player1

        print(f"\nBatting order adjustment: {pos1} {player1_name} is now batting in position {player_2_idx}. {pos2} {player2_name} is now batting in position {player1_idx}.\n")

    def defensive_switch(self, team, player1_idx, player2_idx):
        # swaps the position of two selected players
        player1 = self.game.lineups[team][player1_idx - 1]
        player2 = self.game.lineups[team][player2_idx - 1]

        player1_name, pos1 = player1
        player2_name, pos2 = player2

        player1[1], player2[1] = player2[1], player1[1]

        print(f"\nDefensive adjustment: {pos1} {player1_name} is now playing {pos2}. {pos2} {player2_name} is now playing {pos1}.\n")

    def menu(self, user_team):
        # Pulls up a list of options for a user to interact with
        option = 0

        while option != 5:
            option = input(
                "\nEnter an action:\n"
                "1 - View box score\n"
                "2 - Substitute a player\n"
                "3 - Defensive switch\n"
                "4 - View bases\n"
                "5 - Exit\n"
            )

            if option == "1":
                self.display.view_box_score(False)

            elif option == "2":
                self.display.print_batting_order(user_team, False)
                self.display.print_batting_order(user_team, True)

                player_out_idx = int(input("Enter lineup position of player to remove: "))
                player_in_idx = int(input("Enter bench position of incoming player: "))

                self.substitute_player(user_team, player_out_idx, player_in_idx)

            elif option == "3":
                self.display.print_batting_order(user_team, False)

                player1_idx = int(input("Enter first player's lineup position: "))
                player2_idx = int(input("Enter second player's lineup position: "))

                self.defensive_switch(user_team, player1_idx, player2_idx)

            elif option == "4":
                self.game.display.view_bases()

            elif option == "5":
                print("\nReturning to game...\n")
                break

            else:
                print("\nInvalid option.\n")
