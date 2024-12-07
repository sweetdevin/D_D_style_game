from random import randint
from item_classes import consumable, equipment
# initial living creature class all player and 
# npc will have this super class as of right now
class creature:
    def __init__(self, name, text, vitals={}, exp_val = 10, regex = None):
        self.name = name
        self.text = text
        self.stats = {'str':1, 'agi':1, 'int':1}
        self.vitals = vitals
        self.weapon = 'body'
        self.attacks = {'basic attack': self.basic_attack}
        self.special_attacks = {}
        self.aggressive = False
        self.items = []
        self.equipment = {'head': None, 'neck': None, 'shoulders': None, 'chest': None,
                          'back': None, 'arms': None, 'hands': None, 'finger': None, 
                          'waist': None, 'legs': None, 'feet': None}
        self.active_effects = {}
        self.exp_val = exp_val
        self.regex = regex
        self.load = 0
    # reporter function 
    def __repr__(self):
        return f'''{self.name} 
        health = {self.vitals_getter('health')} of {self.vitals_getter('health max')} 
        mana = {self.vitals_getter('mana')} of {self.vitals_getter('mana max')}
        attack = {self.vitals_getter('attack value')}
        defence = {self.vitals_getter('defence value')}'''
    #custom copy functions to seperate the vitals, exp value, and regex pattern
    def __copy__(self):
        new_instance = type(self)(self.name, self.text, self.vitals.copy(), self.exp_val, self.regex)
        new_instance.refresh_vitals()
        return new_instance
    # set regex function
    def set_regex(self, regex_pattern):
        self.regex = regex_pattern
    #sets vitals based off of stats
    def refresh_vitals(self):
        self.vitals = {'health max': 25 + (self.stats['str'] * 25), 'health': 25 + (self.stats['str'] * 25),
                       "mana max": self.stats['int'] * 10, 'mana': self.stats['int']*10,
                       'attack value': 1+(self.stats['str'] * 3) + (self.stats['agi'] * 3),
                       'defence value':1+self.stats['agi'] * 3, 'encumbrance' : 50 + (self.stats['str'] * 5)}
    #new set active effects function
    def set_active(self, effect_name, effects_dict):
        for key, value in effects_dict.items():
            self.get_n_set(key, value)
        self.active_effects[effect_name] = effects_dict
    # set active effects
    '''def set_active(self, effect_name, stats_string, effect):
        self.active_effects[effect_name] = [stats_string, effect]
        self.get_n_set(stats_string, effect)'''
    # new remove active effects funct
    def remove_active(self, effect_name):
        for key, value in self.active_effects[effect_name].items():
            self.get_n_set(key, value, True)
            self.active_effects.pop(effect_name)
    # remove active effects
    '''def remove_active(self, effect_name):
        self.get_n_set(self.active_effects[effect_name][0], self.active_effects[effect_name][1], True)
        del self.active_effects[effect_name]'''
    #basic attack function
    def basic_attack(self, target):
        # calc damange based on roll, attack val, target defence val
        damage = (self.vitals_getter('attack value') + randint(0, 10)) - target.vitals_getter('defence value')
        # if damage at or below zero report as missed target
        if damage <= 0:
            print(f'{self.name} missed {target.name}')
            return
        target.get_n_set('health', damage, True)
        print(f'{self.name} hit {target.name} with {self.weapon} for {damage} damage')
    # add_tiem function
    def add_item(self, item):
        if self.load + item.weight > self.vitals_getter('encumbrance'):
            return False
        self.items.append(item)
        self.load += item.weight
        return True
    # equip item function
    def equip_item(self, item):
        item_type = item.equipment_type
        if self.equipment[item_type] != None:
            return False
        else:
            self.equipment[item_type] = [item.name, item.effect_dict]
            self.set_active(item_type, item.effect_dict)
            return True
    #remove item function
    def remove_item(self, item):
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
#murlock subclass
murlock_text = "A scaley frog-like humanoid walking upright with thin limbs and an enormous mouth."
class murlock(creature):
    def __init__(self, name, text) -> None:
        super().__init__(name, text)
        self.weapon = 'claws'
        self.special_attacks = {'bubble attack': self.bubble_atk}
    #murlocks special attack
    def bubble_atk(self, target):
            damage = randint(0, 20) + 20
            target.get_n_set('health', damage, True)
            print(f'{self.name} launches bubbles at {target.name} for {damage} damage')
# creating creature class objects and item class objects
#setting values for creature objects and adding item objects to creatures
rat= creature('rat', 'a large disgusting rat')
rat.set_regex(r'^ra?t?$')
rat.refresh_vitals()
rat.exp_val_setter(30)
dreadclaw = murlock('dreadclaw murlock', murlock_text + "\n these murlocks have large claws.")
dreadclaw.refresh_vitals()
dreadclaw.set_regex(r'\b(dread\w*|murlock\w*)\b')
ring_of_health = equipment('ring of health', 'a glowing red ring','finger', {'health max':300})
ring_of_health.set_regex(r'^ring( of health| health)?$')
health_potion = consumable('health potion', 'a vial of a red bubbly liquid', {'health':50})
health_potion.set_regex(r'^(health|potion|health potion)$')
dreadclaw.add_item(health_potion)
snagletooth = murlock('snagletooth murlock', murlock_text + "\n These murlocks have long snarly teeth.")
snagletooth.refresh_vitals()
snagletooth.set_regex(r'\b(snagle\w*|murlock\w*)\b')
snagletooth.add_item(health_potion)
snagletooth.add_item(ring_of_health)
snagletooth.equip_item(ring_of_health)
dreadclaw.exp_val_setter(100)
mana_potion = consumable('mana potion', 'a vial of bubbly blue liquid', {'mana':20})
mana_potion.set_regex(r'^(mana|potion|mana potion)$')
mana_amulet = equipment('mana charm', 'a plusing carved crystal rune', 'neck', {'mana max':30})
mana_amulet.set_regex(r'^(mana|charm|mana charm)$')
dreadclaw.add_item(mana_potion)
dreadclaw.add_item(mana_potion)