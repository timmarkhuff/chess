class Piece:
    def __init__(self, 
                    game, 
                    player, 
                    row: int, 
                    col: int) -> None:
        self.game = game
        self.player = player
        self.row = row
        self.col = col
        self.type = self.__class__.__name__
        self.has_moved = False
        
        self.game.pieces.append(self)

    def capture_piece(self, piece) -> None:
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

    @property
    def active(self) -> bool:
        return self.row is not None and self.col is not None

class Pawn(Piece):
    def __init__(self, 
                game,
                player, 
                row: int, 
                col: int) -> None:
        super().__init__(game, player, row, col)
        self.name = 'p'
        self.original_row = row
        self.original_col = col

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
                en_passant_piece.player != self.player and \
                en_passant_piece.type == self.type:
            return True, en_passant_piece            
        
        # In all other cases, return False
        return False, None

class Knight(Piece):
    def __init__(self, 
                game,
                player, 
                row: int, 
                col: int) -> None:
        super().__init__(game, player, row, col)
        self.name = 'N'

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
                game,
                player, 
                row: int, 
                col: int) -> None:
        super().__init__(game, player, row, col)
        self.name = 'B'

    def check_rules(self, row: int, col: int) -> tuple:
        return self.validate_diagonal(row, col)

class Rook(Piece):
    def __init__(self, 
                game,
                player, 
                row: int, 
                col: int) -> None:
        super().__init__(game, player, row, col)
        self.name = 'R'

    def check_rules(self, row: int, col: int) -> tuple:
        return self.validate_line(row, col)

class Queen(Piece):
    def __init__(self, 
                game,
                player, 
                row: int, 
                col: int) -> None:
        super().__init__(game, player, row, col)
        self.name = 'Q'

    def check_rules(self, row: int, col: int) -> tuple:
        is_valid, captured_piece = self.validate_line(row, col)
        if is_valid:
            return is_valid, captured_piece

        return self.validate_diagonal(row, col)

class King(Piece):
    def __init__(self, 
                game,
                player, 
                row: int, 
                col: int) -> None:
        super().__init__(game, player, row, col)
        self.name = 'K'

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