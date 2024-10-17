from class_test import creature
from rooms import spawnnode
from random import randint
from item_classes import item_class, consumable, container, equipment
# collect and validate player inputs function 
def col_n_validate(location, func_name_str, fail_str, **kwargs):
    names = [x.name for x in location]
    if 'filter' in kwargs:
        names = [x.name for x in location if type(x) == kwargs['filter']]
        if 'bang' in kwargs:
            names = [x.name for x in location if type(x) != kwargs['filter']]
    #validates there is an obj to act on, returns if fails
    if len(names) == 0:
        return False, "you can't do that here"    
    print(names)
    player_input = input(f'{func_name_str} what? \n')
    #validate player input is vailid returns index of input if true
    if player_input in names:
        index = [x.name for x in location].index(player_input)
        return True, index
    #return fail
    return False, f'that {fail_str} is not here'

class player(creature):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.location = spawnnode
        self.basic_action = {'look' : self.look, 'travel': self.traverse,
                             'me': self.me, 'quit': self.quit, 'attack': self.enter_combat,
                             'examine': self.examine, 'take': self.take_item,
                             'use': self.use, 'loot': self.loot}
        self.health = 500
        self.active = False
        self.in_combat = False
        self.attacks = self.attacks | {'run': self.run,
                                            'calm': self.calm}
        self.items = []
        self.consumables = []
    #basic player specific commands
    # a travel function to move the play    
    def traverse(self):
        #print travel directions, collect input
        direction_list = [x for x in self.location.exits.keys()]
        print(direction_list)
        direction = input('which way? \n')
        #validate input, change location, call look
        if direction in direction_list:
            self.location = self.location.exits[direction]
            self.look()
            #check for aggressive mobs, start combat if true
            for value in self.location.contents:
                if type(value).__bases__[0] == creature:
                    if value.aggressive == True:
                        print(f'{value.name} attacks you')
                        self.in_combat = True
                        self.combat_loop(value)
        else: print('cannot travel that way') 
    # a simple look around or location command
    def look(self):
        #print room text, room contents.
        print(self.location.description)
        exits = [x for x in self.location.exits.keys()]
        print(f'obvious exits are {exits}')
        creature_names = [x.name for x in self.location.contents if type(x).__bases__[-1] == creature]
        if len(creature_names) > 0:    
            for x in creature_names:
                print(f'creature - {x}')
        else: print('no creatures')
        item_names = [x.name for x in self.location.contents if type(x).__bases__[-1] == item_class]
        if len(item_names) > 0:
            for x in item_names:
                print(f'item - {x}')
        else: print('no items')        
    # an in game self status check
    def me(self):
        print(self)
        print(f'equipment, {self.items}')
        print(f'consumables, {self.consumables}')
    # an exit for the game loop
    def quit(self):
        self.active = False
        print('so long and thanks for all the fish')
    #combat target aquisition ends by calling combat loop
    def enter_combat(self):
        #print targets
        targets = [x.name for x in self.location.contents if type(x).__bases__[-1] == creature]
        if len(targets) == 0:
            print('there is nothing here to attack')
            return 
        print(targets)
        #select and validate targets
        target = input('attack what? \n')
        if target not in targets:
            print('that target does not exist here')
            return
        self.in_combat = True
        print(f'you attack {target}')
        target_index = [x.name for x in self.location.contents].index(target)
        self.combat_loop(self.location.contents[target_index])
    # the combat loop
    def combat_loop(self, target):
        # turn target agressive
        target.aggressive = True
        if self.in_combat == False: 
            return
        #print attacks
        attacks = [x for x in self.attacks.keys()]
        print(attacks)
       #select, validate, and call attack 
        player_input = input('what action do you take? \n')
        if player_input in attacks:
           self.attacks[player_input](target)
        else:
            print(f'{self.name} is confused by your command and uses a basic attack')
            self.basic_attack(target)
        #still in combat check
        if self.in_combat == False:
            return
        #npc attack phase
        npc_attacks = [x for x in target.attacks.keys()]
        npc_index = randint(0, len(npc_attacks) -1)
        npc_attack = npc_attacks[npc_index]
        target.attacks[npc_attack](self)
        #health check
        if target.health <= 0: 
            #victory text, exit combat, make corpse from dead mob
            # remove mob and add corpse to room
            print(f'{self.name} is victorious')
            self.in_combat = False
            target.aggressive = False
            corpse = container(f'corpse of {target.name}', 'a bloody mangled corpse')
            for item in target.items:
                corpse.add_items(item)
            self.location.remove_item(target)
            self.location.add_item(corpse)
            return
        if self.health <= 0:
            #player death... needs to be expaned. have to figure out death.
            print(f'{self.name} has died')
            self.in_combat = False
            target.aggressive = False
            return
        return self.combat_loop(target)
    # a run away command
    def run(self, target):
        self.in_combat = False
        self.traverse()
    # an end combat command
    def calm(self, target):
        chance = randint(0, 1)
        if chance == 0:
            print(f'{target.name} fails to calm down')
        if chance == 1:
            self.in_combat = False
            target.aggressive = False
            print(f'{target.name} calms down')
    # examine items function
    def examine(self):
        #col and val fun returns either success and index or fail and return string
        success, value = col_n_validate(self.location.contents, 'examine', 'item')
        """items = [x.name for x in self.location.items]
        print(items)
        item_to_examine = input('examine what? \n')"""
        if success:
            # selects item obj and print name and text
            item_obj = self.location.contents[value]
            print(item_obj)
            print(item_obj.text)
            if type(item_obj) == container:
                # if item_obj is a container type print contents
                print('contains')
                if len(item_obj.contents) == 0:
                    print('nothing')
                else: print([x.name for x in item_obj.contents])
        # print value if col and val fails
        else: print(value)
    # take item function    
    def take_item(self):
        # col and val function
        success, value = col_n_validate(self.location.contents,'take', 'item', filter = creature, bang = True)
        """
        names = [x.name for x in self.location.items if type(x) != container]
        print(names)
        item = input('take what? \n')"""
        if success:
            # if success of col and val, select item obj, remove from room
            # add to player inventory, link item obj to player
            item_obj = self.location.contents[value]
            self.location.contents.remove(item_obj)
            item_obj.player_link(self)
            if type(item_obj) == consumable:
                self.consumables.append(item_obj)
            if type(item_obj) == equipment:
                self.items.append(item_obj)
                item_obj.use()
        # if col and val fails print fail string
        else: print(value)
    # loot container function
    def loot(self):
        # col and val function
        success, value =col_n_validate(self.location.contents, 'loot', 'containers', filter=container)
        """containers = [x.name for x in self.location.items if type(x) == container]
        if len(containers) == 0:
            print('no containers here')
            return
        print(containers)
        cont_str = input('loot what? \n') """
        if success:
            # if success, take all from cont obj, add each item to player,
            # link items, remove item from container
            cont_obj = self.location.contents[value]
            for item in [x for x in cont_obj.contents]:
                item.player_link(self)
                if type(item) == equipment:
                    self.items.append(item)
                    self.items[-1].use()
                if type(item) == consumable:
                    self.consumables.append(item)
                cont_obj.contents.remove(item)
        # if success fails print fail string
        else: print(value)
    # use item function 
    def use(self):
        # col and val function
        success, value = col_n_validate(self.consumables, 'use', 'item')
        """
        consumables = [x for x in self.consumables]
        if len(consumables) == 0:
            print('you have no items')
            return
        consumables_names = [x.name for x in consumables]
        print(consumables_names)
        choice = input('use what? \n') """
        if success:
            item = self.consumables.pop(value)
            item.use()
        else: print(value)
# a basic play game loop
def play_game():
    play_name = input('what is your name? \n')
    character = player(play_name)
    character.active = True
    game_loop(character)
def game_loop(player):
    print(f'''you wake up suddenly in a new place and new time.
          with no memories of your past, only your name {player.name}''')
    player.look()
    while player.active == True:
        print('what action do you take?')
        actions = [x for x in player.basic_action.keys()]
        print(actions)
        user_action = input('')
        if user_action in actions:
            player.basic_action[user_action]()
        else: print('please select an action')

#proof of concept test functions
play_game()
