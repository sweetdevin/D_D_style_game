from class_test import creature, murlock, dragon 
from rooms import store, spawnnode
from random import randint, choice
from collections import Counter
from item_classes import item_class, consumable, container, equipment, key, door, exp_potion
import inspect
import asyncio
import re
#list of creature classes for target validation
creature_classes = [creature, murlock, dragon]
#callable object for sync methods. is used to display a custom string for my help menu
class ReporterMethod:
    def __init__(self, func, help_string):
        self.func = func
        self.help_string = help_string

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __repr__(self):
        return self.help_string
#same thing buy for async methods.
class asyncReporterMethod:
    def __init__(self, func, help_string):
        self.func = func
        self.help_string = help_string

    async def __call__(self, *args, **kwargs):
        return await self.func(*args, **kwargs)

    def __repr__(self):
        return self.help_string
#player class 
player_text =  'it\'s you, look in a mirror'
class player(creature):
    def __init__(self, name, text=player_text):
        super().__init__(name, text)
        # starting stats
        self.stats = {'str':1, 'agi':1, 'int':1}
        #default weapon
        self.default_weapon = 'fists'
        #spawn location
        self.location = spawnnode
        # basic actions like move, look, take, drop....ect ect 
        self.basic_action = {'look' : self.look, 'travel': self.traverse, 'me': self.me, 'quit': self.quit, 'examine': self.examine, 
                             'take' : self.take_item, 'use': self.use, 'loot': self.loot, 'help': self.help, 'search': self.search,
                               'equip': self.equip, 'drop': self.drop, 'remove': self.remove, 'equipment' : self.display_equipment,
                               'inventory' : self.display_inventory, 'buy': self.buy_item,'sell': self.sell_item, 'raise' : self.raise_stats,
                               'attack': self.enter_combat}
        # active status implies character is being played, tied to passive heal
        self.active = False
        # an in combat check, might be superfluous now
        self.in_combat = False
        # default combat target
        self.target = None
        #checked for players death
        self.alive = True
        #if player is casting spell. checked to keep from spamcasting
        self.occupied = False
        #basic combat actions for all players
        self.attacks = self.attacks
                                    #   , 'flee': self.flee, 'calm': self.calm}
        #players current experience
        self.experience = 0
        # players sta
        self.stats_dict = {'level': 1, 'aquired': 0, 'used':0 }
    #getters and setters for target
    def target_setter(self, target_obj = None):
        self.target = target_obj
    def target_getter(self):
        return self.target
    #recursive stat raise check called after experience gain.
    def stat_raise_checker(self):
        #if you have enough experience, subtract cost of stat raise, add stat to aquired, call again.
        if self.experience_getter() >= (self.stat_raise_aquired() + 1) * 100:
            print('you can raise your stats')
            self.sub_experience((self.stat_raise_aquired() + 1) * 100)
            self.add_stat_raise()
            self.stat_raise_checker()
    #experience getter
    def experience_getter(self):
        return self.experience
    #add experience and call stat_raise checker
    def gain_experience(self, num):
        self.experience += num
        self.stat_raise_checker() 
    #subtract experince
    def sub_experience(self, num):
        self.experience -= num 
    # add stat to aquired
    def add_stat_raise(self, num = 1):
        self.stats_dict['aquired'] += num
    #return stat raises aquired
    def stat_raise_aquired(self):
        return self.stats_dict['aquired']
    #return stat raises used
    def stat_raise_used(self):
        return self.stats_dict['used']
    #modify stat raises used
    def use_stat_raise(self, num = 1):
        self.stats_dict['used'] += num
    # a raise stats method
    def raise_stats(self, stat):
        #check if the player has any stat raises available
        if self.stat_raise_aquired() - self.stat_raise_used() <= 0:
            print('you don\'t have any stat raises to spend')
            return
        #raises str and associated vitals
        match stat:
            case 'str':
                self.stats_setter('str', self.stats_getter('str') + 1)
                self.get_n_set('health max', 25)
                self.get_n_set('health', 25)
                self.get_n_set('load max', 5)
                self.get_n_set('attack value', 3)
                self.get_n_set('poison resist', 2)
                self.use_stat_raise()
                if self.stat_raise_used() % 3 == 0:
                    self.level_setter()
                print('you feel stronger')
        #raises agi and associated vitals
            case 'agi':
                self.stats_setter('agi', self.stats_getter('agi') + 1)
                self.get_n_set('attack value', 3)
                self.get_n_set('defense value', 5)
                self.use_stat_raise()
                if self.stat_raise_used() % 3 == 0:
                    self.level_setter()
                print('you feel quicker')
            #raises int and associated vitals
            case 'int':
                self.stats_setter('int', self.stats_getter('int') + 1)
                self.get_n_set('mana max', 10)
                self.get_n_set('mana', 10)
                self.set_elemental_resists(3)
                self.use_stat_raise()
                if self.stat_raise_used() % 3 == 0:
                    self.level_setter()
                print('you feel smarter')
            #print if no valid stat was selected
            case _: 
                print(f'{stat} is not a valid stat, they "str", "agi", or "int"')
    raise_stats = ReporterMethod(raise_stats, 'if you are able raise your chosen statistic. syntax: "raise *str* or *agi* or *int*"')
    #level gettets and setters
    def level_getter(self):
        return self.stats_dict['level']
    #level setter defaults to raising the level by one since that is how it will be mostly used.
    def level_setter(self, num = 1):
        self.stats_dict['level'] += num
    # an occupied setter
    def occupied_setter(self, bool):
        self.occupied = bool
    # an occupied check
    def occupied_check(self):
        # if occupied attribute is true print and return true
        if self.occupied == True:
            print('you are busy right now')
            return True
        # if occupied  is false return false
        else: return False
    #level check function
    def level_check(self, req_level):
        # if player level is less than required level print and return False
        if self.level_getter() < req_level:
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
            self.occupied_setter(True)
            print('you begin charging an ability')
            await asyncio.sleep(3)
            return True
    #selecting gold function
    def gold_check(self, location, target_str):
        # check if user input matches a regex patter for any number follow by, or just the word, gold
        if re.match(r"\b(\d+\s)?gold\b", target_str):
            #if no number preceeding use max gold
            if target_str == 'gold':
                #return True and max gold
                return True, location.return_gold()
            # if there is a number preceeding, use number or max gold if number > max gold
            else: 
                num_str = target_str.split(' ', 1)
                num = int(num_str[0])
                if num >= location.return_gold():
                    return True, location.return_gold()
                #return true and user selected number
                else: return True, num
        # if no regex match return False and None
        else: return False, None
    #validate target function
    def validate_target(self, location, target_str, target_list = None):
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
    #a validate target wrapper with default target self.target, used for combat abilities
    def validate_default_target(self, location, target_str = None, target_list = None):
        #give target object a default value
        target_obj = None
        #if target_str was passed
        if target_str:
            valid, target_obj = self.validate_target(location, target_str, target_list)            
            # if validate failed print and return False
            if not valid:
                print('that target is not here')
                return False
        # if no target was passed assign default target
        elif target_str == None:
            target_obj = self.target_getter()
        # return target object
        return target_obj
    # a validate target wrapper with default being self, used for buffs and healing effects
    def validate_default_self(self, location, target_str=None, target_list = None):
        # give target_obj a default value
        target_obj = None
        # if target_str was passed
        if target_str:
            valid, target_obj = self.validate_target(location, target_str, target_list)
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
    async def ability_prep(self, req_level, cost, default_target = 'target', target_str = None):
        #check busy and level return false if fails
        if not self.busy_n_level_check(req_level):
            return False
        # create target_obj variable
        target_obj = None
        # if ability defaults to self, validate target and assign default 
        if default_target == 'self':
            target_obj = self.validate_default_self(self.location.contents, target_str, creature_classes)
        # if ability defaults to self.target, validate target and assign defaukt
        if default_target == 'target':
            target_obj = self.validate_default_target(self.location.contents, target_str, creature_classes)
        #if validate failed or never occured return
        if not target_obj:
            return False
        # check mana, set mana, wait casting time
        mana_check = await self.mana_check_n_set(cost)
        # if success return target obj if fails return false
        if mana_check:
            return target_obj
        else:
            return False
    # simple target location check, used in abilities after casting delay
    def target_location_check(self, target_obj):
        if target_obj == False:
            return False
        if target_obj in self.location.contents or target_obj == self:
            return True
        else: 
            print(f'{target_obj.name} is no longer here')
            return False
    #ability countdown timer, a countdown timer for buffs, removes effect as a set number of seconds
    async def ability_countdown_timer(self, target, effect_name, seconds):
        await asyncio.sleep(seconds)
        target.remove_active(effect_name)
        print(f'the {effect_name} wears off {self.assign_name(target)}')

    #a combat check and set for spells if combat starts with a spell start combat.
    def combat_check_n_set(self, target):
        if self.in_combat == False:
            self.enter_combat(self, target)
    # a help function to guide players
    def help(self, target = None):
        #if no target print lists of basic commands
        if not target:
            print('basic actions')
            print([x for x in self.basic_action.keys()])
            print('combat and class actions')
            print([x for x in self.attacks.keys()])
            print('type "help *action*" for more information on an action')
            return
        #if target print method objects with returns custome string assigned via reportermethod or asyncreportermethod
        if target in [x for x in self.basic_action.keys()]:
            print(self.basic_action[target])
        if target in [x for x in self.attacks.keys()]:
            print(self.attacks[target])
    help = ReporterMethod(help, 'displays the help menu or details about an action or attack. syntax: "help" or "help *action or attack*"')   
 
    # a travel function to move the player requires target.   
    def traverse(self, target=None):
        #check if target string was passes if not return
        if target == None:
            print('travel where?')
            return
        #validate target string that an exit exists
        valid, target = self.validate_target(self.location.exits_regex, target)
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
        self.look(self)
        #check for aggressive mobs, start combat if true
        for value in self.location.contents:
            if type(value) == creature or type(value).__bases__[0] == creature:
                if value.aggressive == True:
                    print(f'{value.name} attacks you')
                    self.enter_combat(self, value.name)
    traverse = ReporterMethod(traverse, 'try to travel in the direction of choice. syntax: "traverse *direction*"')
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
        #if creature exits format and print, using counter for format
        if len(creature_names) > 0:    
            print('creatures')
            creature_counts = Counter(creature_names)
            for npc in creature_counts:
                if creature_counts[npc] >=2:
                    print(f'{creature_counts[npc]} {npc}s')
                else: print(f'{npc}')
        #get list of items
        item_names = [x.name for x in self.location.contents if type(x).__bases__[0] == item_class]
        #if items exist format and print, using counter to format
        if len(item_names) > 0:
            print('items')
            item_counts = Counter(item_names)
            for item in item_counts:
                if item_counts[item] >= 2:
                    print(f'{item_counts[item]} {item}s')
                else: print(f'{item}')
        # if gold exisits print
        if self.location.return_gold() > 0:
            print(f'{self.location.return_gold()} gold coins')
    look = ReporterMethod(look, 'look around your current room. syntax:"look"')      
    # display active effects function for use within the 'self.me' status check
    def display_active(self):
        #create empy dicts
        display_dict = {}
        armour_dict = {}
        #loop active effects items
        for key, value in self.active_effects.items():
            #if item is a worn armour or wielded weapon
            if key in self.equipment.keys():
                #loop item effects and add them to armour dict
                for key_1, value_1 in self.active_effects[key].items():
                    if key_1 == 'damage type':
                        armour_dict[key_1] = value_1
                    else:
                        armour_dict[key_1] = armour_dict.get(key_1, 0) + value_1
            #if item is not a worn armour move value over as is to display dict
            else:
                display_dict[key] = value
        #if there are any values in armour dict add it to display dict under the 'armour' key
        if len(armour_dict) > 0:
            display_dict['equipment'] = armour_dict
        #return display dict
        return display_dict
    def me(self):
        #print self, level 
        print(self)
        print(f'level - {self.level_getter()}')
        print(f'stats: str-{self.stats_getter("str")}, agi-{self.stats_getter("agi")}, int-{self.stats_getter("int")}')
        #print if you can level or how much exp you need to level
        print(f'you have {self.stat_raise_aquired() - self.stat_raise_used()} stat raises to use')
        print(f'you need {(self.stat_raise_aquired() + 1) * 100 - self.experience_getter()} more experience to level up')
        #print active effects
        print(f'active effects, {self.display_active()}')
        #print encumbrance
        print(f'current load, {self.vitals_getter("load")} out of {self.vitals_getter("load max")}')
        #print gold
        print(f'you have {self.return_gold()} gold coins')
    me = ReporterMethod(me, 'examine your status and your belongings. syntax: "me"')
    # display current equipment function
    def display_equipment(self):
        print('you are current wearing')
        #print key and value from equipment dict. should be equipment location for the key and name/effect dict for the value
        for k,v in self.equipment.items():
            print(f'{k} : {v}')
    display_equipment = ReporterMethod(display_equipment, 'a close look at your equiped items. syntax: "equipment"')
    # display inventory function
    def display_inventory(self):
        print('you are currently holding:')
        #instead of just one massive list breaking it down to 3 lists equipment, consumables and key
        #will need to add other things into equipment if i make items that do nothing,
        #if i allows for containers to be held might need further adjustmnet
        items_equip = Counter([x.name for x in self.items if type(x) == equipment])
        items_consumables = Counter([x.name for x in self.items if type(x) == consumable])
        items_keys = Counter([x.name for x in self.items if type(x) == key])
        #print each list, the obejcts and if the count is 2 or more print the count 
        print('equipment:')
        for x in items_equip:
            if items_equip[x] >= 2:
                print(f'{items_equip[x]} {x}s')
            else: print(f'{x}')
        print('consumables:')
        for x in items_consumables:
            if items_consumables[x] >= 2:
                print(f'{items_consumables[x]} {x}s')
            else: print(f'{x}')
        print('keys:')
        for x in items_keys:
            if items_keys[x] >= 2:
                print(f'{items_keys[x]} {x}s')
            else: print(f'{x}')
    display_inventory = ReporterMethod(display_inventory, 'a close look at everything you are carrying. syntax: "inventory"')
    # an exit for the game loop
    def quit(self):
        self.active = False
        print('so long and thanks for all the fish')
    quit = ReporterMethod(quit, 'quits the game')
    #enter comabt mthod
    def enter_combat(self, target = None):
        #if no target was passed print and return
        if target == None:
            print('attack what?')
            return
        # if a target was passed was a string validate target
        if type(target) == str:
            #validate target return bool and target object if pass 
            valid, target = self.validate_target(self.location.contents, target, creature_classes)
            #if validation failed print and return
            if not valid:
                print('that target is not here')
                return
        # else if target passed is not in creature class list
        elif type(target) not in creature_classes:
            return
        # if validation passes, or target in creature class list, self in combat attribute
        self.in_combat = True
        #set default target to mob
        self.target_setter(target)
        #turn mob aggressive, this makes mob auto attack if run away to heal mid fight
        target.aggressive = True
        print(f'you attack {target.name}')
        #call combat async function on target
        self.combat(self.target_getter())
    enter_combat =ReporterMethod(enter_combat, 'attack your target with your basic melee attack. syntax: "attack *target*"')
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
            self.gain_experience(target.exp_val_getter())
            #instance a corpse from the mob
            corpse = container('a fresh corpse', f'corpse of {target.name}')
            corpse.set_regex(r'^corpse$')
            #start corpse decay timer
            asyncio.create_task(corpse.decay(self.location))
            #load corpse with mobs items
            for item in target.items:
                corpse.add_items(item)
            corpse.add_gold(target.return_gold())
            #remove mob
            self.location.remove_item(target)
            #add corpse
            self.location.add_item(corpse)
            #start room respawn timer
            asyncio.create_task(self.location.respawn())
            #heal mob
            target.vitals_setter('health', target.vitals_getter('health max'))
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
    #death event
    async def death_event(self):
        #print and wait for the the death event
        print('you fall to the ground and feel consciousness drift from your body')
        await asyncio.sleep(3)
        print('it doesn\'t fade to black though, it\'s that inbetween awake and asleep state')
        await asyncio.sleep(3)
        print('you feel pulled and pushed, like floating down a small but not gentle creek')
        await asyncio.sleep(3)
        print('what is this feeling? what is this place? you feel nothing... you have nothing')
        await asyncio.sleep(3)
        print('you drift for what could be hours, days, weeks, time looses it\'s meaning')
        await asyncio.sleep(3)
        print('somewhere between sleep and awake you stay until you feel something warm touch your face')
        await asyncio.sleep(3)
        print('wait, you feel?')
        await asyncio.sleep(1)
        print('your eyes snap open and you take a paniced breath, you are alive and back where you started')
        print('was that real? did you really die? or was it all some kind of dream?')
        print('you don\'t know. But you feel weaker and hurt.') 
        print('you are also naked and some of your money is missing.... crazy times')
        #remove all equipment
        for k,v in self.equipment.items(): 
            if v == None:
                continue
            else:
                self.equipment[k] = None
                self.remove_active(k)
        #reduce stats if applicable
        if self.stat_raise_aquired() >= 1:
            self.add_stat_raise(-1)
        if self.stat_raise_used() >= 1:
            count = 1
            while count > 0:
                index = randint(0,2)
                stats = ['str', 'agi', 'int']
                if self.stats_getter(stats[index]) >= 2:
                    self.stats_setter(stats[index], self.stats_getter(stats[index]) - 1)
                    self.use_stat_raise(-1)
                    count -= 1
        #reset vitals after stats adjustments
        self.refresh_vitals()
        #check if level needs to be changed and change level
        if self.level_getter() > (self.stat_raise_used()+3)//3:
            self.level_setter(-1)
        #reduce experience
        self.sub_experience(self.experience_getter()//2)
        #take money
        self.sub_gold(int(self.return_gold()//1.50))
        #change location to spawnnode
        self.location = spawnnode
        #inventory or equipment dropping?
        #reset alive status
        self.alive = True
        self.get_n_set('health', self.vitals_getter('health max') // 4)
    #melee attack loop
    async def basic_attack_loop(self, target):
        #while player in is combat
        while self.in_combat == True:
            #make sure target is still alive
            if self.victory_check(target):
                return
            #perform a melee attack on target
            damage = self.basic_attack(target)
            if damage <= 0:
                print(f'you missed {self.assign_name(target)} with your {self.assign_weapon()}')
            else:
                print(f'you hit {self.assign_name(target)} for with your {self.assign_weapon()} for {damage} {self.vitals_getter("damage type")} damage')
            #see if target survived, if target died end loop
            if self.victory_check(target):
                return
            #target melee attacks me
            target_dmg = target.basic_attack(self)
            if target_dmg <= 0:
                print(f'{self.assign_name(target)} missed you with it\'s {target.assign_weapon()}')
            else:
                print(f'{self.assign_name(target)} hit you with it\'s {target.assign_weapon()} for {target_dmg} {target.vitals_getter("damage type")} damage')
            #see if I died
            if self.death_check(target):
                #if so trigger death event
                await self.death_event()
                return
            #check if I have counter attack status
            if self.vitals_getter('counter attack') == 'active':
                #if so 'lite' attack targeter
                amount = self.basic_attack(target, 'lite')
                print(f'you counter attack for {amount} {self.vitals_getter("damage type")} damage')
                #check if target died
                if self.victory_check(target):
                    return
            #random number 0 to 9 for special attack. 
            #currently set up so the number of special attacks corrolate to the percent chance of executing a special attack
            special_chance = randint(0, 9)
            special_list = [x for x in target.special_attacks.keys()]
            try: 
                special_attack =special_list[special_chance]
            except IndexError:
                special_attack = None
                #attack user with special attack
            if special_attack:    
                target.special_attacks[special_attack](self)
            #if i died end loop
            if self.death_check(target):
                await self.death_event()
                return
            #wait 5 seconds before repeating
            self.mana_display()
            self.health_display()
            target.health_display()
            await asyncio.sleep(5)
    # a function to assign combat loop as a task to run in the background
    def combat(self, target):
        asyncio.create_task(self.basic_attack_loop(target))
    #some functions i've commented out. they were unnecessary and not working with my callable object help menu. 
    # commented out as to not bug anything might reinstate if I can get them working again
    '''# a run function ment for quick exit from combat unique since no target is needed
    async def flee(self, target = None):
        # if no direction passed
        print('you panic and run')
        asyncio.sleep(1)
        if target == None:
            # get exits list and assign random exit from list to target
            exit_list = self.location.get_exits()
            target = choice(exit_list)
        # call traverse on target
        self.traverse(target)
    flee =asyncReporterMethod(flee, 'flee from combat in any available direction. syntax: "run"')'''
    # an end combat command
    '''async def calm(self, target=None):
        #validate target if passed, assigns self.target if not. returns bool if validate failed, target object if pass
        target = self.validate_default_target(self.location.contents, target, creature_classes)
        if target:
            valid, target = self.validate_target(self.location.contents, target)
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
        print(f'you try and calm {target.name}')
        asyncio.sleep(2)
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
    calm = asyncReporterMethod(calm, 'try to calm your current target to end combat. syntax: "calm" or "calm *tagert*"')'''
    '''# special developers spell to instakill
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
            target.vitals_setter('health', 0)'''
    # examine items function
    def examine(self, target = None):
        #if no target print and return
        if target == None:
            print('examine what?')
            return
        # if target was passed validate against location and inventory
        valid_1, target_1 = self.validate_target(self.location.contents, target)
        valid_2, target_2 = self.validate_target(self.items, target)
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
            #if not locked print it's contents or 'nothing' if empty
            print('contains')
            #logic checks
            check_1 = False
            check_2 = False
            #if target has items 
            if len(target.contents) > 0:
                #get item counts
                item_counts = Counter([x.name for x in target.contents])
                #print item counts if more than 1 and items
                for item in item_counts:
                    if item_counts[item] >= 2:
                        print(f'{item_counts[item]} {item}s')
                    else: print(f'{item}')
                #set check to True
                check_1 =True
            #if got in container print amount
            if target.return_gold() > 0:
                print(f'{target.return_gold()} gold coins')
                #set check to True
                check_2 = True
            #if both checks still false print "nothing"
            if check_1 == False and check_2 == False:
                print('nothing')
    examine = ReporterMethod(examine, 'look at an item or creature in the room or your inventory. syntax: "examine *target*"')
    # take item function    
    def take_item(self, target = None):
        # if no target passed print and return
        if target == None:
            print('take what?')
            return
        #check if gold was the target
        check, value = self.gold_check(self.location, target)
        # if target was gold add amount to self gold, print, remove from location and return
        if check == True:
                self.add_gold(value)
                print(f'you took {value} gold coins')
                self.location.sub_gold(value)
                return
        #validate target, returns bool and target object or None
        valid, target_obj = self.validate_target(self.location.contents, target)
        #if target not valid print and return
        if not valid:
            print('you cannot take that')
            return
        # if target object an takeable item type
        if type(target_obj) in [consumable, equipment, key, exp_potion]:
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
            asyncio.create_task(self.location.respawn())
        #if target not a takeable item type
        else:
            print('you cannot take that')
    take_item = ReporterMethod(take_item, 'take an item from the room. syntax: "take *item*"')
    # loot container function
    def loot(self, target = None):
        # if no target passed print and return
        if target == None:
            print('loot what?')
            return
        # validate target returns bool and target_obj or None
        valid, target_obj = self.validate_target(self.location.contents, target)
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
        #for every item in target container add to player items.
        for item in [x for x in target_obj.contents]:
            success = self.add_item(item)
            #if take item fails, print
            if not success:
                print(f'you cannot take {item.name}, it\' too heavy')
                continue
            #link item to player
            item.player_link(self)
            #print and remove item from container
            print(f'you take {item}')
            target_obj.contents.remove(item)
        # if target has gold, add to player gold, print, remove gold from container
        if target_obj.return_gold() > 0:
            self.add_gold(target_obj.return_gold())
            print(f'you loot {target_obj.return_gold()} gold from {target_obj.name}')
            target_obj.sub_gold(target_obj.return_gold()) 
        #print when finished
        print(f'you looted {target_obj.name}')
    loot =ReporterMethod(loot, 'take everything from a corpse or container. syntax: "loot *container*"')
    # drop item function
    def drop(self, target = None):
        #if no target print and return
        if target == None:
            print('drop what?')
            return
        # check if target was gold
        check, value = self.gold_check(self, target)
        # if so add amount to room, print, remove gold from self and return.
        if check == True:
                self.location.add_gold(value)
                print(f'you drop {value} gold coins')
                self.sub_gold(value)
                return
        # if target wasn't gold validate target for items
        valid, target_obj = self.validate_target(self.items, target)
        # if failed print and return
        if not valid:
            print('you don\'t have that item to drop')
            return
        # if target is currently worn, print and return.
        if target_obj.name in self.equipment.values():
            print('you must remove that to drop it')
            return
        # if target not worn add item to location, remove target from items. 
        self.location.add_item(target_obj)
        self.items.remove(target_obj)
        # reduce load by weight. 
        self.get_n_set('load', target_obj.weight_getter(), True)
        print(f'you drop {target_obj.name}')
    drop = ReporterMethod(drop, 'drops an item from your inventory. syntax: "drop *item*"')
    # equip item function
    def equip(self, target = None):
        #if target is none print and return
        if target == None:
            print('equip what?')
            return
        # validate target is in inventory and is an equipment
        valid, target_obj = self.validate_target(self.items, target, [equipment])
        if valid:
            # if valid try to equip
            success = self.equip_item(target_obj)
            if success:
                #if success print
                print(f'you equip {target_obj.name}')
            #if fail print
            else: print(f'you are already wearing a {target_obj.equipment_type}')
    equip= ReporterMethod(equip, 'equips an item from your inventory. syntax: "equip *item*"')
    #remove item function
    def remove(self, target = None):
        #if target is none print and return
        if target == None:
            print('remove what?')
            return
        # validate target for items.
        valid, target_obj = self.validate_target(self.items, target)
        #if valud try to remove
        if valid:
            success = self.remove_item(target_obj)
            #if remove item worked print
            if success:
                print(f'you remove {target_obj.name}')
            #if remove failed print
            else: print(f'you are not wearing {target_obj.name}')
    remove = ReporterMethod(remove, 'remove a worn piece of equipment. syntax: "remove *item*"')
    # use item 
    def use(self, target = None):
        #if no target print and return
        if target == None:
            print('use what?')
            return
        #validate target is in inventory and is a key or consumable
        valid, target_obj = self.validate_target(self.items, target, [consumable, key, exp_potion])
        #if valid use object
        if valid:
            target_obj.use()
        #if fail print and return
        else: print('use what?')
    use = ReporterMethod(use, 'use a potion or item from your inventory. syntax: use *item*')
    # a sell item method
    def sell_item(self, item_str = None):
        shop = None
        # check is location is a shop, if so assin to shop variable, else print and return
        if type(self.location) == store:
            shop = self.location
        else:
            print('you are not at a store')
            return
        # if item_str is none print and return
        if item_str == None:
            print('sell what?')
            return
        #validate target is in inventory
        valid, target_obj = self.validate_target(self.items, item_str)
        # if fail print and return
        if not valid:
            print('you don\'t have that item to sell')
            return
        # if valid add item value to player gold, remove item from player items
        else:
            self.add_gold(target_obj.return_price())
            self.items.remove(target_obj)
            # reduce load by target weight, add item to shop stock, print
            self.get_n_set('load', target_obj.weight_getter(), True)
            shop.add_stock(target_obj)
            print(f'you sold {target_obj} for {target_obj.return_price()}')
    sell_item = ReporterMethod(sell_item, 'if in a store sell an item to the store. syntax: "sell *item*"')
    # a buy item method
    def buy_item(self, item_str = None):
        shop = None
        # if self.location is a store set it to shop, if not print and return
        if type(self.location) == store:
            shop = self.location
        else:
            print('you are not at a store')
            return
        # if item string is none print and return
        if item_str == None:
            print('buy what?')
            return
        #validate target is in shop stock
        valid, target_obj = self.validate_target(shop.stock, item_str)
        # if not pr9nt and return
        if not valid:
            print('that item is not for sale')
            return
        #if valid check player has enough gold, if not print and return
        elif self.gold < target_obj.return_store_price():
            print('you cannot afford that item')
            return
        # if player has enough gold, subtrack gold, remove item from shop stock 
        else:
            self.sub_gold(target_obj.return_store_price())
            shop.remove_stock(target_obj)
            #try to add item and print
            success = self.add_item(target_obj)
            print(f'you buy {target_obj}')
            #if add item failed add item to the room and printS
            if not success:
                print('that item is too heavy so you drop it')
                shop.add_item(target_obj)
    buy_item = ReporterMethod(buy_item, 'if in a store purchase an item. syntax: "buy *item*"')
    # search function
    def search(self, target_str = None):
        #if no target print and return
        if target_str == None:
            print('search what?')
            return
        # validate target returns bool and target object if pass
        valid, target = self.validate_target(self.location.search, target_str)
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
    search = ReporterMethod(search, 'search parts of the room to find hidden items or pathways. syntax: "search *target*"')
    #basic damage spell
    async def nuke(self, level, cost, damage, damage_type, flavor_template, target, flavor_ownership = False):
        #ability prep validates target, assigns default target if necessary, subtracts mana, and waits casting delay
        # returns False or target_obj
        target_obj = await self.ability_prep(level, cost, 'target', target)
        # checks if target_obj is False or if target object is no longer present
        if self.target_location_check(target_obj):
            #format and pring flavor text
            formatted_string = flavor_template.substitute(name = self.assign_name(target_obj, flavor_ownership), weapon = self.assign_weapon())
            print(formatted_string)
            #calculate damage and print
            final_dmg = self.calc_dmg(target_obj, damage, damage_type)
            print(f'you deal {final_dmg} of {damage_type} damage to {self.assign_name(target_obj)}')
            # deal damage to target
            target_obj.get_n_set('health', final_dmg, True)
            # check combat and set if necessary
            self.combat_check_n_set(target_obj)
        #set occupied to False
        self.occupied_setter(False)
    #basic buff spell
    async def buff(self, level, cost, effect_dict, effect_name, flavor_template, duration, target, flavor_ownership = False):
        #ability prep validates target, assigns default target if necessary, subtracts mana, and waits casting delay
        # returns False or target_obj
        target_obj = await self.ability_prep(level, cost, 'self', target)
        # checks if target_obj is False or if target object is no longer present
        if self.target_location_check(target_obj):
            #format and pring flavor text
            formatted_string = flavor_template.substitute(name = self.assign_name(target_obj, flavor_ownership), weapon = self.assign_weapon())
            print(formatted_string)
            # set spell effects
            target_obj.set_active(effect_name, effect_dict)
            #countdown and remove effect task
            asyncio.create_task(self.ability_countdown_timer(target_obj, effect_name, duration))
        #set occupied to False
        self.occupied = False
    #debuffs must be passed a negative number otherwise they will buff
    async def debuff(self, level, cost, effect_dict, effect_name, flavor_template, duration, target, flavor_ownership = False):
        #ability prep validates target, assigns default target if necessary, subtracts mana, and waits casting delay
        # returns False or target_obj
        target_obj = await self.ability_prep(level, cost, 'target', target)
        # checks if target_obj is False or if target object is no longer present
        if self.target_location_check(target_obj):
            #format and pring flavor text
            formatted_string = flavor_template.substitute(name = self.assign_name(target_obj, flavor_ownership), weapon = self.assign_weapon())
            print(formatted_string)
            # set spell effects
            target_obj.set_active(effect_name, effect_dict)
            #countdown and remove effect task
            asyncio.create_task(self.ability_countdown_timer(target_obj, effect_name, duration))
        # set occupied to False
        self.occupied = False
    async def multi_nuke(self, level, cost, damage_range, damage_type, rounds, interval, flavor_template, target, flavor_ownership = False):
        #ability prep validates target, assigns default target if necessary, subtracts mana, and waits casting delay
        # returns False or target_obj
        target_obj = await self.ability_prep(level, cost, 'target', target)
        #loop for rumber of rounds
        for num in range(rounds):
            # checks if target_obj is False or if target object is no longer present
            if self.target_location_check(target_obj):
                #format and pring flavor text
                formatted_string = flavor_template.substitute(name = self.assign_name(target_obj, flavor_ownership), weapon = self.assign_weapon())
                print(formatted_string)
                #calculate damage and print
                damage = randint(damage_range[0], damage_range[1])
                final_dmg = self.calc_dmg(target_obj, damage, damage_type)
                print(f'you deal {final_dmg} of {damage_type} damage to {self.assign_name(target_obj)}')
                # deal damage to target
                target_obj.get_n_set('health', final_dmg, True)
                #check combat and set if necessary
                self.combat_check_n_set(target_obj)
                #wait interval
                await asyncio.sleep(interval)
        #set occupied to False
        self.occupied_setter(False)
    async def pierce_defense(self, level, cost, damage, damage_type, pierce_float, flavor_template, target, flavor_ownership = False):
        #ability prep validates target, assigns default target if necessary, subtracts mana, and waits casting delay
        # returns False or target_obj
        target_obj = await self.ability_prep(level, cost, 'target', target)
        # checks if target_obj is False or if target object is no longer present
        if self.target_location_check(target_obj):
            #flavor text format and print
            formatted_string = flavor_template.substitute(name = self.assign_name(target_obj, flavor_ownership), weapon = self.assign_weapon())
            print(formatted_string)
            #calculate damage, 
            final_dmg = self.calc_dmg(target_obj, damage, damage_type)
            damage_diff = damage - final_dmg
            #pierce works by taking the difference between final damage and passed damage, multiplying it by percent expressed as a float.
            #the absolute value of that is then added to the final damage. this way it works even if the target has negative resistance,  
            pierce_bonus = abs(damage_diff * pierce_float)
            new_total = final_dmg + round(pierce_bonus)
            print(f'you deal {new_total} of {damage_type} damage to {self.assign_name(target_obj)}')
            # deal damage to target
            target_obj.get_n_set('health', final_dmg, True)
            #check and set combat status if necessary
            self.combat_check_n_set(target_obj)
        #set occuiped to false
        self.occupied_setter(False)
    async def heal(self, level, cost, amount, type, flavor_template, target, flavor_ownership = False):
        #ability prep validates target, assigns default target if necessary, subtracts mana, and waits casting delay
        # returns False or target_obj
        target_obj = await self.ability_prep(level, cost, 'self', target)
        # checks if target_obj is False or if target object is no longer present
        if self.target_location_check(target_obj):
            #format and print string
            formatted_string = flavor_template.substitute(name = self.assign_name(target_obj, flavor_ownership), weapon = self.assign_weapon())
            print(formatted_string)
            print(f'{self.assign_name(target_obj)} recover {amount} points of {type}')
            # heal vital by amount
            # I left it open ended instead of hard coding health even though the concept of a mana costing spell to recover mana is asinine
            target_obj.get_n_set(type, amount)
        #set occupied to false
        self.occupied_setter(False)
    async def nuke_n_debuff(self, level, cost, damage, damage_type, effect_name, effect_dict, duration, flavor_template, target, flavor_ownership = False):
        #ability prep validates target, assigns default target if necessary, subtracts mana, and waits casting delay
        # returns False or target_obj
        target_obj = await self.ability_prep(level, cost, 'target', target)
        # checks if target_obj is False or if target object is no longer present 
        if self.target_location_check(target_obj):
            #format and print flavor text
            formatted_string = flavor_template.substitute(name = self.assign_name(target_obj, flavor_ownership), weapon = self.assign_weapon())
            print(formatted_string)
            #calculate damage and print
            final_dmg = self.calc_dmg(target_obj, damage, damage_type)
            print(f'you deal {final_dmg} of {damage_type} damage to {self.assign_name(target_obj)}')
            # deal damage to target
            target_obj.get_n_set('health', final_dmg, True)
            # set spell effects
            target_obj.set_active(effect_name, effect_dict)
            #countdown and remove effect task
            asyncio.create_task(self.ability_countdown_timer(target_obj, effect_name, duration))
            #check and set combat if necessary
            self.combat_check_n_set(target_obj)
        #set occupied to false
        self.occupied = False