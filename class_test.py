from random import randint
from item_classes import consumable, equipment, wooden_sword
# creature class, this is the super class for all living things.
class creature:
    def __init__(self, name, text, vitals={}, exp_val = 1, regex = None, gold = 0):
        # name and description
        self.name = name
        self.text = text
        # game stats which convert to vitals. via refresh vitals 
        self.stats = {'str':1, 'agi':1, 'int':1}
        self.vitals = vitals
        #attacks dict, special attacks added to it in subclasses
        self.attacks = {'basic attack': self.basic_attack}
        self.special_attacks = {}
        #auto attacking attribute
        self.aggressive = False
        #items list, functions as an inventory
        self.items = []
        # equipment dict. 
        self.equipment = {'head': None, 'neck': None, 'shoulders': None, 'chest': None,
                          'back': None, 'arms': None, 'hands': None, 'finger': None, 
                          'waist': None, 'legs': None, 'feet': None, 'weapon': None}
        # active effects, anything that raises or lowers a vital goes there.
        self.active_effects = {}
        #the experience value for killing the mob
        self.exp_val = exp_val
        # the regex patter to select this character
        self.regex = regex
        # gold since gold is weightless and just an integer it made more sense as an attibute than an object
        self.gold = gold
    # reporter function returns name and basic info. 
    # WAS MADE THAT WAY TO HELP DEBUG CREATURES AND VITALS SWITCHING TO JUST SELF.NAME 
    # MIGHT MAKE THINGS A LITTLE BIT EASIER LIKE HOW I AM WITH ITEMS.
    def __repr__(self):
        return f'''{self.name} 
        health = {self.vitals_getter('health')} of {self.vitals_getter('health max')} 
        mana = {self.vitals_getter('mana')} of {self.vitals_getter('mana max')}
        attack = {self.vitals_getter('attack value')}
        defense = {self.vitals_getter('defense value')}'''
    #custom copy functions to seperate the vitals. 
    # I FEEL LIKE THIS IS A MESS, I FEEL LIKE EQUIPMENT, AND ACTIVE EFFECTS, AND ITEMS
    # WILL NEED TO BE ADDED TO COPY, I NEED TO TEST AND UPDATE THIS. NOT USING A DEEP COPY
    # TO SAVE MEMORY, UNNECESSARY BUT FOR LEARING PURPOSES.
    def __copy__(self):
        new_instance = type(self)(self.name, self.text, self.vitals.copy(), self.exp_val, self.regex, self.gold)
        # copies items
        for item in self.items:
            new_instance.add_item(item)
        # copies equipment
        for key, value in self.equipment.items():
            if value != None:
                new_instance.equipment[key] =value
                # call set active with item_type and effect dict
                new_instance.set_active(key, value[1])
        return new_instance
    # set regex function
    def set_regex(self, regex_pattern):
        self.regex = regex_pattern
    #sets vitals based off of stats
    def refresh_vitals(self):
        self.vitals = {'health max': 25 + (self.stats['str'] * 25), 'health': 25 + (self.stats['str'] * 25),
                       "mana max": self.stats['int'] * 10, 'mana': self.stats['int']*10,
                       'attack value': 1+(self.stats['str'] * 3) + (self.stats['agi'] * 3),
                       'defense value':1+self.stats['agi'] * 5, 'load max' : 50 + (self.stats['str'] * 5),
                       'load': 0, 'fire resist': self.stats['int'] * 5, 'water resist': self.stats['int'] * 5,
                       'shock resist': self.stats['int'] * 5, 'chaos resist' : 0, 'damage type': 'normal'}
    #new set active effects function, takes an effect name (string) and effect dict formatted
    # as {vital to change : amount to change}
    def set_active(self, effect_name, effects_dict):
        #for every item in effects dict,  call get_n_set with item
        for key, value in effects_dict.items():
            if key == 'damage type':
                self.vitals_setter(key, value)
            else:
                self.get_n_set(key, value)
        # store effect name and effect dicts in active effects
        self.active_effects[effect_name] = effects_dict
    # new remove active effects funct, just takes the name of the effect to remove.
    def remove_active(self, effect_name):
        # for item in effect dict call get_n_set in subtract mode.
        for key, value in self.active_effects[effect_name].items():
            self.get_n_set(key, value, True)
            #remove effect name from active effects dict
            self.active_effects.pop(effect_name)
    #basic attack function
    def basic_attack(self, target):
        # calc damange based on roll, attack val, target defense val
        base_damage = self.vitals_getter('attack value') + randint(0, 10)
        damage_type = self.vitals_getter('damage type')
        final_damage =self.calc_dmg(target, base_damage, damage_type)
        # if damage at or below zero report as missed target
        if final_damage <= 0:
            print(f'{self.name} missed {target.name}')
            return
        # else deal damage too target, and print
        target.get_n_set('health', final_damage, True)
        weapon = self.equipment['weapon']
        if weapon == None:
            weapon = 'body'
        else: weapon = weapon[0]
        print(f'{self.name} hit {target.name} with it\'s {weapon} for {final_damage} {damage_type} damage')
    # calculate damge function
    def calc_dmg(self, target, base_dmg, dmg_type):
        new_dmg = 0
        #if damage is normal type use defense value
        dmg_resist = self.match_resist(dmg_type)
        if dmg_resist == 'normal':
            percent = 0
            if target.vitals_getter('defense value') <= 100:
                percent = (target.vitals_getter('defense value')/2)/100
            else:
                new_def = target.vitals_getter('defense value') - 100
                percent = .50 + (new_def/4)/100
            if percent > .75:
                percent = .75
            new_dmg = round(base_dmg * (1 - percent))
        # if damage is not normal use resistance value
        else:
            target_resist = target.vitals_getter(dmg_resist)
            if target_resist >= 50:
                print(f'{target.name} has high {dmg_resist}')
            if target_resist <= 0:
                print(f'{target.name} is weak against {str.split(dmg_resist)[0]}')
            new_dmg = round(base_dmg * (1 - (target.vitals_getter(dmg_resist) / 100)))
        #return new damage
        return new_dmg
    # add item function, returns true or false if succ
    def match_resist(self, damage_type):
        match damage_type:
            case 'fire':
                return 'fire resist'
            case 'water':
                return 'water resist'
            case 'shock':
                return 'shock resist'
            case 'chaos':
                return 'chaos resist'
            case _:
                return 'normal'
    def add_item(self, item):
        # if weight will over-encumber, return false
        if self.vitals_getter('load') + item.weight_getter() > self.vitals_getter('load max'):
            return False
        # else add item to inventory, add weight to load, return true
        self.items.append(item)
        self.get_n_set('load', item.weight_getter())
        return True
    # equip item function, takes equipment object, returns true or false if successful
    def equip_item(self, item):
        # assigned item type to the equipment type attribute. don't know why I did it like that
        item_type = item.equipment_type
        # if there is something assigned to that item_type in self.equipment return false
        if self.equipment[item_type] != None:
            return False
        # else add item name and item effect dict to self.equipment under the item type key
        else:
            self.equipment[item_type] = [item.name, item.effect_dict]
            # call set active with item_type and effect dict and return True
            self.set_active(item_type, item.effect_dict)
            return True
    #remove item function, takes an equipment object. This seems bad and need to be reworked
    def remove_item(self, item):
        # This seems overly complex for no reason.
        for k,v in self.equipment.items(): 
            if v == None:
                continue
            if v[0] == item.name:
                self.equipment[k] = None
                self.remove_active(item.equipment_type)
                return True
        return False
    # vitals getter
    def vitals_getter(self, stats_string):
        return self.vitals[stats_string]
    # vitals setter   
    def vitals_setter(self, stats_string, value):
        self.vitals[stats_string] = value
    #stats getter    
    def stats_getter(self, stat_string):
        return self.stats[stat_string]
    # a stats setter
    def stats_setter(self, stat_string, value):
        self.stats[stat_string] = value
    # a display mana function
    def mana_display(self):
        # calc percent of mana
        mana_percent = (self.vitals_getter('mana') / self.vitals_getter('mana max')) * 100
        mana_str = ''
        # build string of % based on half mana percent
        for x in range(round(mana_percent/2)):
            mana_str = mana_str + '%'
        # print mana percent string
        print(f'{self.name} mana - {mana_str}')
    # a display health function
    def health_display(self):
        # calc health percent
        health_percent = (self.vitals_getter('health') / self.vitals_getter('health max')) * 100
        health_str = ''
        # build string of % based on half health percent
        for x in range(round(health_percent/2)):
            health_str = health_str + '%'
        # print health percent string
        print(f'{self.name} health - {str(health_str)}')
    # a function to display both health and mana
    def status_display(self):
        self.mana_display()
        self.health_display()
    def exp_val_getter(self):
        return self.exp_val
    # an experience value modifier function
    def exp_val_setter(self, value):
        self.exp_val = value
    # a get and set function to streamline modifying values
    def get_n_set(self, stats_string, value, subtract = False):
        # if subtrack make value negative
        if subtract == True: value = 0 - value
        # calc ne value by adding value to current value
        new_val = self.vitals_getter(stats_string) + value
        # IS THERE A WAY TO COMBINE THESE TOGETHER?
        # if above max health reduce to max
        if stats_string == 'health' and new_val > self.vitals_getter('health max'):
            new_val = self.vitals_getter('health max')
        # if above max mana update to max
        if stats_string == 'mana' and new_val > self.vitals_getter('mana max'):
            new_val = self.vitals_getter('mana max')
        # set current value to new value
        self.vitals_setter(stats_string, new_val)
    # add gold funct
    def add_gold(self, num):
        self.gold += num
    #subtract gold funct
    def sub_gold(self, num):
        self.gold -= num
    # return gold funct
    def return_gold(self):
        return self.gold
#murlock subclass
murlock_text = "A scaley frog-like humanoid walking upright with thin limbs and an enormous mouth."
class murlock(creature):
    def __init__(self, name, text) -> None:
        super().__init__(name, text)
        self.special_attacks = {'bubble attack': self.bubble_atk}
    #murlocks special attack
    def bubble_atk(self, target):
            damage = randint(0, 20) + 20
            final_dmg = self.calc_dmg(target, damage, 'water resist')
            target.get_n_set('health', final_dmg, True)
            print(f'{self.name} launches bubbles at {target.name} for {final_dmg} water damage')
# creating creature class objects and item class objects
#setting values for creature objects and adding item objects to creatures
rat= creature('rat', 'a large disgusting rat')
rat.set_regex(r'^ra?t?$')
rat.refresh_vitals()
rat.add_gold(10)
rat.vitals_setter('shock resist', 50)
rat.vitals_setter('water resist', 0)
dreadclaw = murlock('dreadclaw murlock', murlock_text + "\n these murlocks have large claws.")
dreadclaw.refresh_vitals()
dreadclaw.exp_val_setter(3)
dreadclaw.set_regex(r'\b(dread\w*|murlock\w*)\b')
ring_of_health = equipment('ring of health', 'a glowing red ring','finger', {'health max':300})
ring_of_health.set_regex(r'^ring( of health| health)?$')
ring_of_health.change_price(50)
health_potion = consumable('health potion', 'a vial of a red bubbly liquid', {'health':50})
health_potion.set_regex(r'^(health|potion|health potion)$')
dreadclaw.add_item(health_potion)
snagletooth = murlock('snagletooth murlock', murlock_text + "\n These murlocks have long snarly teeth.")
snagletooth.refresh_vitals()
snagletooth.vitals_setter('shock resist', -25)
snagletooth.vitals_setter('water resist', 50)
snagletooth.exp_val_setter(3)
snagletooth.set_regex(r'\b(snagle\w*|murlock\w*)\b')
snagletooth.add_item(health_potion)
snagletooth.add_item(ring_of_health)
snagletooth.equip_item(ring_of_health)
dreadclaw.exp_val_setter(100)
mana_potion = consumable('mana potion', 'a vial of bubbly blue liquid', {'mana':20})
mana_potion.set_regex(r'^(mana|potion|mana potion)$')
mana_amulet = equipment('mana charm', 'a plusing carved crystal rune', 'neck', {'mana max':30})
mana_amulet.set_regex(r'^(mana|charm|mana charm)$')
mana_amulet.change_price(50)
dreadclaw.add_item(mana_potion)
dreadclaw.add_item(mana_potion)
snagletooth.add_gold(50)
dreadclaw.add_gold(50)
farm_boy =creature('a young boy', 'a small farmboy, wearing plain clothes, playing with a wooded sword')
farm_boy.refresh_vitals()
farm_boy.exp_val_setter(2)
farm_boy.set_regex(r'^(small )?boy$')
farm_boy.add_item(wooden_sword)
farm_boy.equip_item(wooden_sword)