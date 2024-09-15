class GameLogic:
    """
       Manages the logic for a Chinese Checkers game. This includes initializing the game board,
       handling player moves, and checking for win conditions.
       """

    def __init__(self, num_players):
        """
            Initializes the game with a specified number of players. Sets up the board based on the number of players.
                """
        assert num_players in [2, 3, 4, 5, 6], "Number of players must be 2, 3, 4, or 6."
        self.num_players = num_players
        self.max_rows = 17
        self.max_cols = 25
        self.board = self.initialize_board()

    def initialize_board(self):
        """
            Initializes the game board. Empty playable spaces are marked 'E', and player pieces are marked with
            their respective colors based on the initial setup for each player.
               """
        board = [[' ' for _ in range(self.max_cols)] for _ in range(self.max_rows)]

        # Identify active players based on the number of players
        # For simplicity, this example sequentially selects colors based on the total number of players
        # This logic might need adjustment based on how you determine which players are active
        player_positions = self.get_player_positions()
        active_colors = list(player_positions.keys())[:self.num_players]  # Adjust based on your game's logic

        # Mark playable areas and set starting positions for active players only
        for row in range(self.max_rows):
            for col in range(self.max_cols):
                if self.is_playable_area(row, col):
                    board[row][col] = 'E'  # Mark as empty but playable
        for color in active_colors:
            for pos in player_positions[color]:
                board[pos[0]][pos[1]] = color

        return board

    def get_player_positions(self):
        """
            Defines the initial positions for each player's pieces on the board.
            Returns a dictionary with colors as keys and a list of tuples representing positions.
                """
        return {
            'R': [(0, 12), (1, 11), (1, 13), (2, 10), (2, 12),  # Red's triangle
                  (2, 14), (3, 9), (3, 11), (3, 13), (3, 15)],
            'B': [(16, 12), (15, 11), (15, 13), (14, 10), (14, 12), (14, 14),  # Blue's triangle
                  (13, 9), (13, 11), (13, 13), (13, 15)],
            'G': [(7, 3), (6, 4), (6, 2), (5, 5), (5, 3),  # Green's triangle
                  (5, 1), (4, 6), (4, 4), (4, 2), (4, 0)],
            'Y': [(9, 21), (10, 22), (10, 20), (11, 23), (11, 21),  # Yellow's triangle,
                  (11, 19), (12, 24), (12, 22), (12, 20), (12, 18)],
            'O': [(7, 21), (6, 22), (6, 20), (5, 23), (5, 21),  # Orange's triangle
                  (5, 19), (4, 24), (4, 22), (4, 20), (4, 18)],
            'P': [(9, 3), (10, 4), (10, 2), (11, 5), (11, 3),  # Purple's triangle
                  (11, 1), (12, 6), (12, 4), (12, 2), (12, 0)],
        }

    def is_playable_area(self, row, col):
        """
               Checks if a given position is within a playable area of the board.
               """
        if row % 2 != col % 2:
            return False
        else:
            if row < 4:
                return (col >= 12 - row and col <= 12 + row)
            elif row == 4 or row == 12:
                return True
            elif 4 < row < 9:
                return row - 4 <= col < self.max_cols - (row - 4)
            elif 8 < row < 13:
                return self.max_cols - (row + 13) <= col <= row + 12
            elif 12 < row:
                return (col >= row - 4 and col <= 28 - row)

    def is_within_board(self, position):
        """
        Checks if a given position is within the board's boundaries.
        """
        row, col = position
        return 0 <= row < self.max_rows and 0 <= col < self.max_cols and self.board[row][col] is not None

    def validate_move(self, player, start_pos, end_pos, comment=True):
        """
        Validates whether a move from start_pos to end_pos is legal for the specified player.
        This includes checking for simple moves and jumps.
        """
        try:
            # Input type validation
            if not isinstance(start_pos, tuple) or not isinstance(end_pos, tuple):
                raise TypeError("Start and end positions must be tuples.")

            # Input value validation
            if not self.is_within_board(start_pos) or not self.is_within_board(end_pos):
                raise ValueError("Both positions must be within the board boundaries.")
            if self.board[start_pos[0]][start_pos[1]] != player:
                raise ValueError("The starting position does not contain the player's piece.")
            if self.board[end_pos[0]][end_pos[1]] != 'E':
                raise ValueError("The ending position is not empty.")
            # Hexagonal directions for movement and jumps
            directions = [(0, -2), (1, -1), (1, 1), (0, 2), (-1, 1), (-1, -1)]
            if (end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]) in directions:
                return True
            # Check for jump moves
            for dx, dy in directions:
                mid_pos = (start_pos[0] + dx, start_pos[1] + dy)
                jump_pos = (start_pos[0] + 2 * dx, start_pos[1] + 2 * dy)

                if jump_pos == end_pos and self.is_within_board(mid_pos) and self.board[mid_pos[0]][mid_pos[1]] not in [
                    None, 'E']:
                    # Valid jump over another piece to an empty space
                    return True
            # If none of the conditions are met, the move is illegal
            return False

        except (TypeError, ValueError) as e:
            if player != 'B':
                if comment:
                    print(f"Error validating move: {e}")
            return False

    def make_move(self, move_sequence):
        """
               Executes a sequence of moves on the board, updating the board state accordingly.
               """
        try:
            if not move_sequence:
                raise ValueError("Move sequence cannot be empty.")

            for move in move_sequence[0][1:]:
                if not (isinstance(pos, tuple) and len(pos) == 2 for pos in move):
                    raise TypeError("Each move must be a tuple of two positions.")

            start_pos, end_pos = move_sequence[0][1:]
            if not self.is_within_board(start_pos) or not self.is_within_board(end_pos):
                raise ValueError("All positions must be within the board boundaries.")

            # Retrieve the piece at the start position
            piece = self.board[start_pos[0]][start_pos[1]]
            if piece == 'E' or piece is None:
                raise ValueError("No piece found at the start position.")

            # Ensure the end position is empty
            if self.board[end_pos[0]][end_pos[1]] != 'E':
                raise ValueError("The end position is not empty.")
                # Perform the move
            self.board[start_pos[0]][start_pos[1]] = 'E'  # Mark the start position as empty
            self.board[end_pos[0]][end_pos[1]] = move_sequence[0][0]  # Place the piece at the end position

        except (TypeError, ValueError) as e:
            print(f"Error executing move: {e}")
            return False  # Indicate failure to execute the move sequence

        return True  # Indicate successful execution of the move sequence

    def can_jump_again(self, player, current_pos, prev_location):
        """
                Checks if the player can make another jump from the current position. Prevents reversing back to the previous location.
                """
        # Hexagonal directions for potential jumps
        directions = [(0, -4), (2, -2), (2, 2), (0, 4), (-2, 2), (-2, -2)]
        optional_moves = []
        for dx, dy in directions:
            xjump_pos = current_pos[0] + dx
            yjump_pos = current_pos[1] + dy
            jump_pos = (xjump_pos, yjump_pos)
            # Skip potential jumps that would reverse the pawn back to its previous location
            if jump_pos == prev_location:
                continue

            # Check if the jump is within the board
            if not self.is_within_board(jump_pos):
                continue
            # Check if the middle position has a piece to jump over and the jump position is empty
            player_options = ["R", "B", "G", "Y", "O", "P"]
            if self.board[xjump_pos][yjump_pos] == 'E' and self.board[xjump_pos - (dx // 2)][
                yjump_pos - (dy // 2)] in player_options:
                optional_moves.append((current_pos, (xjump_pos, yjump_pos)))  # Found a valid jump
        return optional_moves  # No valid jumps found that do not reverse to the previous location

    def check_win_condition(self, player):
        """
        Checks if the specified player has fulfilled the win condition by moving all their pieces to the opposing triangle.
        """
        try:
            if player[0] not in ['R', 'B', 'G', 'Y', 'O', 'P']:
                raise ValueError("Invalid player identifier.")

            # Target areas need to be dynamically calculated or predefined based on the player's starting positions
            # and the number of players. This example assumes predefined target areas for a simplified board setup.
            target_areas = self.get_target_areas_for_player(player)
            for row in range(self.max_rows):
                for col in range(self.max_cols):
                    if self.board[row][col] == player[0]:
                        if (row, col) not in target_areas:
                            return False  # A piece is not in the target area
            return True  # All pieces of the player are in the target area

        except ValueError as e:
            print(f"Error checking win condition: {e}")
            return False

    def get_target_areas_for_player(self, player):
        """
            Determines the target area for the specified player's pieces to achieve a win.
               """
        # Placeholder: Define target areas for each player. This should be dynamic based on the game setup.
        target_areas = {
            'R': [(row, col) for row in range(13, 17) for col in range(9, 16)],
            'B': [(row, col) for row in range(0, 4) for col in range(9, 16)],
            'G': [(9, 21), (10, 22), (10, 20), (11, 23), (11, 21),  # Yellow's triangle, moved 2 places to the right
                  (11, 19), (12, 24), (12, 22), (12, 20), (12, 18)],
            'Y': [(7, 3), (6, 4), (6, 2), (5, 5), (5, 3),  # Green's triangle, moved 3 places to the left
                  (5, 1), (4, 6), (4, 4), (4, 2), (4, 0)],
            'O': [(7, 21), (6, 22), (6, 20), (5, 23), (5, 21),  # Orange's triangle, moved 1 place to the right
                  (5, 19), (4, 24), (4, 22), (4, 20), (4, 18)],
            'P': [(9, 3), (10, 4), (10, 2), (11, 5), (11, 3),  # Purple's triangle, moved 2 places to the left
                  (11, 1), (12, 6), (12, 4), (12, 2), (12, 0)],

            # Define other areas for 'B', 'G', 'Y', 'O', 'P' as appropriate
        }
        return target_areas.get(player, [])
