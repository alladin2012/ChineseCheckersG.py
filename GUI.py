from ChineseCheckers import *
from copy import *
import tkinter as tk
from tkinter import simpledialog, messagebox
from GameLogic import GameLogic
import pygame
import os


class GUI:
    def __init__(self, master):
        """
            Initializes the GUI for the Chinese Checkers game, including setting up the canvas,
            buttons, and binding events.
               """
        self.master = master
        self.setup_gui()

    def setup_gui(self):
        """
        Sets up the GUI elements including the canvas, start button, and binds events.
        """
        self.master.title("Chinese Checkers")
        self.canvas_width = 1000
        self.canvas_height = 750
        self.canvas = tk.Canvas(self.master, width=self.canvas_width, height=self.canvas_height, bg='#E0F7FA')
        self.canvas.pack()
        self.circle_ids_to_board_positions = {}  # Store mapping from circle IDs to board positions
        self.pass_button = tk.Button(self.master, text="Pass Turn", font=('Arial', 16),
                                     padx=20, pady=10, command=self.pass_turn)
        self.pass_button.pack_forget()
        self.waiting_for_move = False  # Indicates if we are waiting for the player to make a move
        self.move_start_pos = None  # Stores the start position of the move
        self.move_end_pos = None
        self.game_logic = None
        self.selected_piece = None  # To keep track of the currently selected piece

        self.current_player = 0  # Initialize current player index

        # Initially draw an empty board or a welcome message
        self.draw_empty_board()

        # Configure and pack the start button with bigger font and padding
        self.start_button = tk.Button(self.master, text="Start Game", font=('Arial', 16),
                                      padx=20, pady=10, command=self.start_game)
        self.start_button.pack()
        self.selected_piece = None  # Track the currently selected piece, if any
        self.available_moves = []
        self.player_colors = ['R', 'B', 'G', 'Y', 'O', 'P']  # The order of colors as initialized in the game
        self.waiting_for_start_pos = False
        self.waiting_for_end_pos = False
        self.pass_turn_bol = False
        self.temp_start_pos = None  # Temporarily store start position
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.error_mess = None
        self.jump_mess = None
        self.stylish_font = ('Arial', 20, 'bold')  # Example of a bolder, larger font
        self.stylish_color = '#FFD700'
        pygame.init()
        pygame.mixer.init()
        base_path = os.path.dirname(__file__)  # Get the directory of the current script
        audio_folder_path = os.path.join(base_path, "audio")  # Path to the audio folder

        # Load audio files from the "audio" folder
        self.move_sound = pygame.mixer.Sound(
            os.path.join(audio_folder_path, "mixkit-player-jumping-in-a-video-game-2043.wav"))
        self.jump_sound = pygame.mixer.Sound(
            os.path.join(audio_folder_path, "mixkit-player-jumping-in-a-video-game-2043.wav"))
        self.win_sound = pygame.mixer.Sound(
            os.path.join(audio_folder_path, "mixkit-animated-small-group-applause-523.wav"))



    def start_game(self):
        """
            Starts a new game of Chinese Checkers, handling player setup and game initialization.
                """
        self.start_button.config(text="Replay")
        valid_player_counts = [2, 3, 4, 6]

        while True:
            try:
                num_humans = simpledialog.askinteger("Input", "Enter the number of human players (1-6):",
                                                     parent=self.master, minvalue=1, maxvalue=6)

                num_computers = simpledialog.askinteger("Input", "Enter the number of computer players (0-5):",
                                                        parent=self.master, minvalue=0, maxvalue=5)

                total_players = num_humans + num_computers
                if total_players not in valid_player_counts:
                    raise ValueError("Total number of players must be 2, 3, 4, or 6.")

                break  # Valid input, exit the loop

            except ValueError as e:
                print(f"Invalid input: {e}. Please try again.")

        game = ChineseCheckers(num_humans, num_computers)
        game_over = False
        current_player_index = 0
        self.game_logic = GameLogic(total_players)
        self.ui = UserInterface(self.game_logic)

        while not game_over:
            current_player = game.players[current_player_index]
            if isinstance(current_player, Player):
                # Human player's turn
                self.human_turn(game.game_logic, game.ui, current_player.color, True)
            else:
                # Computer player's turn
                self.computer_turn( current_player)

            # Check win condition for each player after their turn
            if self.game_logic.check_win_condition(current_player.color):
                self.display_winner_on_canvas(current_player.color)
                game_over = True  # End the game loop if a player wins
                self.win_sound.play()

            # Move to the next player's turn
            current_player_index = (current_player_index + 1) % len(game.players)

    def on_canvas_click(self, event):
        """
            Handles click events on the canvas, determining move selections for human players.
                """
        # Check if we are currently expecting a move to be made
        if not self.waiting_for_move:
            return  # Do nothing if not in the state of waiting for a move

        clicked_item = self.canvas.find_closest(event.x, event.y)
        if clicked_item:
            circle_id = clicked_item[0]
            if circle_id in self.circle_ids_to_board_positions:
                # Determine if the click was within the bounds of a circle
                coords = self.canvas.coords(circle_id)
                x_center = (coords[0] + coords[2]) / 2
                y_center = (coords[1] + coords[3]) / 2
                distance = ((x_center - event.x) ** 2 + (y_center - event.y) ** 2) ** 0.5
                radius = (coords[2] - coords[0]) / 2

                if distance <= radius:
                    pos = self.circle_ids_to_board_positions[circle_id]

                    if self.selected_piece:
                        # Revert the appearance of the previously selected circle
                        self.canvas.itemconfig(self.selected_piece, outline='black', width=1)

                    # Highlight the selected circle
                    self.canvas.itemconfig(circle_id, outline='red', width=3)
                    self.selected_piece = circle_id  # Store the currently selected circle

                    if self.move_start_pos is None:
                        self.move_start_pos = pos
                    else:
                        self.move_end_pos = pos
                        self.waiting_for_move = False  # Indicate completion of move input
                        # Optionally, revert the appearance of the final selected circle here
                        self.canvas.itemconfig(self.selected_piece, outline='black', width=1)
                        self.selected_piece = None  # Reset the selection

    def pass_turn(self):
        """
            Allows the player to pass their turn, useful in certain game situations.
                """
        self.pass_turn_bol = True
        self.pass_button.pack_forget()
        # Proceed to the next player's turn. You might need to check if the next player is a human or computer, etc.

    def draw_empty_board(self):
        """
            Optionally draws an empty board layout or a welcome message.
                """
        self.canvas.create_text(self.canvas_width / 2, self.canvas_height / 2,
                                text="Welcome to Chinese Checkers", font=('Arial', 24), fill='black')

    def draw_board(self):
        """
            Draws the game board on the canvas, representing the current game state.
                """
        self.canvas.delete("all")  # Clear any existing items on the canvas

        # Adjust these values as necessary based on your canvas size and desired layout
        board_width = self.canvas_width * 0.75
        col_width = board_width / self.game_logic.max_cols
        row_height = self.canvas_height / self.game_logic.max_rows
        radius = min(col_width, row_height) / 1.4  # Adjust as needed for visual appeal
        self.circle_ids_to_board_positions = {}  # Reset mapping for new board drawing
        # Draw the game board
        for row in range(self.game_logic.max_rows):
            for col in range(self.game_logic.max_cols):
                piece = self.game_logic.board[row][col]
                if piece != ' ':  # Assuming ' ' represents an empty space on the board
                    x = col * col_width + col_width / 2
                    y = row * row_height + row_height / 2
                    fill = self.get_color(piece)
                    # Draw the piece as a circle on the canvas
                    self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=fill, outline='black')
                    circle_id = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=fill,
                                                        outline='black')
                    # Map the circle ID to its board position
                    self.circle_ids_to_board_positions[circle_id] = (row, col)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Draw the turn indicator on the right side
        turn_indicator_x = board_width + (self.canvas_width - board_width) / 2
        turn_indicator_y = self.canvas_height / 2
        turn_indicator_width = min(self.canvas_width - board_width, self.canvas_height) * 0.9
        turn_indicator_height = self.canvas_height * 0.9  # Increased height proportion
        self.canvas.create_rectangle(turn_indicator_x - turn_indicator_width / 2,
                                     turn_indicator_y - turn_indicator_height / 2,
                                     turn_indicator_x + turn_indicator_width / 2,
                                     turn_indicator_y + turn_indicator_height / 2,
                                     fill='white', outline='black')

    def human_turn(self, game_logic, ui, player_color, first=True):
        """
            Manages the human player's turn, allowing them to select moves and handle jumps.
                """
        additional_jumps_available = ""
        current_player_name = player_color
        self.canvas.create_text(875.0, 375.0, text=current_player_name + "'s Turn",
                                font=('Arial', 20), fill='black')
        self.draw_board()
        # Before entering the loop waiting for player input, show the pass button
        self.pass_button.pack(side=tk.BOTTOM, pady=10)  # Adjust positioning as needed
        while True:
            if first:
                self.canvas.create_text(875.0, 375.0,
                                        text=current_player_name + "'s Turn,\nChoose your \nmove: ",
                                        font=self.stylish_font, fill=self.stylish_color)
            else:
                self.canvas.create_text(875.0, 375.0,
                                        text=current_player_name + "'s Turn,"
                                                                   "\nEnter your \nnext jump: ",
                                        font=self.stylish_font, fill=self.stylish_color)

            if not first and self.pass_turn_bol == True:
                self.pass_turn_bol = False
                self.canvas.create_text(875.0, 375.0,
                                        text="'turn passed ",
                                        font=self.stylish_font, fill=self.stylish_color)
                # After a move is made or the turn is passed
                break  # End the turn if the player chooses to pass after a jump
            self.waiting_for_move = True
            self.move_start_pos = None
            self.move_end_pos = None
            while self.waiting_for_move:
                self.master.update_idletasks()
                self.master.update()
                if self.pass_turn_bol:  # If pass button was clicked, exit the wait loop
                    break
            start_pos = copy(self.move_start_pos)
            end_pos = self.move_end_pos

            if self.game_logic.validate_move(player_color, start_pos, end_pos, False):
                distance_moved = max(abs(end_pos[0] - start_pos[0]), abs(end_pos[1] - start_pos[1]))
                if first:
                    self.game_logic.make_move([(player_color, start_pos, end_pos)])
                    self.move_sound.play()
                else:
                    if ((end_pos[0] != start_pos[0] and distance_moved > 1) or (end_pos[0] == start_pos[
                        0] and distance_moved > 3)) and (start_pos, end_pos) in additional_jumps_available:
                        self.game_logic.make_move([(player_color, start_pos, end_pos)])
                        self.move_sound.play()
                    else:
                        self.canvas.delete(self.jump_mess)
                        self.error_mess = self.canvas.create_text(875.0, 450.0,
                                                                  text=f"Invalid move. \nTry again",
                                                                  font=self.stylish_font, fill=self.stylish_color)
                        continue

                # Display the board immediately after making a move or jump to show updated game state
                self.master.update_idletasks()  # Force update of the GUI
                self.draw_board()
                self.master.update_idletasks()  # Force update of the GUI after drawing

                if (end_pos[0] != start_pos[0] and distance_moved > 1) or (end_pos[0] == start_pos[
                    0] and distance_moved > 3):  # If the move was a jump
                    # Check if additional jumps are possible
                    additional_jumps_available = self.game_logic.can_jump_again(player_color, end_pos, start_pos)
                    if additional_jumps_available:
                        self.draw_board()
                        self.canvas.delete(self.error_mess)
                        self.jump_mess = self.canvas.create_text(890.0, 450.0,
                                                                 text="can make \nanother jump",
                                                                 font=self.stylish_font, fill=self.stylish_color)
                        self.pass_button.place(x=self.canvas_width - 200,
                                               y=600)  # Adjust 'x' and 'y' as needed to place it upper right
                        first = False  # Indicate that we're still in the same turn for subsequent jumps
                        continue  # Continue in the loop to allow the player to make additional jumps
                break  # Exit the loop if no jump was made or no additional jumps are possible
            else:
                self.canvas.delete(self.jump_mess)
                self.canvas.create_text(875.0, 450.0,
                                        text="Invalid move. \nTry again",
                                        font=self.stylish_font, fill=self.stylish_color)

    def computer_turn(self, computer_player):
        """
            Simulates the computer player's turn, making moves based on the game logic.
                """
        self.canvas.create_text(875.0, 375.0, text=computer_player.color + "Computer \nPlayer's Turns",
                                font=self.stylish_font, fill=self.stylish_color)
        comp_move = computer_player.choose_move(self.game_logic, computer_player)
        if comp_move:
            # Execute the chosen move
            self.game_logic.make_move([(computer_player.color[0],) + comp_move])
            self.move_sound.play()
            self.master.update_idletasks()  # Force update of the GUI
            self.draw_board()
            self.master.update_idletasks()
            # Unpack the chosen move to start and end positions
            start_pos, end_pos = comp_move

            # Check for possible jumps after the initial move
            distance_moved = max(abs(end_pos[0] - start_pos[0]), abs(end_pos[1] - start_pos[1]))
            if (end_pos[0] != start_pos[0] and distance_moved > 1) or end_pos[0] == start_pos[0] and distance_moved > 3:
                possible_jumps = self.game_logic.can_jump_again(computer_player.color[0], end_pos, start_pos)
                counter = 0
                while possible_jumps:
                    counter += 1
                    # Choose a random jump from the possible jumps
                    jump_move = random.choice(possible_jumps)
                    # Unpack the start and end positions from the chosen jump move
                    if counter < 5:  # max jumps
                        jump_start_pos, jump_end_pos = jump_move
                        # Execute the jump move
                        self.game_logic.make_move([(computer_player.color[0],) + (jump_start_pos, jump_end_pos)])
                        self.move_sound.play()
                    else:
                        break
                    # Update possible jumps for subsequent jumps
                    possible_jumps = self.game_logic.can_jump_again(computer_player.color[0], jump_end_pos,
                                                                    jump_start_pos)
        else:
            self.canvas.create_text(875.0, 375.0,
                                    text="Computer player\n cannot move.",
                                    font=self.stylish_font, fill=self.stylish_color)

    def display_winner_on_canvas(self, winner_color):
        """
            Displays the winner on the canvas once the game is concluded.
                """
        self.canvas.delete("all")  # Optionally clear the canvas before displaying the winner
        self.canvas.create_text(self.canvas_width / 2, self.canvas_height / 2,
                                text=f"Winner: {winner_color}", font=self.stylish_font, fill=self.stylish_color)

    def get_color(self, cell):
        """
            Maps cell values to specific colors for drawing the board.
                """
        colors = {
            'R': '#E57373',  # Red
            'B': '#64B5F6',  # Blue
            'G': '#81C784',  # Green
            'Y': '#FFF176',  # Yellow
            'O': '#FFB74D',  # Orange
            'P': '#BA68C8',  # Purple
            'E': 'white'  # Empty but playable spot
        }
        return colors.get(cell, 'white')  # Default to white for empty/unrecognized cells


def main():
    """
        Main function to run the GUI application.
        """
    root = tk.Tk()
    GUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
