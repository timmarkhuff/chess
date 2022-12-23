from logic import Game

def validate_int(x: int) -> int:
    # attempt to convert to an integer
    try:
        x = int(x)
    except ValueError:
        return  None
    
    # ensure that the integer is within bounds
    if 0 <= x <= 7:
        return x
    else:
        return None

game = Game()
game.add_pieces_to_board()

message = 'Welcome!'
while game.winner is None:
    print(game.represent_board())
    print(message)

    text = f'{game.current_player.name}, please select a column: '
    col = validate_int(input(text))
    if col is None:
        continue
    text = f'{game.current_player.name}, please select a row: '
    row = validate_int(input(text))
    if row is None:
        continue

    piece, message = game.select_piece(row, col)

    if piece is None:
        continue

    while game.winner is None:
        text = f'Move {game.selected_piece.name} at ({col},{row}) to column: '
        move_col = validate_int(input(text))
        if move_col is None:
            print('Invalid entry!')
            break

        text = f'Move {game.selected_piece.name} at ({col},{row}) to row: '
        move_row = validate_int(input(text))
        if move_row is None:
            print('Invalid entry!')
            continue

        success, message = game.move_selected_piece(move_row, move_col)
        winner = game.check_winner()
        if success:
            break
        
        print(game.represent_board())
        print(message)

print(game.represent_board())
print(f'Game over! {winner.name} is the winner.')
