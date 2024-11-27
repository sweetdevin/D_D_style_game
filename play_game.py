import inspect
import asyncio
import shelve
from player_types import sorcerer
from item_classes import container
import re
# a basic play game loop
#a passive self healing heatlh and mana
player_classes = [sorcerer]
class_strings = ['sorcerer']
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
        count = 1
        for string in class_strings:
            print(f'{count}, {string}')
        class_choice = input('what are your abilities? \n')
        if class_choice == '1' or class_choice == 'sorcerer':
            character = sorcerer(play_name)
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
        #if player is dead
        if player.alive == False:
            # user input to restart game or quit
            # I MIGHT NEED TO REWORK THIS SO IT DOESN'T GLITCH THE ASYNC
            choice = input("restart or quit?\n")
            if choice == 'restart': play_game()
            else: player.quit()
        #get user input from queue
        player_input = await queue.get()
        #making lists of acceptable syntax
        #list for basic actions
        actions = [x for x in player.basic_action.keys()]
        # empty list for room actions
        room_actions = []
        # populate list with room actions if applicable. This prevents and error is no room actions
        if len(player.location.room_actions)>0:
             room_actions = [x for x in player.location.room_actions.keys()]
        #list for attacks
        attacks = [x for x in player.attacks.keys()]
        #splitting user input into syntax and target as of right now only one word syntax in accepted
        input_split = player_input.split(' ', 1)
        user_action = input_split[0]
        try:
            target = input_split[1]
        except IndexError: target = None
        #checking user input against lists
        #checking basic actions list
        if user_action in actions:
            # if target was listed call action with target
            if target:
                player.basic_action[user_action][0](target)
                continue        
            # if no target was listed try calling action with no target
            else:
                try:
                    player.basic_action[user_action][0]()
                # ERROR HANDLING MAY BE UNNECESSARY WITH NEW VALIDATION
                except TypeError:
                    print(f'{user_action} what?')
                    continue
        #checking against room actions
        elif user_action in room_actions:
            # if target was passed call action with target
            if target:
                try: 
                    player.location.room_actions[user_action](target)
                # error handling might need examining or adjusting
                except AttributeError:
                    print(f"try just {user_action}")
                    continue
            #if no target was passed call with no target
            else: player.location.room_actions[user_action](player)
        #checking against attacks
        elif user_action in attacks:
            # if a target was designated
            if target:       
                #checks if async
                is_async = inspect.iscoroutinefunction(player.attacks[user_action])
                # if async add to task list
                if is_async: 
                    try:
                        await asyncio.create_task(player.attacks[user_action](target))
                    except AttributeError:
                        print('that target is not here')
                # if not async call action with target
                else:
                    try:
                        player.attacks[user_action](target)
                    except AttributeError:
                        print('that target is not here, error handling')
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