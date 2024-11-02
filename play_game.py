import asyncio
from player_class import player
# a basic play game loop

async def passive_heal(player):
    while player.active == True:
        player.get_n_set('health', 1)
        player.get_n_set('mana', 1)
        await asyncio.sleep(15)
        print('you heal 1 health and mana')
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
        asyncio.run(passive_heal(player))
        if player.alive == False:
            choice = input("restart or quit?\n")
            if choice == 'restart': play_game()
            else: player.quit()
        player_input = input('what action do you take? \n')
        actions = [x for x in player.basic_action.keys()]
        room_actions = []
        if len(player.location.room_actions)>0:
             room_actions = [x for x in player.location.room_actions.keys()]
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
            try:
                player.basic_action[user_action][0]()
            except TypeError:
                print('what?')
                continue
        elif user_action in room_actions:
            if len(input_split) > 1:
                target = input_split[1]
                try: 
                    player.location.room_actions[user_action](target)
                except AttributeError:
                    print(f"try just {user_action}")
                continue
            player.location.room_actions[user_action](player)
        else: print('please select an action')

#proof of concept test functions
play_game()