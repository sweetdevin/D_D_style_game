from player_class import player
# a basic play game loop
def play_game():
    play_name = input('what is your name? \n')
    character = player(play_name)
    character.active = True
    character.refresh_vitals()
    game_loop(character)
def game_loop(player):
    print(f'''you wake up suddenly in a new place and new time.
          with no memories of your past, only your name {player.name}''')
    player.look()
    while player.active == True:
        if player.alive == False:
            choice = input("restart or quit?\n")
            if choice == 'restart': play_game()
            else: player.quit()
        player_input = input('what action do you take? \n')
        actions = [x for x in player.basic_action.keys()]
        input_split = player_input.split(' ', 1)
        user_action = input_split[0]
        if user_action in actions:
            if len(input_split) > 1:
                target = input_split[1]
                try: 
                    player.basic_action[user_action][0](target)
                except TypeError:
                    print("what?")
                continue
            player.basic_action[user_action][0]()
        else: print('please select an action')

#proof of concept test functions
play_game()