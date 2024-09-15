import pytest
from ChineseCheckers import *
from GameLogic import *


@pytest.fixture
def setup_game():
    """Fixture to set up a game instance for testing."""
    game = ChineseCheckers(2, 2)  # Initialize with 2 human and 2 computer players for testing
    return game


def test_game_initialization(setup_game):
    """Test game initialization."""
    game = setup_game
    assert len(game.players) == 4, "Total players should be 4."
    assert isinstance(game.game_logic, GameLogic), "Game logic should be initialized."


# Test Player and ComputerPlayer functionality
def test_player_initialization():
    player = Player("Test Player", "R")
    assert player.name == "Test Player"
    assert player.color == "R"


def test_valid_move(setup_game):
    """Test making a valid move."""
    game = setup_game
    # Assuming we know the board's initial setup, let's simulate a valid move for a human player
    # This might involve moving a piece from one position to another within the legal moveset
    # Note: The specific starting and ending positions will depend on your game's rules and starting board setup
    start_pos = (3, 9)  # A hypothetical valid starting position for a piece
    end_pos = (4, 8)  # A hypothetical valid ending position for that piece
    player_color = game.players[0].color  # Assuming the first player is a human player and it's their turn

    valid_move = game.game_logic.validate_move(player_color, start_pos, end_pos)
    assert valid_move, "This should be recognized as a valid move according to the game's rules."


def test_invalid_move(setup_game):
    """Test making an invalid move."""
    game = setup_game
    # Assume trying an impossible move
    start_pos = (0, 0)
    end_pos = (5, 5)
    player_color = game.players[0].color
    invalid_move = GameLogic.validate_move(player_color, start_pos, end_pos, False)
    assert not invalid_move, "This should be recognized as an invalid move."


def test_computer_move_generation(setup_game):
    """Test computer player move generation."""
    game = setup_game
    # Assuming computer players are the last two in the list
    computer_player = game.players[3]
    assert isinstance(computer_player, ComputerPlayer), "Player should be a ComputerPlayer instance."
    # This will not check for the quality or validity of the move, just that something is generated
    move = computer_player.generate_possible_moves(game.game_logic, computer_player)
    assert move, "Computer player should generate at least one move."


def test_check_win_condition(setup_game):
    """Test checking the win condition."""
    game = setup_game
    player_color = game.players[0].color  # Assuming the first player for simplicity

    # For a win condition test, you might need to manually set up a winning board state
    # This setup will depend on your game's rules for winning
    # The following is a hypothetical setup that you would need to adjust
    # Let's assume the player needs to move all their pieces to the opposite side of the board

    # Clear the board for setup
    for row in game.game_logic.board:
        for col in range(len(row)):
            row[col] = 'E'  # Marking all spaces as empty

    # Manually place the player's pieces in a winning configuration
    # This configuration should reflect your game's actual win condition logic
    # For example, filling the opponent's starting triangle with the player's pieces
    for pos in game.game_logic.get_target_areas_for_player(player_color)[
               0:10]:  # Assuming the target area function returns a list of winning positions
        game.game_logic.board[pos[0]][pos[1]] = player_color

    # Now check if the game logic recognizes this as a win
    win = game.game_logic.check_win_condition(player_color)
    assert win, "The game should recognize this as a winning condition."


def test_computer_player_choice():
    game_logic = GameLogic(2)  # Simple game logic initialization for 2 players
    computer_player = ComputerPlayer("B", game_logic)
    # Mock or simulate a game state where the computer player has a valid move
    # This might require setting up the board directly or simulating prior moves
    move = computer_player.choose_move(game_logic, computer_player)
    assert move, "Computer should generate a move."


@pytest.fixture
def game_with_custom_setup():
    """Fixture to create a game with a custom setup, for more controlled conditions."""
    game = ChineseCheckers(3, 0)  # A game with 3 human players, no computer players
    return game


@pytest.fixture
def game_with_custom_setup():
    """Fixture to create a game with a custom setup, for more controlled conditions."""
    game = ChineseCheckers(3, 0)  # A game with 3 human players, no computer players
    return game


@pytest.fixture
def logging_setup(tmp_path):
    """Fixture to set up a Logging instance with a temporary file."""
    d = tmp_path / "sub"
    d.mkdir()
    log_file = d / "test_log.txt"
    logger = Logging(str(log_file))
    return logger


def test_blocked_move():
    game_logic = GameLogic(2)
    # Setup a scenario where a move is blocked
    # This requires manipulating the board to a state where a move that would otherwise
    # be valid is blocked by another piece
    start_pos = (4, 6)
    blocked_pos = (5, 7)
    game_logic.board[start_pos[0]][start_pos[1]] = 'R'
    game_logic.board[blocked_pos[0]][blocked_pos[1]] = 'B'
    assert not game_logic.validate_move('R', start_pos, blocked_pos, False), "Move should be blocked and invalid."


### Tests ###

def test_load_game(logging_setup):
    """Test loading a game from a log file."""
    logger = logging_setup
    # Assuming the log file contains actions for a game start with 2 humans, 2 computers
    actions = ["2024-03-29 12:00:00 - System: Game Start, number of humans: 2, number of computers: 2"]
    log_file_path = logger.log_file_path
    with open(log_file_path, "w") as log_file:
        for action in actions:
            log_file.write(f"{action}\n")

    loaded_actions = logger.load_game()
    assert loaded_actions == actions, "Should load the game actions from the log file."


@pytest.fixture
def game_logic():
    """Fixture to initialize game logic for testing."""
    return GameLogic(2)  # Initialize with 2 players for simplicity


def test_parse_move(game_logic):
    """Test parsing of a user input move."""
    move_str = "5,1 to 6,2"
    expected_start = (5, 1)
    expected_end = (6, 2)

    # Assuming parse_move is a method of GameLogic. Adjust if it's defined differently.
    start_pos, end_pos = parse_move(move_str)
    assert start_pos == expected_start, f"Expected start position to be {expected_start}, got {start_pos}"
    assert end_pos == expected_end, f"Expected end position to be {expected_end}, got {end_pos}"


def test_game_initialization_with_various_players():
    """Test game initialization with various numbers of players."""
    # Test with minimum players
    game_min = ChineseCheckers(1, 1)
    assert len(game_min.players) == 2, "Should initialize game with 2 players."

    # Test with maximum players
    game_max = ChineseCheckers(6, 0)
    assert len(game_max.players) == 6, "Should initialize game with 6 players."

    # Test with an invalid number of players
    with pytest.raises(AssertionError):
        ChineseCheckers(7, 0), "Should raise an error for invalid total number of players."
