from typing import Tuple
from pieces import Pawn, Rook, Bishop, King, Knight, Queen

# for colors
from colorama import just_fix_windows_console
from termcolor import colored
just_fix_windows_console()

LETTERS = 'ABCDEFGH'
PIECE_NAMES = 'PRNBKQ'

class Game:
    def __init__(self) -> None:
        """
        For managing the chess game logic
        """
        self.BOARD_SIZE = 8
        size = self.BOARD_SIZE
        self.board = [[None for _ in range(size)] for _ in range(size)]

        self.players = [
            Player('Player 0', 0, 1),
            Player('Player 1', 1, -1),
        ]

        self.current_player = self.players[0]
        self.winner = None

        self.pieces = []    

    def add_pieces_to_board(self):
        main_row = 0
        pawn_row = 1
        for player in self.players:
            # Create pawns
            for n in range(self.BOARD_SIZE):
                col = n
                Pawn(self, player, pawn_row, col)

            # Create rooks
            Rook(self, player, main_row, 0)
            Rook(self, player, main_row, 7)

            # Create knights
            Knight(self, player, main_row, 1)
            Knight(self, player, main_row, 6)

            # Create bishops
            Bishop(self, player, main_row, 2)
            Bishop(self, player, main_row, 5)

            # Create King and Queen
            Queen(self, player, main_row, 3)
            player.king = King(self, player, main_row, 4)

            main_row = 7
            pawn_row = 6 

        self.update_board_list()
        
    def toggle_current_player(self):
        if self.current_player == self.players[0]:
            self.current_player = self.players[1]
        else:
            self.current_player = self.players[0]

    def update_board_list(self):
        """
        Converts self.pieces into a list of lists to
        represent where the pieces are on the board.        
        """
        size = self.BOARD_SIZE
        self.board = [[None for _ in range(size)] for _ in range(size)]

        for piece in self.pieces:
            if piece.active:
                self.board[piece.row][piece.col] = piece

    def get_piece_at_coordinate(self, row: int, column: int):
        return self.board[row][column]

    def represent_board(self) -> str:
        """
        Returns a string representation of
        the board
        """
        # initialize the string to return
        ret = ''
        # add column headers
        column_header = '   '
        for letter in LETTERS:
            column_header += f' {letter} '
        column_header += '\n'
        ret += column_header

        # add the pieces to the board
        bg_is_dark = True
        for row in range(len(self.board)):
            rank_label = f' {(row - 8) * - 1} ' 
            ret += rank_label
            bg_is_dark = not bg_is_dark
            for col in range(len(self.board)):
                bg_color = 'on_blue' if bg_is_dark else 'on_white'
                bg_is_dark = not bg_is_dark
                if self.board[row][col] is None:
                    value = colored('   ', 'white', bg_color)
                else:
                    piece = self.board[row][col]
                    color = 'red' if piece.player.id == 0 else 'green'
                    value = colored(f' {piece.name} ', color, bg_color)
                ret += value
            ret += (rank_label + '\n')
        ret += column_header

        # add the captured pieces
        captured_pieces_0 = ''
        captured_pieces_1 = ''
        for piece in self.pieces:
            if piece.player.id == 1 and not piece.active:
                if not captured_pieces_1:
                    captured_pieces_1 += '\n'
                captured_pieces_1 += colored(f'{piece.name} ', 'green')
            if piece.player.id == 0 and not piece.active:
                if not captured_pieces_0:
                    captured_pieces_0 += '\n'
                captured_pieces_0 += colored(f'{piece.name} ', 'red')
        ret = ret + captured_pieces_0 + captured_pieces_1
        ret += '\n------------------------------------'
        return ret

    def parse_notation(self, notation: str) -> dict:
        """
        Takes a chess notation (str) and returns a dict of the values 
        parsed from that string.
        """
        if len(notation) not in (3,4):
            return None

        parsed_notation = {
            'piece_name': None,
            'col': None,
            'row': None,
            'to_col': None,
            'to_row': None,
        }

        piece_name = notation[0].upper()
        to_file = notation[-2].upper()
        to_rank = notation[-1]

        if not (piece_name in PIECE_NAMES and \
            to_file in LETTERS and \
            to_rank.isnumeric()):
            return None
            
        parsed_notation['piece_name'] = piece_name
        parsed_notation['to_col'] = LETTERS.index(to_file)
        parsed_notation['to_row'] = (int(to_rank) - 8) * -1

        # special handling for four-digit notation
        if len(notation) == 4:
            second_digit = notation[1].upper()
            if second_digit.isnumeric():
                parsed_notation['row'] = (int(second_digit) - 8) * -1
            else:
                parsed_notation['col'] = LETTERS.index(second_digit)

        return parsed_notation

    def move_w_notation(self, parsed_notation: dict):
        """
        Takes a parsed chess notation (dict), finds the piece to select (if any)
        and returns that piece, a piece to capture (if any) and a response (str)
        """
        current_players_pieces = [piece for piece in self.pieces 
                                if piece.player == self.current_player and piece.active]
        potential_pieces = []
        for piece in current_players_pieces:
            if parsed_notation['piece_name'] != piece.name.upper():
                continue
            if parsed_notation['row'] is not None and parsed_notation['row'] != piece.row:
                continue
            if parsed_notation['col'] is not None and parsed_notation['col'] != piece.col:
                continue

            success, potential_capture = piece.validate_move(parsed_notation['to_row'], parsed_notation['to_col'])
            if success:
                potential_pieces.append((piece, potential_capture))

        if len(potential_pieces) == 0:
            response = 'Move is invalid.'
            return False, response
        elif len(potential_pieces) > 1:
            response = 'Multiple matching pieces found.'
            return False, response
        else:
            found_piece = potential_pieces[0][0]
            captured_piece = potential_pieces[0][1]
            response = f"{self.current_player.name}'s {found_piece.type} moved."
            self.select_piece(found_piece)
            if captured_piece is not None:
                self.capture_piece(captured_piece)
            self.move_selected_piece(parsed_notation['to_row'], parsed_notation['to_col'])
            return True, response

    def select_piece(self, piece) -> None:
        self.selected_piece = piece

    def capture_piece(self, piece) -> None:
        piece.row = None
        piece.col = None

    def move_selected_piece(self, row, col) -> None:
        self.selected_piece.row = row
        self.selected_piece.col = col
        self.selected_piece.has_moved = True
        self.selected_piece = None
        self.update_board_list()
        self.toggle_current_player()
        self.check_winner()

    def check_winner(self):
        if not self.players[0].king.active:
            self.winner = self.players[1]
        elif not self.players[1].king.active:
            self.winner = self.players[0]
        else:
            self.winner = None
        return self.winner

    def check_for_valid_movesWIP(self, piece):
        # check if there are any valid moves for this piece         
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                is_valid, _ = piece.validate_move(row, col)
                if is_valid:
                    break
            if is_valid:
                break
        else:
            response = f'No valid moves for {piece.name} at ({piece.col},{piece.row}).'
            return None, response
              
    def evaluate_moveWIP(self, row: int, col: int) -> bool:
        """
        Attempt to move the selected piece based on the rules of
        that piece. Capture pieces as necessary. 
        """
        # Don't allow any further selections if the game is over
        if self.winner is not None:
            return None, 'The game is over.'

        is_valid, piece_to_capture = self.selected_piece.validate_move(row, col)
        
        # capture piece
        if piece_to_capture is not None:
            self.selected_piece.capture_piece(piece_to_capture)

        if is_valid:
            self.selected_piece.row = row
            self.selected_piece.col = col
            response = f'{self.selected_piece.name} moved to ({col},{row})'
            self.selected_piece = None
            self.update_board_list()
            self.toggle_current_player()
            self.check_winner()
            return True, response
        else:
            response = f'{self.selected_piece.name} at ({self.selected_piece.col},{self.selected_piece.row}) '\
                    f'to ({col},{row}) is not a valid move.'
            return False, response

class Player:
    def __init__(self, name: str, 
                id: bool,
                movement_direction: int) -> None:
        self.name = name
        self.id = id
        self.movement_direction = movement_direction