from class_test import creature
from rooms import spawnnode
from random import randint
from item_classes import item_class, consumable, container, equipment, key, door
# collect and validate player inputs function 
def col_n_validate(location, func_name_str, fail_str, target = None, *args):
    # filters options if needed args are class types to include

    names = [x.name for x in location]
    if args:
        names = [x.name for x in location if type(x) in args]
    if target == None:
        if len(names) == 0:
            return False, "you can't do that here"    
        print(names)
        target = input(f'{func_name_str} what? \n')
    #validate player input is valid returns index of input if true
    print(target)
    if target in names:
        index = [x.name for x in location].index(target)
        return True, index
    #return fail
    return False, f'that {fail_str} is not here'
player_text =  'yourself, look in a mirror'
class player(creature):
    def __init__(self, name, text=player_text) -> None:
        super().__init__(name, text)
        self.stats = {'str':2, 'agi':2, 'int':2}
        self.location = spawnnode
        self.basic_action = {'look' : [self.look, 'look around your current room'], 'travel': [self.traverse, 'travel to another room'],
                             'me': [self.me,'examine yourself and what you are carrying'], 'quit': [self.quit, 'quits the game'], 
                             'attack': [self.enter_combat, 'attacks an enemy'], 'examine': [self.examine, 'loot at objects in the room'], 
                             'take' : [self.take_item, 'take an item from the room'], 'use': [self.use, 'use an item from  your inventory'],
                               'loot': [self.loot, 'loots a container in the room'], 'help': [self.help, 'displays this help menu'],
                               'level': [self.level_up, 'if you have enough experience you can level up'], 
                               'search': [self.search, 'search a target to discover hidden things']}
        self.active = False
        self.in_combat = False
        self.alive = True
        self.attacks = self.attacks | {'run': self.run, 'calm': self.calm,
                                       'dev touch': self.dev_touch}
        self.consumables = []
        self.experience = 0
        self.level = 1
        self.active_effects = {'health': 0, 'health max': 0, 'mana':0, 'mana max':0,
                               'attack value':0, 'defence value':0}
    # level up function
    def level_up(self):
        #check experience
        if self.experience >= self.level * 100:
            self.experience -= self.level * 100
            self.level += 1
            #award stat raises and start stat raise loop
            count = 6  
            while count > 0:
                stat_to_raise = input(f'{count} raises left. What stat do you improve? "str" "agi" or "int"\n')
                if stat_to_raise in ['str', 'agi', 'int']:
                    self.stats[stat_to_raise] += 1
                    count -=1
                else: print('please type a stat "str", "agi" or "int"')
            print("you have leveled up \n you are fully healed")
            self.refresh_vitals()
            self.refresh_active()
            self.get_n_set('mana', self.vitals_getter('mana max'))
            self.get_n_set('health', self.vitals_getter('health max'))
    # refresh equipment func
    def set_active(self, stats_string, effect):
        self.active_effects[stats_string] += effect
        self.get_n_set(stats_string, self.active_effects[stats_string])
    def refresh_active(self):
        for key, value in self.active_effects.items():
            self.get_n_set(key, value)      
    #add consumable 
    def add_consumable(self, item_obj):
        self.consumables.append(item_obj)
    #basic player specific commands
    def help(self):
        print([x for x in self.basic_action.keys()])
        detail = input("type a command for more details or exit to leave this menu \n")
        if detail == 'exit': return
        try:
            print(self.basic_action[detail][1])
        except KeyError:
            print(f'no help on {detail}')
        return self.help()  

    # a travel function to move the play    
    def traverse(self, target=None):
        #print travel directions, collect input
        direction_list = self.location.get_exits()
        if target not in direction_list:
            print(direction_list)
            target = input('which way? \n')
        #validate input, change location, call look
        door_list = [x for x in self.location.contents if type(x) == door]
        door_blocking = [x.exit for x in door_list]
        if target in door_blocking:
            print('there is a locked door in your way')
            return
        elif target in direction_list:
            self.location = self.location.exits[target]
            print(f'you travel {target}')
            self.look()
            #check for aggressive mobs, start combat if true
            for value in self.location.contents:
                if type(value) == creature or type(value).__bases__[0] == creature:
                    if value.aggressive == True:
                        print(f'{value.name} attacks you')
                        self.in_combat = True
                        self.combat_loop(value)
        else: print('cannot travel that way') 
    # a simple look around or location command
    def look(self):
        #print room text, room contents.
        print('you look around the room')
        print(self.location.description)
        exits = self.location.get_exits()
        print(f'obvious exits are {exits}')
        creature_names = [x.name for x in self.location.contents if type(x).__bases__[0] == creature or type(x) == creature]
        if len(creature_names) > 0:    
            for x in creature_names:
                print(f'creature - {x}')
        else: print('no creatures')
        item_names = [x.name for x in self.location.contents if type(x).__bases__[0] == item_class]
        if len(item_names) > 0:
            for x in item_names:
                print(f'item - {x}')
        else: print('no items')        
    # an in game self status check
    def me(self):
        print(self)
        print(f'level - {self.level}')
        if self.experience > self.level * 100:
            print('you can level')
        else: print(f'you need {self.level * 100 - self.experience} more experience to level up')
        print(f'equipment, {self.items}')
        print(f'consumables, {self.consumables}')
    # an exit for the game loop
    def quit(self):
        self.active = False
        print('so long and thanks for all the fish')
    #combat target aquisition ends by calling combat loop
    def enter_combat(self, target = None):
        #print targets
        targets = [x.name for x in self.location.contents if type(x).__bases__[0] == creature or type(x) == creature]
        if target == None:
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
        #health check on target
        if target.vitals_getter('health') <= 0: 
            #victory text, exit combat, make corpse from dead mob
            # remove mob and add corpse to room
            print(f'{self.name} is victorious')
            self.in_combat = False
            target.aggressive = False
            self.experience += target.exp_val * (1 - self.level/100)
            corpse = container(f'corpse of {target.name}', 'a bloody mangled corpse')
            for item in target.items:
                corpse.add_items(item)
            self.location.remove_item(target)
            self.location.add_item(corpse)
            return
        #still in combat check
        if self.in_combat == False:
            return
        #npc attack phase
        npc_attacks = [x for x in target.attacks.keys()]
        npc_index = randint(0, len(npc_attacks) -1)
        npc_attack = npc_attacks[npc_index]
        target.attacks[npc_attack](self)
        #player death event handled in game loop
        if self.vitals_getter('health') <= 0:
            print(f'{self.name} has died')
            self.alive = False
            self.in_combat = False
            target.aggressive = False
            return
        return self.combat_loop(target)
    # a run away command
    def run(self, target):
        self.in_combat = False
        self.traverse(target)
    # an end combat command
    def calm(self, target):
        chance = randint(0, 1)
        if chance == 0:
            print(f'{target.name} fails to calm down')
        if chance == 1:
            self.in_combat = False
            target.aggressive = False
            print(f'{target.name} calms down')
    # special developers spell to instakill
    def dev_touch(self, target):
        print(f'with godlike powers {self.name}, points at {target.name} and says die')
        target.vitals_setter('health', 0)

    # examine items function
    def examine(self, target = None):
        #col and val fun returns either success and index or fail and return string
        success, value = col_n_validate(self.location.contents, 'examine', 'item', target)
        if success:
            # selects item obj and print name and text
            item_obj = self.location.contents[value]
            print(f'you examine {item_obj}')
            print(item_obj.text)
            if type(item_obj) == container:
                # if item_obj is a container type print contents
                if item_obj.is_locked == True:
                    print('is locked')
                    return
                print('contains')
                if len(item_obj.contents) == 0:
                    print('nothing')
                else: print([x.name for x in item_obj.contents])
        # print value if col and val fails
        else: print(value)
    # take item function    
    def take_item(self, target = None):
        # col and val function
        success, value = col_n_validate(self.location.contents,'take', 'item', target, consumable, equipment, key)
        if success:
            # if success of col and val, select item obj, remove from room
            # add to player inventory, link item obj to player
            item_obj = self.location.contents[value]
            self.location.contents.remove(item_obj)
            item_obj.player_link(self)
            if type(item_obj) == consumable or key:
                self.add_consumable(item_obj)
            elif type(item_obj) == equipment:
                self.add_item(item_obj)
                item_obj.use(self)
            print(f'you take {item_obj}')
        # if col and val fails print fail string
        else: print(value)
    # loot container function
    def loot(self, target = None):
        # col and val function
        success, value =col_n_validate(self.location.contents, 'loot', 'containers', target, container)
        if success:
            # if success, take all from cont obj, add each item to player,
            # link items, remove item from container
            cont_obj = self.location.contents[value]
            if cont_obj.is_locked == True:
                print('that container in locked')
            for item in [x for x in cont_obj.contents]:
                item.player_link(self)
                if type(item) == equipment:
                    self.add_item(item)
                    item.use()
                elif type(item) == consumable or key:
                    self.add_consumable(item)
                print(f'you take {item}')
                cont_obj.contents.remove(item)
        # if success fails print fail string
        else: print(value)
    # use item function 
    def use(self, target = None):
        # col and val function
        success, value = col_n_validate(self.consumables, 'use', 'item', target)
        if success:
            item = self.consumables.pop(value)
            item.use()
        else: print(value)

    def search(self, target):
        try:
            found_obj = self.location.search[target]
        except KeyError:
            print('search what?')
            return
        if type(found_obj) == str:
            print(found_obj)
            return
        self.location.discover(found_obj)