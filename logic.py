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
            Player('Red', 0, 1),
            Player('Green', 1, -1),
        ]

        self.current_player = self.players[1]
        self.winner = None
        self.current_turn = 1

        self.pieces = [] 

        # add the kings
        player = self.players[0]
        player.king = King(self, player, 0, 4)
        player = self.players[1]
        player.king = King(self, player, 7, 4)
        self.update_board_list()

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

            # Create Queen
            Queen(self, player, main_row, 3)

            main_row = 7
            pawn_row = 6 

        self.update_board_list()
        
    def toggle_current_player(self):
        self.current_turn += 1
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
            response = "Multiple matching pieces found.\n"\
            "Please be more specific by including the rank or file of the attacking piece."
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
        self.move_piece(self.selected_piece, row, col)
        self.selected_piece = None
        self.update_board_list()
        self.toggle_current_player()
        self.check_winner()

    def move_piece(self, piece, row, col) -> None:
        piece.row = row
        piece.col = col
        piece.has_moved = True

    def check_winner(self):
        if not self.players[0].king.active:
            self.winner = self.players[1]
        elif not self.players[1].king.active:
            self.winner = self.players[0]
        else:
            self.winner = None
        return self.winner

    def is_under_attack(self, row: int, col: int) -> bool:
        """
        Test if a given square (defined by row and col) is under
        attack by pieces.
        """
        # If there is a piece at the coordinate, is_under_attack is not
        # applicable. Return False. 
        piece_at_coord = self.get_piece_at_coordinate(row, col)
        if piece_at_coord:
            return False
        
        # create a virtual pawn to test if the position is under attack
        virtual_pawn = Pawn(self, self.current_player, row, col)

        other_players_pieces = [piece for piece in self.pieces 
                                if piece.player != self.current_player and piece.active]
        
        ret = False
        for piece in other_players_pieces:
            if piece.validate_move(row, col):
                ret = True
                break

        del virtual_pawn
        return ret

    def if_check(self) -> bool:
        pass


class Player:
    def __init__(self, name: str, 
                id: bool,
                movement_direction: int) -> None:
        self.name = name
        self.id = id
        self.movement_direction = movement_direction
        self.captured_pieces = []