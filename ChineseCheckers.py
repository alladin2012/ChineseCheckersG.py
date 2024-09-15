from GameLogic import GameLogic
from UserInterface import UserInterface
from Player import Player
from ComputerPlayer import *
from Logging import *
import datetime


class ChineseCheckers:
    def __init__(self, human_players, computer_players):
        """
            Represents a game of Chinese Checkers including players, game logic, and user interface.
            Initializes the game with a given number of human and computer players.
            """
        total_players = human_players + computer_players
        MAX_PLAYERS = 6
        MIN_PLAYERS = 2
        assert MIN_PLAYERS <= total_players <= MAX_PLAYERS, "Total number of players must be between 2 and 6."
        self.players = []
        colors = ["R", "B", "G", "Y", "O", "P"]
        player_names = ["Red", "Blue", "Green", "Yellow", "Orange", "Purple"]  # Initialize human players
        for i in range(human_players):
            self.players.append(Player(player_names[i], colors[i]))
        for i in range(human_players, total_players):
            self.players.append(ComputerPlayer(player_names[i], colors[i]))
        self.game_logic = GameLogic(total_players)
        self.ui = UserInterface(self.game_logic)


def play_game():
    """
       Main function to play the game. Allows starting a new game or loading an existing game.
       Manages the game loop including player turns and checking for game over conditions.
       """
    print("Welcome to Chinese Checkers!")
    choice = input("Start a new game or load an existing one? (new/load): ")
    if choice.lower() == 'load':
        # Logic for loading and continuing a game from a log file
        actions = ""
        while not actions:
            address = input("Enter the log file address to load: ")
            logger = Logging(address)
            actions = logger.load_game()
        num_humans, num_computers = logger.log_start_board(actions)
        game_over = False

        current_player_index = 0
        game = ChineseCheckers(num_humans, num_computers)
        actions = logger.parse_log_file()

        for line in actions:
            print("The current move is:", line)
            if input(
                    "Press Enter to apply the move or type 'continue' to start playing now: ").lower() == 'continue':
                break
            else:
                current_player_index = (current_player_index + 1) % (
                        num_humans + num_computers)  # Move to the next player
                game.game_logic.make_move([(line[0], line[1], line[2])])
                game.ui.display_board()
        print("Continuing game from the current state...")
    else:
        # Logic for starting a new game
        valid_input = False
        while not valid_input:
            try:
                num_humans = int(input("Enter the number of human players (1-6): "))
                num_computers = int(input("Enter the number of computer players (0-5): "))

                total_players = num_humans + num_computers
                if not (2 <= total_players <= 6):
                    raise ValueError("Total number of players must be between 2 and 6.")
                if num_humans < 0 or num_computers < 0:
                    raise ValueError("Number of players cannot be negative.")

                valid_input = True  # Input is valid, proceed with the game setup
            except ValueError as e:
                print(f"Invalid input: {e}. Please try again.")
        game = ChineseCheckers(num_humans, num_computers)

        game_over = False
        current_player_index = 0
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = f"game_log_{current_time}.txt"
        logger = Logging(log_file)
        logger.log_action("System",
                          "Game Start, number of humans: " + str(num_humans) + ", number of computers: " + str(
                              num_computers))
    while not game_over:
        current_player = game.players[current_player_index]
        if isinstance(current_player, Player):
            # Human player's turn
            game.ui.display_board()
            human_turn(game.game_logic, game.ui, current_player.color, logger, True)
        else:
            # Computer player's turn
            computer_turn(game.game_logic, current_player, logger)

        # Check win condition for each player after their turn
        if game.game_logic.check_win_condition(current_player.color):
            game.ui.display_winner(current_player.color)
            game_over = True  # End the game loop if a player wins

        # Move to the next player's turn
        current_player_index = (current_player_index + 1) % len(game.players)


def human_turn(game_logic, ui, player_color, logger, first=True):
    """
       Handles the logic for a human player's turn. Allows for making moves and logging actions.
       Supports multi-jump moves by checking for possible jumps after an initial move.
       """
    available_jumps = ""
    while True:
        print(f"Human Player's Turn ({player_color}):")
        # ui.display_board()  # Display the board at the start of the turn
        if first:
            human_move = input("Enter your move (row_start,col_start) to (row_end,col_end): ")
        else:
            human_move = input("Enter your next jump (row_start,col_start) to (row_end,col_end) or 'pass': ")

        if not first and human_move.lower() == 'pass':
            print("Turn passed.")
            break  # End the turn if the player chooses to pass after a jump

        start_pos, end_pos = parse_move(human_move)
        if start_pos is None or end_pos is None:
            print("Invalid move format. Please use the format 'row_start,col_start to row_end,col_end'.")
            continue

        if game_logic.validate_move(player_color, start_pos, end_pos):
            distance_moved = max(abs(end_pos[0] - start_pos[0]), abs(end_pos[1] - start_pos[1]))
            if first:
                game_logic.make_move([(player_color, start_pos, end_pos)])
                logger.log_action(player_color, f"Moved from {start_pos} to {end_pos}")
            elif ((end_pos[0] != start_pos[0] and distance_moved > 1) or (
                    end_pos[0] == start_pos[0] and distance_moved > 2)) and (
                    (start_pos, end_pos) in available_jumps):
                game_logic.make_move([(player_color, start_pos, end_pos)])
                logger.log_action(player_color, f"Moved from {start_pos} to {end_pos}")

            else:
                print("Invalid move. Try again.")
                continue

            if (end_pos[0] != start_pos[0] and distance_moved > 1) or (
                    end_pos[0] == start_pos[0] and distance_moved > 2):  # If the move was a jump
                # Check if additional jumps are possible
                available_jumps = game_logic.can_jump_again(player_color, end_pos,
                                                            start_pos)
                if available_jumps:  # Assume can_jump_again does not require prev_location
                    print("You can make another jump.")
                    ui.display_board()
                    first = False  # Set first to False to indicate subsequent jumps
                    continue  # Allow the player to make another jump
            break  # Exit the loop if no jump was made or no additional jumps are possible
        else:
            print("Invalid move. Try again.")
            continue


def computer_turn(game_logic, computer_player, logger):
    """
       Handles the logic for a computer player's turn. Chooses and makes moves based on game logic.
       Logs actions for auditing game history.
       """
    print("Computer Player's Turn (B):")
    comp_move = computer_player.choose_move(game_logic, computer_player)
    if comp_move:
        game_logic.make_move([(computer_player.color[0],) + comp_move])
        logger.log_action(computer_player.color, f"Moved from {comp_move[0]} to {comp_move[1]}")
    else:
        print("Computer player cannot move.")


def parse_move(move_str):
    """
        Parses a string input for a move into a start and end position.
        Validates the format and returns the positions as tuples.
        """
    try:
        start_str, end_str = move_str.split(" to ")
        start = tuple(map(int, start_str.strip().split(',')))
        end = tuple(map(int, end_str.strip().split(',')))
        if len(start) != 2 or len(end) != 2:
            raise ValueError("Move must specify two coordinates: start and end.")
        return start, end
    except ValueError as e:
        print(f"Error parsing move: {e}")
        return None, None


if __name__ == "__main__":
    play_game()
