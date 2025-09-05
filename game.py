import random


class Player:
    """Represents a single player in the game."""

    def __init__(
        self,
        name: str,
    ):
        self.name = name
        self.score = 0

    def roll_dice(
        self,
        dice_sides: int = 6,
    ) -> int:
        """Roll a dice and update the player's score."""
        self.score = random.randint(1, dice_sides)
        return self.score


class Game:
    """Main game controller. Handles players, rolls, and deciding who starts."""

    def __init__(
        self,
    ):
        # These are effectively our "declarations" — clear and easy to read at the top.
        self.players: list[Player] = []
        self.starting_player: Player | None = None

    def get_player_count(
        self,
    ) -> int:
        """
        Ask the user how many players are playing.
        Keeps asking until a valid number >= 2 is entered.
        """
        while True:
            try:
                count = int(input("Please enter the number of players: "))
                if count >= 2:
                    return count
                print("⚠️ You need at least 2 players to play!")
            except ValueError:
                print("⚠️ Invalid input. Please enter a valid number.")

    def setup_players(
        self,
    ):
        """Prompt the user for all player names and initialise Player objects."""
        player_count = self.get_player_count()

        # First player's name is requested separately for clarity
        first_name = input("Please enter your first player's name: ")
        self.players.append(Player(first_name))

        # Ask for remaining player names
        for _ in range(player_count - 1):
            name = input("Please enter the next player's name (to the left): ")
            self.players.append(Player(name))

    def confirm_continue(
        self,
    ):
        """
        Confirm with the user if they want to continue the game.
        Keeps asking until a valid Y/N is entered.
        """
        while True:
            response = input(
                f"Players: {[p.name for p in self.players]}. Continue? (Y/N): "
            ).strip().upper()

            if response == "Y":
                return
            elif response == "N":
                print("GAME ENDED ❌")
                exit()
            else:
                print("⚠️ Please enter Y or N.")

    def roll_for_starting_player(
        self,
        players: list[Player],
    ):
        """
        Each player rolls a dice to determine who starts.
        If there is a tie, only tied players re-roll until we have a winner.
        """
        print("\n🎲 Rolling dice to decide who starts...\n")
        scores = []

        # Each player rolls once
        for player in players:
            input(f"{player.name}, type ROLL to roll your dice: ")
            roll = player.roll_dice()
            scores.append(roll)
            print(f"   {player.name} rolled a {roll}")

        # Find highest score
        max_score = max(scores)
        top_players = [
            players[i] for i, s in enumerate(scores) if s == max_score
        ]

        # Handle ties recursively — only tied players roll again
        if len(top_players) > 1:
            print("\n⚡ It's a tie! Rolling again for tied players...")
            return self.roll_for_starting_player(
                top_players,
            )

        # No tie → set the starting player
        self.starting_player = top_players[0]
        print(
            f"\n🏆 {self.starting_player.name} had the highest roll ({max_score}) and goes first!"
        )

    def start(
        self,
    ):
        """Main entry point for the game flow."""
        print("\n=== WELCOME TO THE DICE GAME ===\n")
        self.setup_players()
        self.confirm_continue()
        self.roll_for_starting_player(
            self.players,
        )


### START GAME ###
if __name__ == "__main__":
    game = Game()
    game.start()
