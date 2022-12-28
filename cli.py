from logic import Game

game = Game()
game.add_pieces_to_board()

message = 'Welcome!'
while game.winner is None:
    print(game.represent_board())

    success = False
    while not success and game.winner is None:
        print(message)
        # gather entry
        text = f'{game.current_player.name}, make a move: '
        notation = input(text)
        parsed_notation = game.parse_notation(notation)
        if parsed_notation is None:
            message = "Invalid entry"
            continue

        # make move
        success, message = game.move_w_notation(parsed_notation)

print(game.represent_board())
print(f'Game over! {game.winner.name} is the winner.')
