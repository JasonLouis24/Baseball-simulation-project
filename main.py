from game import BaseballGame


# --- Execution ---
if __name__ == "__main__":
    print("--- World Series Simulator ---")
    user_team = input("Do you want to manage the Brewers or Rays? (Enter MIL for the Brewers, TB for Rays): ").strip().upper()
    cpu_team = "TB" if user_team == "MIL" else "MIL"

    game = BaseballGame(user_team, cpu_team)
    game.play_full_series(cpu_team, user_team)
