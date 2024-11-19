import inspect
import asyncio
import shelve
from player_class import player
from item_classes import container
import re
# a basic play game loop
#a passive self healing heatlh and mana
async def passive_heal(player):
    #while player is active
    while player.active == True:
        #wait 15 seconds
        await asyncio.sleep(15)
        #get current values
        current_health = player.vitals_getter('health')
        current_mana = player.vitals_getter('mana')
        #add 1 health and mana, get_n_set had a limiter to not go over max
        player.get_n_set('health', 1)
        player.get_n_set('mana', 1)
        #if mana or health changed display mana and health
        if current_health != player.vitals_getter('health max') or current_mana != player.vitals_getter('mana max'):
            player.mana_display()
            player.health_display()
#play game function to load or instance a player and 
def play_game():
    play_name = input('what is your name? \n')
    character = None
    try:
        with shelve.open('player.db') as db:
            character = db[play_name]
    except KeyError:
        character = player(play_name)
    character.active = True
    character.refresh_vitals()
    character.refresh_active()
    asyncio.run(game_loop(character))
#EXPERIMENTAL CODE
#function to handle user inputs on a seperate thread as to not block event loop
async def handle_input(queue):
    while True:
        user_input = await asyncio.to_thread(input, "what do you do? \n")
        await queue.put(user_input)
#gameplay loop
async def game_loop(player):
    print(f'''you wake up suddenly in a new place and new time.
          with no memories of your past, only your name {player.name}''')
    player.look()
    #instance async queue
    queue = asyncio.Queue()
    # start passive healing in background
    asyncio.create_task(passive_heal(player))
    # start listening for user input
    asyncio.create_task(handle_input(queue))
    #gameplay while loop based on player.active attribute 
    while player.active == True:
        #handles death.
        if player.alive == False:
            choice = input("restart or quit?\n")
            if choice == 'restart': play_game()
            else: player.quit()
        #get user input from queue
        player_input = await queue.get()
        #validate user imput
        #making lists of acceptable syntax
        actions = [x for x in player.basic_action.keys()]
        room_actions = []
        if len(player.location.room_actions)>0:
             room_actions = [x for x in player.location.room_actions.keys()]
        attacks = [x for x in player.attacks.keys()]
        #splitting user input into syntax and target as of right now only one word syntax in accepted
        input_split = player_input.split(' ', 1)
        user_action = input_split[0]
        #checking user input against lists
        #checking basic actions list
        if user_action in actions:
            if len(input_split) > 1:
                target = input_split[1]
                player.basic_action[user_action][0](target)
                continue        
            else:
                try:
                    player.basic_action[user_action][0]()
                except TypeError:
                    print(f'{user_action} what?')
                    continue
        #checking against room actions I might need to build this out more with error handing
        elif user_action in room_actions:
            if len(input_split) > 1:
                target = input_split[1]
                try: 
                    player.location.room_actions[user_action](target)
                except AttributeError:
                    print(f"try just {user_action}")
                    continue
            player.location.room_actions[user_action](player)
        #checking against attacks
        elif user_action in attacks:
            # if a target was designated
            if len(input_split) > 1:
                #check to make sure target is vaild
                target= input_split[1]        
                #if valid performs attack, displays player mana and health
                #checks if async
                is_async = inspect.iscoroutinefunction(player.attacks[user_action])
                if is_async: 
                    try:
                        asyncio.create_task(player.attacks[user_action](target))
                    except AttributeError:
                        print('that target is not here')
                else:
                    try:
                        player.attacks[user_action](target)
                    except AttributeError:
                        print('that target is not here')
                if player.in_combat == False:                            
                    player.enter_combat(target)
                continue
            # if no target was selects launch attack anyway
            else:
                #if code is async handle here
                is_async = inspect.iscoroutinefunction(player.attacks[user_action])
                if is_async: 
                    asyncio.create_task(player.attacks[user_action]())
                    #except AttributeError:
                    #   print('that target is not here')
                #calls code if sync
                else:
                    #try:
                   player.attacks[user_action]()
                    #error handling
                    #except TypeError:
                    #    print(f'{user_action} what?')
        else: print('please select an action')
#a validate target function, similar to col_n_val, but just validating. 
'''def validate_target(location, target_str):
    #get regex patterns from location parameter
    regex_patterns = [x.regex for x in location]
    # check regex for match
    index = 0
    for pattern in regex_patterns:
        #if match use index to select target object, return turn and object
        result = re.search(pattern, target_str)
        if result:
            target_obj = location[index]
            return True, target_obj
        #else advance index and try again
        else:
            index +=1
    # if no pattern matches return false and none
    return False, None'''
#proof of concept test functions
play_game()