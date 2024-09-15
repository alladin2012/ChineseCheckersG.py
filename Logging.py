import datetime


class Logging:
    """
        Handles logging of game actions to a file, including moves made by players, game start, and loading game states.
        """

    def __init__(self, log_file_path):
        """
            Initializes the logging system with a path to the log file.
                """
        self.log_file_path = log_file_path

    def log_action(self, player_color, action):
        """
            Logs a game action performed by a player, appending it to the log file with a timestamp.
                """
        with open(self.log_file_path, "a") as log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"\n{timestamp} - Player {player_color}: {action} ")

    def load_game(self):
        """
            Loads the game state from the log file, returning a list of logged actions.
                """
        try:
            actions = []
            with open(self.log_file_path, "r") as log_file:
                for line in log_file:
                    actions.append(line.strip())
            return actions
        except FileNotFoundError:
            print("Error: Log file not found.")
        except Exception as e:  # Catch other exceptions, but use specific exceptions when possible
            print(f"An unexpected error occurred: {e}")

    def log_start_board(self, actions):
        """
            Parses the log file for the starting configuration of the game, extracting the number of human and computer players.
                """
        for line in actions:
            if "number of humans: " in line:
                index = line.find("humans: ")
                parts = line[index:]
                num_humans = int(parts[8])
                index = line.find("computers: ")
                parts = line[index:]
                num_pc = int(parts[11])
                return num_humans, num_pc

    def parse_log_file(self):
        """
            Parses the log file for moves made during the game, returning a list of moves in a structured format.
                """
        moves = []
        with open(self.log_file_path, "r") as log_file:

            for line in log_file:
                # Assuming each line in the log follows a specific format
                # For example: "timestamp - Player X: Moved from (start_pos) to (end_pos)"
                parts = line.strip().split(" - Player ")
                if len(parts) == 2:
                    action = parts[1].split(": ")[1]
                    if action.startswith("Moved from"):
                        move_str = action.replace("Moved from ", "")
                        start_pos, end_pos = self.parse_move(move_str)
                        moves.append((parts[1][0], start_pos, end_pos))  # (player_color, start_pos, end_pos)
        return moves

    def parse_move(self, move_str):
        """
            Parses a move from a string representation to structured start and end positions.
                """
        try:
            start_str, end_str = move_str.split(" to ")
            start = tuple(map(int, start_str.strip('()').split(',')))
            end = tuple(map(int, end_str.strip('()').split(',')))
            return start, end
        except ValueError as e:
            print(f"Error parsing move: {e}")
            return None, None
