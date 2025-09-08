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

        # Roll one dice per player and pair results with player objects
        rolls = [(p, random.randint(1, 6)) for p in self.players]

        # Sort rolls by highest value (x[1] is the dice roll x[0] is the player name) in descending order using reverse=True
        rolls.sort(key=lambda x: x[1], reverse=True)

        # Sets the starting player to the player with the highest roll by accessing the first element of the sorted rolls list
        self.starting_player = rolls[0][0]

        # Find where the starting player sits in the original player list by using the index method and assigning it to start_idx
        start_idx = self.players.index(self.starting_player)

        # Rotate player order so the starter goes first and turns continue in order by slicing the player list and appending the first slice to the end
        self.players = self.players[start_idx:] + self.players[:start_idx]

        print(f"🏆 {self.starting_player.name} starts first!\n")


    ### ---- SCORING ENGINE ---- ###

    def calculate_score(
        self,
        dice: list[int],
    ) -> int:
        """Returns the score for a given dice roll, following 10,000 rules."""
        # Counts the number of each die in the roll and groups them by their value so we can check for sets and singles
        counts = Counter(dice)
        score = 0

        # Simple check for a straight (1,2,3,4,5,6) → automatic 1000 points
        if sorted(counts.keys()) == [1, 2, 3, 4, 5, 6]:
            return 1000

        
        # Check for three pairs (e.g. 2,2,3,3,6,6) by checking the length of the counts dictionary is 3 and all the values are 2  → automatic 1000 points  
        if len(counts) == 3 and all(v == 2 for v in counts.values()):
            return 1000

        # Three-of-a-kind and above (scales exponentially) by using a for loop to iterate through the counts dictionary and checking if the count is greater than or equal to 3
        for num, cnt in counts.items():
            if cnt >= 3:
                # Base score = 1000 for triple 1's, else num * 100 for other triples 
                base = 1000 if num == 1 else num * 100
                # Each extra die beyond three doubles the base score by using the exponentiation operator **
                score += base * (2 ** (cnt - 3))
                # Remove these dice from counts so we don't double-count singles by subtracting the count from the number of dice
                counts[num] -= cnt

        # Score remaining single 1's (100 each) and single 5's (50 each)
        score += counts[1] * 100
        score += counts[5] * 50

        return score

    ### ---- TURN LOGIC ---- ###

    def player_turn(
    self,
    player: Player,
):
        """Handles a single player's turn with proper roll/bank prompts."""
        print(f"\n----- {player.name}'s Turn -----")
        turn_score = 0
        dice_left = self.DICE_COUNT

        while True:
            # Always ask the player if they want to roll before rolling
            choice = input(f"{player.name}, do you want to roll {dice_left} dice? (Y/N): ").strip().upper()

            # If player chooses NOT to roll
            if choice == "N":
                # Check entry threshold rule
                if player.total_score + turn_score < self.ENTRY_THRESHOLD:
                    print(f"⚠️ You need at least {self.ENTRY_THRESHOLD} points to get on the board. You must roll.")
                    continue  # Force another prompt
                else:
                    # Player is allowed to bank and end their turn
                    player.total_score += turn_score
                    print(f"✅ {player.name} banks {turn_score} points. Total score: {player.total_score}")
                    return

            # Roll the dice
            roll = player.roll_dice(dice_left)
            print(f"🎲 Rolled: {roll}")

            # Calculate score from this roll
            roll_score = self.calculate_score(roll)
            if roll_score == 0:
                print("💀 No scoring dice! You lose all points for this turn.")
                return

            # Update turn score
            turn_score += roll_score
            print(f"💰 Current turn score: {turn_score}")

            # Count scoring dice to determine how many dice are left
            scoring_dice = self.count_scoring_dice(roll)
            dice_left = dice_left - scoring_dice if dice_left - scoring_dice > 0 else self.DICE_COUNT

            # If player scored with all dice → hot dice rule
            if dice_left == self.DICE_COUNT:
                print("🔥 Hot dice! You scored with every die.")
                hot_choice = input(f"{player.name}, roll all six again or bank? (R/B): ").strip().upper()
                if hot_choice == "B":
                    player.total_score += turn_score
                    print(f"✅ {player.name} banks {turn_score} points. Total score: {player.total_score}")
                    return
                # If they choose "R", we just loop back and roll again


    def count_scoring_dice(
        self,
        dice: list[int],
    ) -> int:
        """Counts how many dice contributed to scoring in the current roll."""
        counts = Counter(dice) # Count how many of each number was rolled
        used = 0

        # Add dice used in sets of three or more (e.g. three 2's = 3 dice used) by iterating through the counts dictionary and adding the count to the used variable if the count is greater than or equal to 3
        for num, cnt in counts.items():
            if cnt >= 3:
                used += cnt

         # Add leftover scoring singles: 1's and 5's
         # Use % 3 so we only count singles outside of sets of three+
        used += counts[1] % 3
        used += counts[5] % 3
        return used # Return the number of dice used for scoring

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
        winner = max(self.players, key=lambda p: p.total_score) # Use the max function to find the player with the highest total score by using the total_score attribute of the player object
        print(f"\n🏆 {winner.name} wins with {winner.total_score} points!")


### START GAME ###
if __name__ == "__main__":
    game = Game() # Create a new game instance
    game.start() # Start the game
