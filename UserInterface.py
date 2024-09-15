class UserInterface:
    """
        Manages the user interface for the game, handling board display, move prompts, and winner announcements.
        """

    def __init__(self, game_logic):
        """
            Initializes the UserInterface with a reference to the game logic.
                """
        self.game_logic = game_logic

    def display_board(self):
        """
            Prints the current state of the game board to the console.
                """
        board = self.game_logic.board
        max_rows = len(board)
        max_cols = len(board[0]) if max_rows > 0 else 0

        # Building the board representation as a string
        board_str = "   "  # Start with spacing to align with the row numbers

        # Column headers
        for col_num in range(max_cols):
            board_str += f"{col_num % 10} "  # Using modulo 10 to keep single digit, improves alignment for >9
        board_str += "\n"

        for row in range(max_rows):
            # Row number at the start of each row. Adjust the format if you have more than 99 rows.
            board_str += f"{str(row).rjust(2)} "  # Right justify to align numbers and board correctly

            for col in range(max_cols):
                if board[row][col] is None:
                    board_str += "   "  # Three spaces for positions outside the playable area
                elif board[row][col] == 'E':
                    board_str += ". "  # Dot for empty positions
                else:
                    # Assuming pieces are represented by their player's color initial
                    board_str += f"{board[row][col]} "
            board_str += "\n"
        print(board_str)

    def display_winner(self, winner):
        """
            Announces the winner of the game.
                """
        print(f"Congratulations, Player {winner} has won the game!")


