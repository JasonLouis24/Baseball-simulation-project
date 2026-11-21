**World Series Simulator**

A text-based baseball simulation game where you manage either the Milwaukee Brewers or the Tampa Bay Rays through a best-of-seven World Series


**Description**

This Python application simulates full baseball games and a best-of-seven World Series between the Milwaukee Brewers and the Tampa Bay Rays using weighted probabilities 
and interactive terminal prompts. At the start of a series, you choose which team to manage while the CPU controls the opponent. Across each at-bat, inning, game, and series, 
the simulator handles pitch selection (fastballs vs. offspeed pitches), stolen base attempts, balls in play (ground balls, fly balls, line drives, and pop flies) and hit types, double plays, 
fielder's choices, sacrifice flies, fielding/throwing errors, and runner advancement logic. Extra innings logic is built in, and the game follows MLB's 2-3-2 home-field series format. 
Between at-bats, you can open an in-game management menu to view box scores or base runners, make bench substitutions (without allowing removed players to re-enter), and execute defensive position switches while the program tracks both 
single-game and series-wide player statistics and awards a World Series MVP at the end. A variety of statistics are calculated and displayed throughout the program as well. 


**Getting Started**

**Dependencies**

Python 3.14.7 (uses standard library modules; no third-party packages are required)
Any OS capable of running Python 3 in a terminal/command prompt can be used (including Windows, macOS, or Linux)


**Installing**

Clone or download the project repository containing `main.py`, `game.py`, `pitching.py`, `fielding.py`, `management.py`, `stats.py`, and `rosters.py` into a local folder


**Executing program**

Open a terminal or command prompt and navigate to the project directory.
Run the entry point script: bash python main.py


**Help**

Enter `MIL` or `TB` when prompted at startup. Entering a different team abbreviation will cause a `KeyError`
If you encounter an issue, open an issue in the repository or contact the author listed below.


**Authors**

Jason Louis - louis@etown.edu


**Version History**

1.0
Initial Release


**License**

This project is licensed under the MIT License - see the LICENSE.md file for details
