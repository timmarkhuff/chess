from typing import List

class Game:
    def __init__(self) -> None:
        """
        For managing the chess game logic
        """
        self.BOARD_SIZE = 8

        self.players = [
            Player('Player 0', 0, 1),
            Player('Player 1', 1, -1),
        ]

        self.current_player = self.players[0]
        self.winner = None

        # add pieces
        self.pieces = []    

    def add_pieces_to_board(self):
        main_row = 0
        pawn_row = 1
        
        for player in self.players:
            # Create pawns
            name = 'PA' if player.id == 0 else 'pa'
            for n in range(self.BOARD_SIZE):
                col = n
                Pawn(name, self, player, pawn_row, col)

            # Create rooks
            name = 'RO' if player.id == 0 else 'ro'
            Rook(name, self, player, main_row, 0)
            Rook(name, self, player, main_row, 7)

            # Create knights
            name = 'KN' if player.id == 0 else 'kn'
            Knight(name, self, player, main_row, 1)
            Knight(name, self, player, main_row, 6)

            # Create bishops
            name = 'BI' if player.id == 0 else 'bi'
            Bishop(name, self, player, main_row, 2)
            Bishop(name, self, player, main_row, 5)

            # Create King and Queen
            name = 'QU' if player.id == 0 else 'qu'
            Queen(name, self, player, main_row, 3)
            name = 'KI' if player.id == 0 else 'ki'
            player.king = King(name, self, player, main_row, 4)

            main_row = 7
            pawn_row = 6 
        
    def toggle_current_player(self):
        if self.current_player == self.players[0]:
            self.current_player = self.players[1]
        else:
            self.current_player = self.players[0]

    def board_as_list(self) -> List[list]:
        """
        Converts self.pieces into a list of lists to
        represent where the pieces are on the board.        
        """
        size = self.BOARD_SIZE
        board = [[None for _ in range(size)] for _ in range(size)]
        for piece in self.pieces:
            if piece.active:
                board[piece.row][piece.col] = piece

        return board 

    def get_piece_at_coordinate(self, row: int, column: int):
        board = self.board_as_list()
        return board[row][column]

    def represent_board(self) -> str:
        """
        Returns a string representation of
        the board
        """
        board = self.board_as_list()
        ret = '  '

        # add column headers
        for col in range(len(board)):
            ret += f'_{col}_'
        ret += '\n'

        # add the pieces to the board
        for row in range(len(board)):
            ret += f'{row}|'
            for col in range(len(board)):
                if board[row][col] is None:
                    value = '__'
                else:
                    value = board[row][col].name
                ret += f'{value}|'
            ret += '\n'

        # add the captured pieces
        ret += 'Captured Pieces:'
        captured_pieces_0 = ''
        captured_pieces_1 = ''
        for piece in self.pieces:
            if piece.player.id == 1 and not piece.active:
                if not captured_pieces_1:
                    captured_pieces_1 += '\n'
                captured_pieces_1 += f'{piece.name}, '
            if piece.player.id == 0 and not piece.active:
                if not captured_pieces_0:
                    captured_pieces_0 += '\n'
                captured_pieces_0 += f'{piece.name}, '
        ret = ret + captured_pieces_0 + captured_pieces_1
        ret += '\n------------------------------------'
        return ret
    
    def select_piece(self, row: int, col: int) -> tuple:
        # Don't allow any further selections if the game is over
        if self.winner is not None:
            return None, 'The game is over.'

        board = self.board_as_list()
        piece = board[row][col]

        if piece is None:
            return None, "No piece at that position."
        
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

        if piece.player != self.current_player:
            response = f"It's not {piece.player.name}'s turn."
            return None, response

        if piece.active:
            self.selected_piece = piece
            response = f'{piece.name} selected!'
            return piece, response
        else:
            response = 'That piece has been captured!'
            return None, response

    def move_selected_piece(self, row: int, col: int) -> bool:
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
            self.toggle_current_player()
            self.check_winner()
            return True, response
        else:
            response = f'{self.selected_piece.name} at ({self.selected_piece.col},{self.selected_piece.row}) '\
                    f'to ({col},{row}) is not a valid move.'
            return False, response

    def check_winner(self):
        if not self.players[0].king.active:
            self.winner = self.players[1]
        elif not self.players[1].king.active:
            self.winner = self.players[0]
        else:
            self.winner = None
        return self.winner



class Player:
    def __init__(self, name: str, 
                id: bool,
                movement_direction: int) -> None:
        self.name = name
        self.id = id
        self.movement_direction = movement_direction

class Piece:
    def __init__(self, 
                    name: str, 
                    game: Game, 
                    player: Player, 
                    row: int, 
                    col: int) -> None:
        self.name = name
        self.game = game
        self.player = player
        self.row = row
        self.col = col
        self.active = True
        self.type = self.__class__.__name__
        
        self.game.pieces.append(self)

    def capture_piece(self, piece) -> None:
        piece.active = False
        piece.row = None
        piece.col = None

    def check_boundaries(self, row, col) -> bool:
        """
        Checks if the specified move is in bounds
        """
        ret_val = (0 <= row <= self.game.BOARD_SIZE) and \
                (0 <= col <= self.game.BOARD_SIZE)
        return ret_val

    def validate_move(self, row: int, col: int) -> tuple:
        """
        First checks some basic validation conditions that apply
        to all pieces, then check the piece-specific conditions.
        """
        if self.row == row and self.col == col:
            return False, None

        return self.check_rules(row, col)

    def validate_diagonal(self, row: int, col: int) -> tuple:
        """
        Check if the requested move is a valid diagonal move.
        Return a boolean and the captured piece, if there is one.
        """
        if abs(self.row - row) != abs(self.col - col):
            return False, None

        piece_at_destination = self.game.get_piece_at_coordinate(row, col)
        if piece_at_destination is not None and piece_at_destination.player == self.player:
            return False, None

        direction_to_check_x = 1 if col > self.col else -1
        direction_to_check_y = 1 if row > self.row else -1
        check_pos_x = self.col
        check_pos_y = self.row
        while True:
            check_pos_x += direction_to_check_x
            check_pos_y += direction_to_check_y

            if check_pos_x == col:
                return True, piece_at_destination

            piece_at_curr_pos = self.game.get_piece_at_coordinate(check_pos_y, check_pos_x)
            if piece_at_curr_pos:
                return False, None

    def validate_line(self, row: int, col: int) -> tuple:
        """
        Check if the requested move is in a straight line, either
        along a row or a column. Returns a boolean and the captured piece,
        if any. 
        """
        piece_at_destination = self.game.get_piece_at_coordinate(row, col)
        if piece_at_destination is not None and piece_at_destination.player == self.player:
            return False, None
        
        # Find the direction to search
        if self.row != row and self.col != col:
            return False, None
        elif self.row == row:
            direction_to_search_x = get_direction(self.col, col) 
            direction_to_search_y = 0
        elif self.col == col:
            direction_to_search_x = 0
            direction_to_search_y = get_direction(self.row, row)

        # Check if any pieces are in the way
        check_pos_x = self.col
        check_pos_y = self.row
        while True:
            check_pos_x += direction_to_search_x
            check_pos_y += direction_to_search_y

            if check_pos_x == col and check_pos_y == row:
                return True, piece_at_destination

            piece_at_curr_pos = self.game.get_piece_at_coordinate(check_pos_y, check_pos_x)
            if piece_at_curr_pos:
                return False, None

class Pawn(Piece):
    def __init__(self, 
                name: str, 
                game: Game,
                player: Player, 
                row: int, 
                col: int) -> None:
        super().__init__(name, game, player, row, col)
        self.original_row = row
        self.original_col = col

    @property
    def has_moved(self) -> bool:
        """
        Checks if the pawn has moved from its original position
        """
        return not self.original_row == self.row or not self.original_col == self.col

    def check_rules(self, row: int, col: int) -> tuple:
        """
        Given a board position (expressed as row and column), determine if
        it is a valid move for this piece and if any pieces should be captured as
        a result of the move.
        """
        # Prevent moving on top of player's own piece
        piece_at_destination = self.game.get_piece_at_coordinate(row, col)
        if piece_at_destination is not None and \
            piece_at_destination.player == self.player:
            return False, None

        # Forward movement
        max_spaces_to_move = 1 if self.has_moved else 2
        proposed_movement = row - self.row
        if col == self.col and \
            have_same_sign(proposed_movement, self.player.movement_direction) and \
            abs(proposed_movement) <= max_spaces_to_move and \
            piece_at_destination is None:
            return True, None

        # Capturing along the diagonal
        if (col - 1 == self.col or col + 1 == self.col) and \
            row - self.row == self.player.movement_direction and \
            piece_at_destination is not None:
            return True, piece_at_destination

        # en passant
        ep_row = row - self.player.movement_direction
        en_passant_piece = self.game.get_piece_at_coordinate(ep_row, col)
        if (col - 1 == self.col or col + 1 == self.col) and \
            proposed_movement == self.player.movement_direction and \
                en_passant_piece is not None and \
                en_passant_piece.type == self.type:
            return True, en_passant_piece            
        
        # In all other cases, return False
        return False, None

class Knight(Piece):
    def __init__(self, 
                name: str, 
                game: Game,
                player: Player, 
                row: int, 
                col: int) -> None:
        super().__init__(name, game, player, row, col)

    def check_rules(self, row: int, col: int) -> tuple:
        piece_at_destination = self.game.get_piece_at_coordinate(row, col)
        if abs(self.row - row) == 1 and abs(self.col - col) == 2 or \
            abs(self.row - row) == 2 and abs(self.col - col) == 1:
            if piece_at_destination is not None and \
                piece_at_destination.player != self.player:
                return True, piece_at_destination
            return True, None

        return False, None

class Bishop(Piece):
    def __init__(self, 
                name: str, 
                game: Game,
                player: Player, 
                row: int, 
                col: int) -> None:
        super().__init__(name, game, player, row, col)

    def check_rules(self, row: int, col: int) -> tuple:
        return self.validate_diagonal(row, col)

class Rook(Piece):
    def __init__(self, 
                name: str, 
                game: Game,
                player: Player, 
                row: int, 
                col: int) -> None:
        super().__init__(name, game, player, row, col)

    def check_rules(self, row: int, col: int) -> tuple:
        return self.validate_line(row, col)

class Queen(Piece):
    def __init__(self, 
                name: str, 
                game: Game,
                player: Player, 
                row: int, 
                col: int) -> None:
        super().__init__(name, game, player, row, col)

    def check_rules(self, row: int, col: int) -> tuple:
        is_valid, captured_piece = self.validate_line(row, col)
        if is_valid:
            return is_valid, captured_piece

        return self.validate_diagonal(row, col)

class King(Piece):
    def __init__(self, 
                name: str, 
                game: Game,
                player: Player, 
                row: int, 
                col: int) -> None:
        super().__init__(name, game, player, row, col)

    def check_rules(self, row: int, col: int) -> tuple:
        piece_at_destination = self.game.get_piece_at_coordinate(row, col)
        is_valid = abs(row - self.row) in (0,1) and abs(col - self.col) in (0,1)
        if piece_at_destination is not None and piece_at_destination.player == self.player:
            return False, None
        return is_valid, piece_at_destination
    
def have_same_sign(val1: int, val2: int) -> bool:
    """
    Checks if two integers have the same sign
    """
    return abs(val1 + val2) == abs(val1) + abs(val2)

def get_direction(from_val: int, to_val: int) -> int:
    """
    Gets the direction between two integers
    e.g.
    from 1 to 200 -> 1
    from 1 to -5 -> -1 
    """
    return int((to_val - from_val) / abs(to_val - from_val))