from class_test import creature, murlock 
from rooms import spawnnode
from random import randint, choice
from item_classes import item_class, consumable, container, equipment, key, door
import asyncio
import re
creature_classes = [creature, murlock]
#a validate target function 
def validate_target(location, target_str, target_list = None):
    #if location is a dict
    if type(location) == dict:
        #loop checking keys vs target string
        for pattern, value in location.items():
            result = re.search(pattern, target_str)
            #if a match is found return true and the value
            if result:
                if target_list:
                    if type(value) not in target_list:
                        return False, None
                return True, value
    # else if location is a list
    elif type(location) == list:
    #get regex patterns from location parameter
        regex_patterns = [x.regex for x in location]
        # check regex for match
        # track itterations for index
        index = 0
        # loop checking patterns vs target string
        for pattern in regex_patterns:
            result = re.search(pattern, target_str)
            #if match return true and the index from location list
            if result:
                target_obj = location[index]
                if target_list:
                    if type(target_obj) not in target_list:
                        return False, None
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
                               'level': [self.level_up, 'if you have enough experience you can level up'], 'search': [self.search, 'search a target to discover hidden things'],
                               'equip': [self.equip, 'wear or wield a piece of equipment from your inventroy'], 'drop': [self.drop, 'drops an item from inventory'],
                               'remove': [self.remove, 'unequip an item'], 'equipment' : [self.display_equipment, 'show your current armour'],
                               'inventory' : [self.display_inventory, 'show what you are holding']}
        self.active = False
        self.in_combat = False
        self.target = None
        self.alive = True
        self.occupied = False
        self.attacks = self.attacks | {'attack': self.enter_combat, 'run': self.run, 'calm': self.calm,
                                       'dev_touch': self.dev_touch}
        self.experience = 0
        self.level = 1
    #getters and setters for target
    def target_setter(self, target_obj = None):
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
    # set and refresh equipment func
    #def set_active(self, effect_name, stats_string, effect):
     #   self.active_effects[effect_name] = [stats_string, effect]
      #  self.get_n_set(stats_string, self.active_effects[stats_string])
    def refresh_active(self):
        if len(self.active_effects) > 0:
            for value in self.active_effects.values():
                self.get_n_set(value[0], value[1])
    #def remove_active(self, effect_name):
     #   self.get_n_set(self.active_effects[effect_name][0], self.active_effects[1], True)
      #  del self.active_effects[effect_name]
    # an occupied check
    def occupied_check(self):
        # if occupied attribute is true print and return true
        if self.occupied == True:
            print('you are busy right now')
            return True
        # if occupied  is false return false
        else: return False
    def level_check(self, req_level):
        # if player level is less than required level print and return False
        if self.level < req_level:
            print('you are not a high enough level for that ability')
            return False
        # else return True
        else: return True
    # a busy a level combined designed to use before player class abilities
    def busy_n_level_check(self, req_level):
        # check occuiped status
        occupied = self.occupied_check()
        # check level
        level_pass = self.level_check(req_level)
        # if unoccupied and level_passes return True
        if occupied == False and level_pass == True:
            return True
        #else return false
        else: return False    
    #mana check to be used before all mana costing attacks, 
    #makes sure self has mana if it does not returns false.
    async def mana_check_n_set(self, cost):
        # if current mana less than cost, print and return false
        if self.vitals_getter('mana') < cost:
            print(f'you lack the mind for that')
            return False
        #if true subtracts spell cost
        else:
            self.get_n_set('mana', cost, True)
            # self occupied to true print and wait casting time
            self.occupied = True
            print('you begin charging an ability')
            await asyncio.sleep(3)
            return True
    #a validate target wrapper with default target self.target
    def validate_default_target(self, location, target_str = None, target_list = None):
        #give target object a default value
        target_obj = None
        #if target_str was passed
        if target_str:
            valid, target_obj = validate_target(location, target_str, target_list)            
            # if validate failed print and return False
            if not valid:
                print('that target is not here')
                return False
        # if no target was passed assign default target
        elif target_str == None:
            target_obj = self.target_getter()
        # return target object
        return target_obj
    # a validate target wrapper with default being self
    def validate_default_self(self, location, target_str=None, target_list = None):
        # give target_obj a default value
        target_obj = None
        # if target_str was passed
        if target_str:
            valid, target_obj = validate_target(location, target_str, target_list)
            # if validate failed print and return False
            if not valid:
                print('that target is not here')
                return False
        # if no target was passed assign default value of self
        elif target_str == None:
            target_obj = self
        # return target object
        return target_obj
    # EXPERIMENTAL THE EVERYTHING FUNCTION ALL THE CHECKS AND VALIDATIONS FOR ATTACKS
    async def ability_prep(self, req_level, cost, default_target = 'target', target_str = None, target_list = None):
        #check busy and level return false if fails
        if not self.busy_n_level_check(req_level):
            return False
        # create target_obj variable
        target_obj = None
        # if ability defaults to self, validate target and assign default 
        if default_target == 'self':
            target_obj = self.validate_default_self(self.location.contents, target_str, target_list)
        # if ability defaults to self.target, validate target and assign defaukt
        if default_target == 'target':
            target_obj = self.validate_default_target(self.location.contents, target_str, target_list)
        #if validate failed or never occured return
        if not target_obj:
            return False
        # check mana, set mana, wait casting time
        mana_check = await self.mana_check_n_set(cost)
        # if success return target obj
        if mana_check:
            return target_obj
    #ability countdown timer
    async def ability_countdown_timer(self, target, effect_name, seconds):
        await asyncio.sleep(seconds)
        target.remove_active(effect_name)
        print(f'the {effect_name} wears off {target.name}')
    #a combat check and set for spells
    def combat_check_n_set(self, target):
        if self.in_combat == False:
            self.enter_combat(target)
    #basic player specific commands
    def help(self):
        #print list of basic commands
        print([x for x in self.basic_action.keys()])
        #collect input about specific command
        detail = input("type a command for more details or exit to leave this menu \n")
        # exit loop if exit
        if detail == 'exit': return
        # try to print details about actions
        try:
            print(self.basic_action[detail][1])
        # if unable print so
        except KeyError:
            print(f'no help on {detail}')
        # recurse until user inputs exit
        return self.help()  

    # a travel function to move the player requires target.   
    def traverse(self, target=None):
        #check if target string was passes if not return
        if target == None:
            print('travel where?')
            return
        #validate target string that an exit exists
        valid, target = validate_target(self.location.exits_regex, target)
        #if no exit return
        if not valid:
            print('travel where?')
            return
        
        # check to see if door blocking
        door_list = [x for x in self.location.contents if type(x) == door]
        door_blocking = [x.exit for x in door_list]
        # If door print and return
        if target in door_blocking:
            print('there is a locked door in your way')
            return
        #exit combat
        self.in_combat = False
        #change location attributre
        self.location = self.location.exits[target]
        #print the travel
        print(f'you travel {target}')
        #print the new room
        self.look()
        #check for aggressive mobs, start combat if true
        for value in self.location.contents:
            if type(value) == creature or type(value).__bases__[0] == creature:
                if value.aggressive == True:
                    print(f'{value.name} attacks you')
                    self.enter_combat(value.name) 
    # a simple look around or location command
    def look(self):
        #print action and room text
        print('you look around the room')
        print(self.location.description)
        #get and print list of exits
        exits = self.location.get_exits()
        print(f'obvious exits are {exits}')
        #get list of creatures
        creature_names = [x.name for x in self.location.contents if type(x).__bases__[0] == creature or type(x) == creature]
        #if list is not empty print list
        if len(creature_names) > 0:    
            for x in creature_names:
                print(f'creature - {x}')
        #else print no creatures
        else: print('no creatures')
        #get list of items
        item_names = [x.name for x in self.location.contents if type(x).__bases__[0] == item_class]
        #if list is not empty print list
        if len(item_names) > 0:
            for x in item_names:
                print(f'item - {x}')
        #else print no itesm
        else: print('no items')        
    # an in game self status check
    def me(self):
        #print self, level, 
        print(self)
        print(f'level - {self.level}')
        #print if you can level or how much exp you need to level
        if self.experience > self.level * 100:
            print('you can level')
        else: print(f'you need {self.level * 100 - self.experience} more experience to level up')
        #print active effects
        print(f'active effects, {self.active_effects}')
        #print encumbrance
        print(f'current encumbrance, {self.load} out of {self.vitals_getter("encumbrance")}')
    # display current equipment function
    def display_equipment(self):
        print('you current area wearing')
        for k,v in self.equipment.items():
            print(f'{k} : {v}')
    # display inventory function
    def display_inventory(self):
        print('you are currently holding:')
        items_equip = []
        items_consumables = []
        items_keys = []
        for item in self.items:
            item_type = type(item)
            if item_type == equipment: items_equip.append(item)
            elif item_type == consumable: items_consumables.append(item)
            elif item_type == key: items_keys.append(item)
        print('equipment:')
        for x in items_equip:
            print(x)
        print('consumables:')
        for x in items_consumables:
            print(x)
        print('keys:')
        for x in items_keys:
            print(x)

    # an exit for the game loop
    def quit(self):
        self.active = False
        print('so long and thanks for all the fish')
    #combat target aquisition ends by calling combat loop
    def enter_combat(self, target = None):
        #if no target was passed print and return
        if target == None:
            print('attack what?')
            return
        # if a target was passed was a string validate target
        if type(target) == str:
            #validate target return bool and target object if pass 
            valid, target = validate_target(self.location.contents, target, creature_classes)
            #if validation failed print and return
            if not valid:
                print('that target is not here, validate ')
                return
        # else if target passed is not in creature class list
        elif type(target) not in creature_classes:
            return
        # if validation passes, or target in creature class list, self in combat attribute
        self.in_combat = True
        #set default target to mob
        self.target_setter(target)
        #turn mob aggressive
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
            #turn mob passive
            target.aggressive = False
            #set default target to none
            self.target_setter()
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
            #start room respawn timer
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
            # 10% chance mob does special attack if it has one
            special_chance = randint(1, 10)
            if special_chance == 5 & len(target.special_attacks) > 0:
                special_list = [x for x in target.special_attacks.keys()]
                #if target has more than one special attack select random one
                special_index = randint(0, len(special_list) - 1)
                # get special attack from list
                special_attack_str = special_list[special_index]
                #attack user with special attack
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
    # a run function ment for quick exit from combat unique since no target is needed
    def run(self, target = None):
        # if no direction passed 
        if target == None:
            # get exits list and assign random exit from list to target
            exit_list = self.location.get_exits()
            target = choice(exit_list)
        # call traverse on target
        self.traverse(target)
    # an end combat command
    def calm(self, target=None):
        #validate target if passed, assigns self.target if not. returns bool if validate failed, target object if pass
        target = self.validate_default_target(self.location.contents, target, creature_classes)
        if target:
            valid, target = validate_target(self.location.contents, target)
            if not valid:
                print('that target is not here')
                return
        elif target == None:
            target = self.target_getter()
        # if no target available print and return
        if target == None:
            print('nothing to calm')
            return
        # flip coin
        chance = randint(0, 1)
        # if fail print and return
        if chance == 0:
            print(f'{target.name} fails to calm down')
            return
        #if passed
        if chance == 1:
            #end combat, turn target passive, set default target to none
            self.in_combat = False
            target.aggressive = False
            self.target_setter()
            #print and return
            print(f'{target.name} calms down')
            return
    # special developers spell to instakill
    def dev_touch(self, target=None):
            #validate target if passed, assign target to self.target if not
            #returns bool if validate failed, target_obj if available, none if not
            target = self.validate_default_target(self.location.contents, target, creature_classes)
            # if validate failed, return
            if type(target) == bool:
                return
            # if no target print and return
            if target == None:
                print('attack what?')
                return
            # print and instakill target
            print(f'with godlike powers {self.name}, points at {target.name} and says die')
            target.vitals_setter('health', 0)
    # examine items function
    def examine(self, target = None):
        #if no target print and return
        if target == None:
            print('examine what?')
            return
        # if target was passed validate against location and inventory
        valid_1, target_1 = validate_target(self.location.contents, target)
        valid_2, target_2 = validate_target(self.items, target)
        # check if any of the validates worked
        if valid_1:
            target = target_1
        elif valid_2:
            target = target_2
        #if they all failed print and return
        else: 
            print('examine what?')
            return
        #if one was successful print and examine target
        print(f'you examine {target}')
        print(target.text)
        #if target is a container type
        if type(target) == container:
            #if locked print and return
            if target.is_locked == True:
                print('is locked')
                return
            #if not locked print it's content or 'nothing' if empty
            print('contains')
            if len(target.contents) == 0:
                print('nothing')
            else: print([x.name for x in target.contents])
    # take item function    
    def take_item(self, target = None):
        # if no target passed print and return
        if target == None:
            print('take what?')
            return
        #validate target, returns bool and target object or None
        valid, target_obj = validate_target(self.location.contents, target)
        #if target not valid print and return
        if not valid:
            print('you cannot take that')
            return
        # if target object an takeable item type
        if type(target_obj) in [consumable, equipment, key]:
            # remove item from location and connect it to player
            success = self.add_item(target_obj)
            if not success:
                print(f'you cannot take {target_obj.name},  it\' too heavy')
            self.location.remove_item(target_obj)
            target_obj.player_link(self)
            #if key or consumable type at it to consumable list
            #print message
            print(f'you take {target_obj.name}')
            #start respawn timer
            asyncio.create_task(self.location.reswpawn())
        #if target not a takeable item type
        else:
            print('you cannot take that')
    # loot container function
    def loot(self, target = None):
        # if no target passed print and return
        if target == None:
            print('loot what?')
            return
        # validate target returns bool and target_obj or None
        valid, target_obj = validate_target(self.location.contents, target)
        # if validate failed print and return
        if not valid:
            print('you cannot loot that')
            return
        #if target is anything other than container type
        if type(target_obj) != container:
            print('you can only loot container or corpses')
            return
        # if container locked print and return
        if target_obj.is_locked == True:
            print('that container in locked')
            return
        #for every item in target container link to player
        for item in [x for x in target_obj.contents]:
            # add to appropriate list
            success = self.add_item(item)
            if not success:
                print(f'you cannot take {item.name}, it\' too heavy')
            item.player_link(self)
            #print and remove item from container
            print(f'you take {item}')
            target_obj.contents.remove(item)
        #print when finished
        print(f'you looted {target_obj.name}')
    # drop item function
    def drop(self, target = None):
        if target == None:
            print('drop what?')
            return
        valid, target_obj = validate_target(self.items, target)
        if not valid:
            return
        if target_obj.name in self.equipment.values():
            print('you must remove that to drop it')
            return
        self.location.add_item(target_obj)
        self.items.remove(target_obj)
        print(f'you drop {target_obj.name}')
    # equip item function
    def equip(self, target = None):
        if target == None:
            print('equip what?')
            return
        valid, target_obj = validate_target(self.items, target, [equipment])
        if valid:
            success = self.equip_item(target_obj)
            if success:
                print(f'you equip {target_obj.name}')
            else: print(f'you are already wearing a {target_obj.equipment_type}')
    #remove item function
    def remove(self, target = None):
        if target == None:
            print('remove what?')
            return
        valid, target_obj = validate_target(self.items, target)
        if valid:
            success = self.remove_item(target_obj)
            if success:
                print(f'you remove {target_obj.name}')
            else: print(f'you are not wearing {target_obj.name}')

    # use item function THIS FUNCTION MIGHT GET MODIFIED IF I UPDATE EQUIPMENT
    def use(self, target = None):
        #if no target print and return
        if target == None:
            print('use what?')
            return
        #validate target returns bool and target object is pass
        valid, target_obj = validate_target(self.items, target, [consumable, key])
        #if valid use object
        if valid:
            target_obj.use()
        #if fail print and return
        else: print('use what?')
    # search function
    def search(self, target_str = None):
        #if no target print and return
        if target_str == None:
            print('search what?')
            return
        # validate target returns bool and target object if pass
        valid, target = validate_target(self.location.search, target_str)
        #if validate failed print and return
        if not valid:
            print('search what?')
            return
        #if target object is a string print and return
        if type(target) == str:
            print(target)
            return
        #if target object not a string, call discover object fuction on object
        else:
            self.location.discover(target)
            return