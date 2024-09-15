import random


class ComputerPlayer:
    """
        Represents an AI-controlled player that makes decisions based on the current state of the game board.
        """

    def __init__(self, color, game_logic):
        """
            Initializes a new computer player with a specific color and a reference to the game's logic.

            :param color: The color assigned to the computer player.
            :param game_logic: A reference to the game logic for making decisions.
                """
        self.color = color
        self.game_logic = game_logic

    def generate_possible_moves(self, game_logic, player):
        """
            Generates all possible moves for the computer player based on the current state of the game board.

                :param game_logic: The game logic to evaluate possible moves.
                :param player: The computer player for whom moves are being generated.
                :return: A list of tuples representing possible moves (start_pos, end_pos).
                """
        optional_directions = [(0, -2), (1, -1), (1, 1), (0, 2), (-1, 1), (-1, -1)]
        possible_moves = []
        for row in range(17):
            for col in range(25):
                if game_logic.board[row][col] == player.color[0]:
                    for direction in optional_directions:
                        if game_logic.validate_move(player.color[0], (row, col),
                                                    (row + direction[0], col + direction[1]), False):
                            possible_moves.append(((row, col), (row + direction[0], col + direction[1])))
                    for move in game_logic.can_jump_again(player.color[0], (row, col), None):
                        possible_moves.append(move)
        return possible_moves

    def choose_move(self, game_logic, computer_player):
        """
            Chooses the best move from the generated list of possible moves.
            :param game_logic: The game logic to evaluate the moves.
            :param computer_player: The computer player making the decision.
            :return: A tuple representing the chosen move (start_pos, end_pos), or None if no moves are possible.
                """
        possible_moves = self.generate_possible_moves(game_logic, computer_player)
        return random.choice(possible_moves) if possible_moves else None
