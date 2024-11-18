from class_test import creature, murlock 
from rooms import spawnnode
from random import randint
from item_classes import item_class, consumable, container, equipment, key, door
import asyncio
import re
creature_classes = [creature, murlock]
# collect and validate player inputs function 
'''def col_n_validate(location, func_name_str, fail_str, target = None, *args):
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
    if target in names:
        index = [x.name for x in location].index(target)
        return True, index
    #return fail
    return False, f'that {fail_str} is not here'''
#a validate target function, similar to col_n_val, but just validating. 
def validate_target(location, target_str):
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
    return False, None

player_text =  'yourself, look in a mirror'
class player(creature):
    def __init__(self, name, text=player_text) -> None:
        super().__init__(name, text)
        self.stats = {'str':2, 'agi':2, 'int':2}
        self.location = spawnnode
        self.basic_action = {'look' : [self.look, 'look around your current room'], 'travel': [self.traverse, 'travel to another room'],
                             'me': [self.me,'examine yourself and what you are carrying'], 'quit': [self.quit, 'quits the game'], 
                              'examine': [self.examine, 'loot at objects in the room'], 
                             'take' : [self.take_item, 'take an item from the room'], 'use': [self.use, 'use an item from  your inventory'],
                               'loot': [self.loot, 'loots a container in the room'], 'help': [self.help, 'displays this help menu'],
                               'level': [self.level_up, 'if you have enough experience you can level up'], 
                               'search': [self.search, 'search a target to discover hidden things']}
        self.active = False
        self.in_combat = False
        self.target = None
        self.alive = True
        self.attacks = self.attacks | {'attack': self.enter_combat, 'run': self.run, 'calm': self.calm,
                                       'dev_touch': self.dev_touch, 'slam': self.slam,
                                       'heal' : self.heal, 'warcry' : self.attack_buff}
        self.consumables = []
        self.experience = 0
        self.level = 1
        self.active_effects = {'health': 0, 'health max': 0, 'mana':0, 'mana max':0,
                               'attack value':0, 'defence value':0}
    #getters and setters for target
    def target_setter(self, target_obj):
        self.target = target_obj
    def target_getter(self):
        return self.target
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
            #print and heal player
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
        try:
            for item in self.items:
                self.set_active(item.stats, item.effect)
        except ValueError:
            self.active = {'health': 0, 'health max': 0, 'mana':0, 'mana max':0,
                               'attack value':0, 'defence value':0}
            

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
        if target == None:
            print('travel where?')
            return
        for key, pattern in self.location.exits_regex.items():
                result = re.match(pattern, target)
                if result:
                    target = key
        direction_list = self.location.get_exits()
        # check to see if door blocking
        door_list = [x for x in self.location.contents if type(x) == door]
        door_blocking = [x.exit for x in door_list]
        # If door print and return
        if target in door_blocking:
            print('there is a locked door in your way')
            return
        #validate direction
        elif target in direction_list:
            self.in_combat = False
            self.location = self.location.exits[target]
            print(f'you travel {target}')
            self.look()
            #check for aggressive mobs, start combat if true
            for value in self.location.contents:
                if type(value) == creature or type(value).__bases__[0] == creature:
                    if value.aggressive == True:
                        print(f'{value.name} attacks you')
                        self.enter_combat(value)
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
        #if target valid set combat to True
        if target == None:
            print('attack what?')
            return
        self.in_combat = True
        #set default target to mob
        self.target_setter(target)
        target.aggressive = True
        print(f'you attack {target.name}')
        #call combat async function on target
        self.combat(self.target_getter())
    # victory check for comabt
    def victory_check(self, target):
        # check targets health is below 0
        if target.vitals_getter('health') <= 0:
            #print victory
            print(f'{self.name} is victorious')
            #remove from combat loop
            self.in_combat = False
            target.aggressive = False
            #add experience based on level
            self.experience += target.exp_val * (1 - self.level/100)
            #instance a corpse from the mob
            corpse = container('a fresh corpse', f'corpse of {target.name}')
            corpse.set_regex(r'^corpse$')
            #start corpse decay timer
            asyncio.create_task(corpse.decay(self.location))
            #load corpse with mobs items
            for item in target.items:
                corpse.add_items(item)
            #remove mob
            self.location.remove_item(target)
            #add corpse
            self.location.add_item(corpse)
            #start respawn timer
            asyncio.create_task(self.location.reswpawn())
            #heal mob
            target.refresh_vitals()
            #return that victory was achieved
            return True
    #death check
    def death_check(self, target):
        #check player health is below zero
        if self.vitals_getter('health') <= 0:
                #print death  notice
                print(f'{self.name} has died')
                #set alive, combat, and mob aggression
                self.alive = False
                self.in_combat = False
                target.aggressive = False
                #return True 
                return True
    #melee attack loop
    async def basic_attack_loop(self, target):
        #while player in is combat
        while self.in_combat == True:
            #perform a melee attack on target
            self.basic_attack(target)
            #see if target survived
            victory = self.victory_check(target)
            #if target died end loop
            if victory:
                return
            #target melee attacks me
            target.basic_attack(self)
            special_chance = randint(1, 10)
            if special_chance == 5 & len(target.special_attacks) > 0:
                special_list = [x for x in target.special_attacks.keys()]
                special_index = randint(0, len(special_list) - 1)
                special_attack_str = special_list[special_index]
                target.special_attacks[special_attack_str](self)
            #see if i lived
            death = self.death_check(target)
            #if i died end loop
            if death:
                return
            #wait 5 seconds before repeating
            self.mana_display()
            self.health_display()
            target.health_display()
            await asyncio.sleep(5)
    # a function to assign combat loop as a task to run in the background
    def combat(self, target):
        asyncio.create_task(self.basic_attack_loop(target))
    # a simple special attack for testing
    def slam(self, target = None):
        if target == None:
            target = self.target_getter()
        valid = self.mana_check_n_set(5)
        if valid:
            target.get_n_set('health', 20, True)
            print(f'you slam down hard on {target.name}')
    # a simple async buff for testing
    async def attack_buff(self, target =None ):
        if target == None:
            target = self
        target.get_n_set('attack value', 10)
        await asyncio.sleep(60)
        target.get_n_set('attack value', 10, True)

    #a simple heal for testing
    def heal(self, target = None):
            if target == None:
                target = self
            target.get_n_set('health', 5 + 5 * self.stats_getter('int'))
    # a run function
    def run(self, target = None):
        if target == None:
            exit_list = self.location.get_exits()
            random_int = randint(0, len(exit_list) -1)
            random_exit = exit_list[random_int]
            target = random_exit
        self.in_combat = False
        self.traverse(target)
    # an end combat command
    def calm(self, target=None):
        if target == None:
            target = self.target_getter()
        chance = randint(0, 1)
        if chance == 0:
            print(f'{target.name} fails to calm down')
        if chance == 1:
            self.in_combat = False
            target.aggressive = False
            print(f'{target.name} calms down')
    # special developers spell to instakill
    def dev_touch(self, target=None):
            if target == None:
                target = self.target_getter()
            print(f'with godlike powers {self.name}, points at {target.name} and says die')
            target.vitals_setter('health', 0)
    # examine items function
    def examine(self, target = None):
        if target == None:
            print('examine what?')
            return
        valid_1, target_1 = validate_target(self.location.contents, target)
        valid_2, target_2 = validate_target(self.consumables, target)
        if valid_1:
            target = target_1
        elif valid_2:
            target = target_2
        else: 
            print('examine what?')
            return
        print(f'you examine {target}')
        print(target.text)
        if type(target) == container:
            # if item_obj is a container type print contents
            if target.is_locked == True:
                print('is locked')
                return
            print('contains')
            if len(target.contents) == 0:
                print('nothing')
            else: print([x.name for x in target.contents])
    # take item function    
    def take_item(self, target = None):
            # add to player inventory, link item obj to player
        valid, target_obj = validate_target(self.location.contents, target)
        if not valid:
            print('you cannot take that')
            return
        if type(target_obj) in [consumable, equipment, key]:
            self.location.remove_item(target_obj)
            target_obj.player_link(self)
            if type(target_obj) == consumable or key:
                self.add_consumable(target_obj)
            elif type(target_obj) == equipment:
                self.add_item(target_obj)
                target_obj.use(self)
            print(f'you take {target_obj.name}')
            #start respawn timer
            asyncio.create_task(self.location.reswpawn())
        else:
            print('you cannot take that')
    # loot container function
    def loot(self, target = None):
        if target == None:
            print('loot what?')
            return
        valid, target_obj = validate_target(self.location.contents, target)
        if not valid:
            print('you cannot loot that')
            return
        if type(target_obj) == container:
            if target_obj.is_locked == True:
                print('that container in locked')
            for item in [x for x in target_obj.contents]:
                item.player_link(self)
                if type(item) == equipment:
                    self.add_item(item)
                    item.use()
                elif type(item) == consumable or key:
                    self.add_consumable(item)
                print(f'you take {item}')
                target_obj.contents.remove(item)
    # use item function 
    def use(self, target = None):
        if target == None:
            print('use what?')
            return
        valid, target_obj = validate_target(self.consumables, target)
        if valid:
            self.consumables.remove(target_obj)
            target_obj.use()
        else: print('use what?')
    # search function
    def search(self, target_str):
        #only error handling since user since objects are hidden
        for pattern, value in self.location.search.items():
            valid = re.search(pattern, target_str)
            if valid:
                found_obj = value
                if type(found_obj) == str:
                    #print string if string and return
                    print(found_obj)
                    return
                #if object call discover object fuction on object
                else:
                    self.location.discover(found_obj)
                    return
        print('search what?')
        return