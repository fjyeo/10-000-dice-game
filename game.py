import random
from collections import Counter


class Player:
    """Represents a single player in the 10,000 dice game."""

    def __init__(
        self,
        name: str,
    ):
        self.name = name
        self.total_score = 0

    def roll_dice(
        self,
        num_dice: int,
    ) -> list[int]:
        """Rolls the given number of dice and returns the results."""
        return [random.randint(1, 6) for _ in range(num_dice)]


class Game:
    """Main game controller for 10,000. Handles players, rounds, scoring, and flow."""

    TARGET_SCORE = 10_000
    ENTRY_THRESHOLD = 800
    DICE_COUNT = 6

    def __init__(
        self,
    ):
        self.players: list[Player] = []
        self.starting_player: Player | None = None

    ### ---- SETUP ---- ###

    def get_player_count(
        self,
    ) -> int:
        """Prompt user for player count (must be ≥ 2)."""
        while True:
            try:
                count = int(input("How many players are playing? "))
                if count >= 2:
                    return count
                print("⚠️ You need at least two players!")
            except ValueError:
                print("⚠️ Please enter a valid number.")

    def setup_players(
        self,
    ):
        """Initialise all player objects and decide starting order."""
        player_count = self.get_player_count()
        for i in range(player_count):
            name = input(f"Enter name for Player {i+1}: ")
            self.players.append(Player(name))

        # Decide starting player with a single dice roll
        print("\n🎲 Rolling to decide who starts...")
        rolls = [(p, random.randint(1, 6)) for p in self.players]
        rolls.sort(key=lambda x: x[1], reverse=True)
        self.starting_player = rolls[0][0]
        start_idx = self.players.index(self.starting_player)
        self.players = self.players[start_idx:] + self.players[:start_idx]
        print(f"🏆 {self.starting_player.name} starts first!\n")

    ### ---- SCORING ENGINE ---- ###

    def calculate_score(
        self,
        dice: list[int],
    ) -> int:
        """Returns the score for a given dice roll, following 10,000 rules."""
        counts = Counter(dice)
        score = 0

        # Straight (1-6)
        if sorted(counts.keys()) == [1, 2, 3, 4, 5, 6]:
            return 1000

        # Three pairs (e.g. 2,2,3,3,6,6)
        if len(counts) == 3 and all(v == 2 for v in counts.values()):
            return 1000

        # Three-of-a-kind and above (scales exponentially)
        for num, cnt in counts.items():
            if cnt >= 3:
                base = 1000 if num == 1 else num * 100
                score += base * (2 ** (cnt - 3))  # doubles per extra die
                counts[num] -= cnt

        # Singles of 1's and 5's after removing sets
        score += counts[1] * 100
        score += counts[5] * 50

        return score

    ### ---- TURN LOGIC ---- ###

    def player_turn(
        self,
        player: Player,
    ):
        """Handles a single player's turn."""
        print(f"\n----- {player.name}'s Turn -----")
        turn_score = 0
        dice_left = self.DICE_COUNT

        while True:
            roll = player.roll_dice(dice_left)
            print(f"🎲 Rolled: {roll}")

            roll_score = self.calculate_score(roll)
            if roll_score == 0:
                print("💀 No scoring dice! You lose all points for this turn.")
                return  # No points banked

            turn_score += roll_score
            print(f"Current turn score: {turn_score}")

            # If all dice scored → "hot dice" → roll all six again
            scoring_dice = self.count_scoring_dice(roll)
            dice_left = dice_left - scoring_dice if dice_left - scoring_dice > 0 else self.DICE_COUNT

            # Must reach 800 before being "on the board"
            if player.total_score < self.ENTRY_THRESHOLD and turn_score + player.total_score < self.ENTRY_THRESHOLD:
                print(f"⚠️ You need at least {self.ENTRY_THRESHOLD} to get on the board.")
                continue

            # Ask player whether to bank or risk continuing
            choice = input("Bank points and end turn? (Y/N): ").strip().upper()
            if choice == "Y":
                player.total_score += turn_score
                print(f"✅ {player.name}'s total score: {player.total_score}")
                return

    def count_scoring_dice(
        self,
        dice: list[int],
    ) -> int:
        """Counts how many dice contributed to scoring in the current roll."""
        counts = Counter(dice)
        used = 0

        # Sets of three or more always score
        for num, cnt in counts.items():
            if cnt >= 3:
                used += cnt

        # Singles of 1's and 5's
        used += counts[1] % 3
        used += counts[5] % 3
        return used

    ### ---- GAME LOOP ---- ###

    def start(
        self,
    ):
        """Main game flow."""
        print("\n=== WELCOME TO 10,000 ===\n")
        self.setup_players()

        # Continue until someone reaches target score
        game_over = False
        while not game_over:
            for player in self.players:
                self.player_turn(player)
                if player.total_score >= self.TARGET_SCORE:
                    print(f"\n🔥 {player.name} has reached {self.TARGET_SCORE}!")
                    game_over = True
                    break

        # Final round for other players
        print("\n=== FINAL ROUND ===")
        for player in self.players:
            if player is not self.starting_player:
                self.player_turn(player)

        # Announce winner
        winner = max(self.players, key=lambda p: p.total_score)
        print(f"\n🏆 {winner.name} wins with {winner.total_score} points!")


### START GAME ###
if __name__ == "__main__":
    game = Game()
    game.start()
