from random import randint
import item_classes
#EXPERIMENTAL TESTING building NPC function. 
def build_npc(npc_class, name, text, exp_val,gold,level, regex, combat_name = None):
    #create object
    npc_obj = npc_class(name,text, exp_val=exp_val,regex=regex, gold=gold,level=level)
    #refresh vitals
    npc_obj.refresh_vitals()
    #add combat name
    if combat_name:
        npc_obj.set_combat_name(combat_name)
    return npc_obj
# creature class, this is the super class for all living things.
class creature:
    def __init__(self, name, text, vitals={}, exp_val = 1, regex = None, gold = 0, level=1):
        # name, short name or combat name, and description
        self.name = name
        self.name_short = None
        self.text = text
        # game stats which convert to vitals. via refresh vitals 
        self.stats = {'str':level, 'agi':level, 'int':level}
        self.vitals = vitals
        #affinity which converts to resistance 
        self.affinity = 'none'
        #attacks dict, special attacks added to it in subclasses
        self.attacks = {'basic attack': self.basic_attack}
        self.special_attacks = {}
        #auto attacking attribute
        self.aggressive = False
        #items list, functions as an inventory
        self.items = []
        # default weapon string 
        self.default_weapon = 'body' 
        # equipment dict
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
        defense = {self.vitals_getter('defense value')}
        stats = str - {self.stats_getter('str')}, agi - {self.stats_getter('agi')}, int - {self.stats_getter('int')}
        resistance; fire = {self.vitals_getter('fire resist')}, water = {self.vitals_getter('water resist')}, shock = {self.vitals_getter('shock resist')}, earth = {self.vitals_getter('earth resist')}'''
    
    #custom copy functions to seperate the vitals. 
    # I FEEL LIKE THIS IS A MESS, I FEEL LIKE EQUIPMENT, AND ACTIVE EFFECTS, AND ITEMS
    # WILL NEED TO BE ADDED TO COPY, I NEED TO TEST AND UPDATE THIS. NOT USING A DEEP COPY
    # TO SAVE MEMORY, UNNECESSARY BUT FOR LEARING PURPOSES.
    def __copy__(self):
        new_instance = type(self)(self.name, self.text, self.vitals.copy(), self.exp_val, self.regex, self.gold,)
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
    #set name short
    def set_combat_name(self, name_string):
        self.name_short = name_string
    # get combat name
    def get_combat_name(self):
        if not self.name_short:
            return self.name
        else: return self.name_short
    # set regex function
    def set_regex(self, regex_pattern):
        self.regex = regex_pattern
    #sets vitals based off of stats
    def refresh_vitals(self):
        self.vitals = {'health max': 25 + (self.stats['str'] * 25), 'health': 25 + (self.stats['str'] * 25),
                       "mana max": self.stats['int'] * 10, 'mana': self.stats['int']*10,
                       'attack value': 1+(self.stats['str'] * 3) + (self.stats['agi'] * 3),
                       'defense value':1+self.stats['agi'] * 5, 'load max' : 50 + (self.stats['str'] * 5),
                       'load': 0, 'fire resist': self.stats['int'] * 3, 'water resist': self.stats['int'] * 3,
                       'shock resist': self.stats['int'] * 3, 'earth resist': self.stats['int'] *3, 'posion resist': self.stats['str'] * 2, 
                       'chaos resist' : 0, 'damage type': 'normal', 'counter attack': None}
        # adjust resistance based on affinity
        match self.affinity:
            case 'water':
                self.get_n_set('water resist', 50)
                self.get_n_set('shock resist', 25, True)
            case 'fire':
                self.get_n_set('fire resist', 50)
                self.get_n_set('water resist', 25, True)
            case 'shock':
                self.get_n_set('shock resist', 50)
                self.get_n_set('earth resist', 25, True)
            case 'earth':
                self.get_n_set('earth resist', 50)
                self.get_n_set('fire resist', 25, True)
            case 'all': 
                self.set_all_resist(25)
            case _:
                pass
    #new set active effects function, takes an effect name (string) and effect dict formatted
    # as {vital to change : amount to change}
    def set_active(self, effect_name, effects_dict):
        #for every item in effects dict,  call get_n_set with item
        for key, value in effects_dict.items():
            if key in ['damage type', 'counter attack']:
                self.vitals_setter(key, value)
            else:
                self.get_n_set(key, value)
        # store effect name and effect dicts in active effects
        self.active_effects[effect_name] = effects_dict
    # new remove active effects func, just takes the name of the effect to remove.
    def remove_active(self, effect_name):
        # for item in effect dict call get_n_set in subtract mode.
        for key, value in self.active_effects[effect_name].items():
            match key:
                # damage types are special since they are strings and categorical. damage type has it's own function.
                case 'damage type':
                    self.reverse_damage_type()
                # counter attack is just a binary variable so it switches easier than damage type
                case 'counter attack':
                    self.vitals_setter('counter attack', None)
                # if active effect is not damage type or counter attack get_n_set will work and gets used.
                case _:
                    self.get_n_set(key, value, True)
        #remove effect name from active effects dict
        self.active_effects.pop(effect_name)
    # reverse damage type function this one is tricky I need to remove current damage type and revert back to weapon damage type 
    # if applicable. still glitches out if you equip a weapon with damage type while an active damage type effect. 
    def reverse_damage_type(self):
        damage_type = 'normal'
        try: damage_type = self.equipment['weapon'][1]['damage type']
        except (KeyError, TypeError): damage_type = 'normal'
        self.vitals_setter('damage type', damage_type)
    # assign weapon function used in combat and ability displays 
    def assign_weapon(self):
        weapon = None
        if self.equipment['weapon'] == None:
            weapon = self.default_weapon
        else: weapon = self.equipment['weapon'][0]
        return weapon
    # assign name for combat and ability displays. ownership implies ownership to an object ie *target_obj's weapon*
    def assign_name(self, target_obj, ownership = False):
        target_name = None
        if target_obj == self:
            target_name = 'you'
            if ownership:
                target_name = 'your'
        else: 
            target_name = target_obj.get_combat_name()
            if ownership:
                target_name = target_name + "'s"
        return target_name

    #basic attack function
    def basic_attack(self, target, power = 'full'):
        # calc damange based on roll, attack val, target defense val
        base_damage = self.vitals_getter('attack value') + randint(0, 10)
        if power == 'lite':
            base_damage = round(base_damage/2)
        damage_type = self.vitals_getter('damage type')
        final_damage =self.calc_dmg(target, base_damage, damage_type)
        # if damage at or below zero report as missed target
        # else deal damage too target, and print
        target.get_n_set('health', final_damage, True)
        return final_damage
    # calculate damge function
    def calc_dmg(self, target, base_dmg, dmg_type):
        new_dmg = 0
        #if damage is normal type use defense value
        dmg_resist = self.match_resist(dmg_type)
        if dmg_resist == 'normal':
            percent = 0
            # first 100 defense value gives .5% damage resist per defense value
            if target.vitals_getter('defense value') <= 100:
                percent = (target.vitals_getter('defense value')/2)/100
            else:
                # beyond the first 100 gain .25% damage resist per defense value
                new_def = target.vitals_getter('defense value') - 100
                percent = .50 + (new_def/4)/100
            # max out damage resist at 75%
            if percent > .75:
                percent = .75
            new_dmg = round(base_dmg * (1 - percent))
        # if damage is not normal use resistance value. one resist value = 1% damage resist for damage types. no cap on maximum
        # might need to add a cap at 100% or elemental damage might heal....
        else:
            target_resist = target.vitals_getter(dmg_resist)
            if target_resist >= 50:
                print(f'{target.get_combat_name()} has high {dmg_resist}')
            if target_resist <= 0:
                print(f'{target.get_combat_name()} is weak against {str.split(dmg_resist)[0]}')
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
            case 'earth':
                return 'earth resist'
            case 'posion':
                return 'posion resist'
            case 'chaos':
                return 'chaos resist'
            case _:
                return 'normal'
    #add many items for building npcs
    def add_many_items(self, *items):
        for item in items:
        # if weight will over-encumber, return false
            if self.vitals_getter('load') + item.weight_getter() > self.vitals_getter('load max'):
                continue
            # else add item to inventory, add weight to load, return true
            self.items.append(item)
            self.get_n_set('load', item.weight_getter())
    # add and equip multiple items. used mostly for building NPCS
    def add_n_equip(self, *items):
        for item in items:
            if self.add_item(item):
                self.equip_item(item)
    # add single item
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
        # search values till value matches item. then set value to none, and remove active effects
        for k,v in self.equipment.items(): 
            if v == None:
                continue
            if v[0] == item.name:
                self.remove_active(item.equipment_type)
                self.equipment[k] = None
                return True
        return False
    # vitals getter
    def vitals_getter(self, stats_string):
        return self.vitals[stats_string]
    # vitals setter   
    def vitals_setter(self, stats_string, value):
        self.vitals[stats_string] = value
    #set all resistance function  for quickly creating npcs
    def set_all_resist(self, amount):
        self.get_n_set('fire resist', amount)
        self.get_n_set('water resist', amount)
        self.get_n_set('shock resist', amount)
        self.get_n_set('earth resist', amount)
        self.get_n_set('poison resist', amount)
        self.get_n_set('chaos resist', amount)
    #set just elemental resistances used when raising int
    def set_elemental_resists(self, amount):
        self.get_n_set('fire resist', amount)
        self.get_n_set('water resist', amount)
        self.get_n_set('shock resist', amount)
        self.get_n_set('earth resist', amount)
    #stats getter    
    def stats_getter(self, stat_string):
        return self.stats[stat_string]
    # a stats setter
    def stats_setter(self, stat_string, value):
        self.stats[stat_string] = value
    #set raise all stats, used when making npcs
    def set_all_stats(self, value):
        self.stats_setter('str', value)
        self.stats_setter('agi', value)
        self.stats_setter('int', value)
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
    # return exp amoutn
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
        new_val = self.vitals.get(stats_string, 0) + value
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
    def __init__(self, name, text, vitals={}, exp_val=1, regex=None, gold=0):
        super().__init__(name, text, vitals, exp_val, regex, gold)
        self.special_attacks = {'bubble attack': self.bubble_atk}
        self.affinity = 'water'
        self.default_weapon = 'claws'
    #murlocks special attack
    def bubble_atk(self, target):
            damage = randint(0, 5) + self.stats_getter('int') * 10
            final_dmg = self.calc_dmg(target, damage, 'water resist')
            target.get_n_set('health', final_dmg, True)
            print(f'{self.get_combat_name()} launches bubbles at {target.get_combat_name()} for {final_dmg} water damage')
# dragon subclass
class dragon(creature):
    def __init__(self, name, text, vitals={}, exp_val=1, regex=None, gold=0, level=1):
        super().__init__(name, text, vitals, exp_val, regex, gold, level)
        self.special_attacks = {'fire breath':self.fire_breath, 'tail swipe':self.tail_swipe, 'chomp':self.chomp}
        self.affinity = 'all'
        self.default_weapon = 'claws'
    #  fire breathe special attack deals fire damage based on int and agi
    def fire_breath(self, target):
        damage = randint(0,10) + (self.stats_getter('agi') + self.stats_getter('int')) * 6
        final_dmg = self.calc_dmg(target,damage,'fire')
        target.get_n_set('health', final_dmg, True)
        print(f'{self.get_combat_name()} takes a deep breath and breathes fire on {target.get_combat_name()} for {final_dmg} fire damage')
    # tail swipe special attack damage based on attack value
    def tail_swipe(self, target):
        damage = randint(0,10) + self.vitals_getter('attack value')
        final_dmg = self.calc_dmg(target,damage,'normal')
        target.get_n_set('health',final_dmg,True)
        print(f'{self.get_combat_name()} quickly turns around and swings it\'s tail at {target.get_combat_name()} for {final_dmg} normal damage')
    # chomp special attack damage based on str and agi
    def chomp(self, target):
        damage = randint(0,10) + (self.stats_getter('str') + self.stats_getter('agi')) * 6
        final_dmg = self.calc_dmg(target,damage,'normal')
        target.get_n_set('health',final_dmg,True)
        print(f'{self.get_combat_name()} snaps his jaws at {target.get_combat_name()} chomping down hard for {final_dmg} normal damage')
# creating creature class objects and item class objects
#setting values for creature objects and adding item objects to creatures
# tower of dragons making the dragons 
# built the old way without the build NPC function. need to rewrite with the build NPC func.
#level 1 piff
piff_text = '''a small green dragon, his scaley skin seems thin and his muscles look loose. 
dispite being a magical dragon, piff seems piddly and weak'''
piff_dragon = dragon('Piff the magic dragon', piff_text,exp_val=10,regex=r'^(piff )?((the )?magic )?dragon$|^piff$',gold=50,level=2)
piff_dragon.set_combat_name('piff')
piff_dragon.refresh_vitals()
piff_dragon.get_n_set('defense value',  25)
kalfor_text = '''this dragon is long and slender, almost snake-like with short arms
it's skin is covered in fur rather than scales and it's friendly dog face almost
makes you think you could befriend it. The moment you approach however it snarls and poises aggressivly '''
#level 2 kalfor
kalfor_dragon =dragon('Kalfor the unlucky', kalfor_text)
kalfor_dragon.set_regex(r'^kalfor( the unlucky)?$|^(kalfor )?dragon$')
kalfor_dragon.set_combat_name('kalfor')
kalfor_dragon.add_gold(100)
kalfor_dragon.exp_val_setter(30)
kalfor_dragon.stats_setter('str', 4)
kalfor_dragon.stats_setter('agi', 2)
kalfor_dragon.refresh_vitals()
kalfor_dragon.set_all_resist(25)
kalfor_dragon.vitals_setter('defense value', 35)
#level 3 dortrog
dortrog_text = '''this dragon is odd looking. it's thin legs and tiny wings look odd for it long scaley body.
but the most bizare is the one large, very muscular, human looking arm. This dragon storms around angrily obviously unfriendly'''
dortrog_dragon = dragon('dortrog the burninator', dortrog_text)
dortrog_dragon.set_regex(r'^dortrog( the burninator)?$|^(dortrog )?dragon$')
dortrog_dragon.set_combat_name('dortrog')
dortrog_dragon.add_gold(200)
dortrog_dragon.exp_val_setter(100)
dortrog_dragon.stats_setter('str', 6)
dortrog_dragon.stats_setter('agi', 2)
dortrog_dragon.refresh_vitals()
dortrog_dragon.set_all_resist(25)
dortrog_dragon.vitals_setter('defense value', 40)
#level 4 mushy
mushy_text = '''this dragon is small and red with a long snake-like body. it has small horns on it's head and is very quick.'''
mushy_dragon = dragon('mushy the guardian', mushy_text)
mushy_dragon.set_regex(r'^mushy( the guardian)?$|^dragon$')
mushy_dragon.set_combat_name('mushy')
mushy_dragon.add_gold(400)
mushy_dragon.exp_val_setter(200)
mushy_dragon.stats_setter('str', 4)
mushy_dragon.stats_setter('agi', 6)
mushy_dragon.refresh_vitals()
mushy_dragon.set_all_resist(25)
mushy_dragon.vitals_setter('defense value', 50)
#level 5 spiral
spiral_text = '''This young purple dragon has gold wings and gold horns. His horns and tail and a very distinct spiral pattern to them 
He stands proud and looks suprisingly quick and strong dispite the rooms happy aura this dragon doesn't look like he would be your friend'''
spiral_dragon = dragon('spiral the dragon', spiral_text)
spiral_dragon.set_regex(r'^(spiral (the )?)?dragon$|^spiral$')
spiral_dragon.set_combat_name('spiral')
spiral_dragon.add_gold(600)
spiral_dragon.exp_val_setter(400)
spiral_dragon.stats_setter('str', 7)
spiral_dragon.stats_setter('agi', 7)
spiral_dragon.refresh_vitals()
spiral_dragon.set_all_resist(30)
spiral_dragon.vitals_setter('defense value', 60)
#level 6 scorchhard
scorchhard_text = '''This large orange dragon has large blue wings, small stumpy horns and a perminate fire burning on it's tail. 
It walks only on it's hind legs with it's front arms smaller for grabbing. The fire on it's tail burns brighter when it is angry.
why it's name is pocket monester seems to be lost in translation'''
scorchard_dragon = dragon('scorchhard the pocket monster', scorchhard_text)
scorchard_dragon.set_regex(r'^scorchhard( the pocket monster)?$|^dragon$')
scorchard_dragon.set_combat_name('scorchhard')
scorchard_dragon.add_gold(1000)
scorchard_dragon.exp_val_setter(700)
scorchard_dragon.stats_setter('str', 9)
scorchard_dragon.stats_setter('agi', 7)
scorchard_dragon.refresh_vitals()
scorchard_dragon.set_all_resist(35)
scorchard_dragon.vitals_setter('defense value', 70)
#level 7 draco HE NEEDS A SPOOF NAME
lizco_text = '''This dragon is very big, it's dark brown and copper colored with a frill of horns on it's head. A sturdy body 
and four thick limbs make this dragon appear very stout. He look fairly intelegent and has a scar on his chest from where he 
once shared his heart.'''
lizco_dragon = dragon('lizco the lizardheart', lizco_text)
lizco_dragon.set_regex(r'^lizco( the)?( lizardheart)?( dragon)?$|^dragon$')
lizco_dragon.set_combat_name('lizco')
lizco_dragon.add_gold(1500)
lizco_dragon.exp_val_setter(1000)
lizco_dragon.stats_setter('str', 11)
lizco_dragon.stats_setter('agi', 8)
lizco_dragon.refresh_vitals()
lizco_dragon.set_all_resist(40)
lizco_dragon.vitals_setter('defense value', 80)
#level 8 smaug SPOOF TO SMUG OR SMOOG
lyttire_text='''This long dragon has red and black scales covering it long snake-like body. Unlike the other long dragons 
this dragon has long legs and arms and it's wings attach to it's arms. Greedy, wicked, and vilianious, a truely terrifying creature'''
lyttire_dragon=dragon('littire the little', lyttire_text)
lyttire_dragon.set_regex(r'^littire( the)?( little)?( dragon)?$|^dragon$')
lyttire_dragon.set_combat_name('littire')
lyttire_dragon.add_gold(2000)
lyttire_dragon.exp_val_setter(1400)
lyttire_dragon.stats_setter('str', 12)
lyttire_dragon.stats_setter('agi', 10)
lyttire_dragon.refresh_vitals()
lyttire_dragon.set_all_resist(40)
lyttire_dragon.vitals_setter('defense value', 90)
#level 9 deathwing from warcraft
warwing_text = '''this dragon is massive and all black. It's scales look like stone and it's skin almost appears to be lava.
it's red eyes look ready to strike and it's powerful body looks capable of untold destruction'''
warwing_dragon = dragon('warwing the deathcraft', warwing_text)
warwing_dragon.set_regex(r'^warwing( the)?( deathcraft)?( dragon)?$|^dragon$')
warwing_dragon.set_combat_name('warwing')
warwing_dragon.add_gold(2500)
warwing_dragon.exp_val_setter(1700)
warwing_dragon.stats_setter('str', 13)
warwing_dragon.stats_setter('agi', 13)
warwing_dragon.refresh_vitals()
warwing_dragon.set_all_resist(45)
warwing_dragon.vitals_setter('defense value', 100)

#level 10 bahamut HE NEEDS A SPOOF NAME
muthaba_text = '''This dragon is platnium in color with 2 long horns on it's head. With 4 strong legs and wings coming from
it's back this dragon stands tall and nobel as the lord of all dragons. His strength is unmatched'''
muthaba_dragon = dragon('muthaba the dragonlord', muthaba_text)
muthaba_dragon.set_regex(r'^muthaba( the)?( dragonlord)?( dragon)?$|^dragon$')
muthaba_dragon.set_combat_name('muthaba')
muthaba_dragon.add_gold(3000)
muthaba_dragon.exp_val_setter(2000)
muthaba_dragon.stats_setter('str', 15)
muthaba_dragon.stats_setter('agi', 15)
muthaba_dragon.refresh_vitals()
muthaba_dragon.set_all_resist(50)
muthaba_dragon.vitals_setter('defense value', 120)
#other creatures
rat= creature('rat', 'a large disgusting rat')
rat.set_regex(r'^ra?t?$')
rat.refresh_vitals()
rat.add_gold(10)
rat.vitals_setter('shock resist', 50)
rat.vitals_setter('water resist', 0)
# murlocks and some items for the murlocks
young_murlock = murlock('young murlock', murlock_text + "\n this murlock is just a juvenial")
young_murlock.set_regex(r'^(young )?murlock$')
young_murlock.exp_val_setter(5)
young_murlock.refresh_vitals()
young_murlock.vitals_setter('water resist', 50)
young_murlock.vitals_setter('shock resist', -25)
dreadclaw = murlock('dreadclaw murlock', murlock_text + "\n this murlock has large claws.")
dreadclaw.set_all_stats(2)
dreadclaw.refresh_vitals()
dreadclaw.exp_val_setter(10)
dreadclaw.set_regex(r'\b(dread\w*|murlock\w*)\b')
dreadclaw_chief = murlock('dreadclaw chief', murlock_text +'\n this murlock is the leader of the dreadclaws',)
dreadclaw_chief.set_regex(r'^(dreadclaw|chief|murlock)( (dreadclaw|chief|murlock)){0,2}$')
dreadclaw_chief.set_all_stats(3)
dreadclaw_chief.refresh_vitals()
dreadclaw_chief.vitals_setter('water resist', 50)
dreadclaw_chief.vitals_setter('shock resist', 0)
dreadclaw_chief.exp_val_setter(30)
dreadclaw_chief.add_gold(50)
ring_of_health = item_classes.equipment('ring of health', 'a glowing red ring','finger', {'health max':50})
ring_of_health.set_regex(r'^ring( of health| health)?$')
ring_of_health.change_price(50)
health_potion = item_classes.consumable('health potion', 'a vial of a red bubbly liquid', {'health':50})
health_potion.set_regex(r'^(health|potion|health potion)$')
dreadclaw.add_item(health_potion)
snagletooth = murlock('snagletooth murlock', murlock_text + "\n This murlock has long snarly teeth.")
snagletooth.set_all_stats(2)
snagletooth.refresh_vitals()
snagletooth.vitals_setter('shock resist', -25)
snagletooth.vitals_setter('water resist', 50)
snagletooth.exp_val_setter(10)
snagletooth.set_regex(r'\b(snagle\w*|murlock\w*)\b')
snagletooth.add_item(health_potion)
snagletoooth_cheif = murlock('snagletooth chief', murlock_text + "\n this is the chief of the snagletooths")
snagletoooth_cheif.set_regex(r'^(snagletooth|chief|murlock)( (snagletooth|chief|murlock)){0,2}$')
snagletoooth_cheif.set_all_stats(3)
snagletoooth_cheif.refresh_vitals()
snagletoooth_cheif.vitals_setter('water resist', 50)
snagletoooth_cheif.vitals_setter('shock resist', 0)
snagletoooth_cheif.exp_val_setter(30)
snagletoooth_cheif.add_gold(50)
snagletoooth_cheif.add_item(ring_of_health)
snagletoooth_cheif.add_item(item_classes.west_door_key_blue)
snagletoooth_cheif.add_item(item_classes.fishing_trident)
snagletoooth_cheif.equip_item(item_classes.fishing_trident)
murlock_guard = murlock('murlock guard', murlock_text + '\n this solid murlock guards the longhouse, he looks serious')
murlock_guard.set_regex(r'^murlock( guard)?$|^guard$')
murlock_guard.set_all_stats(2)
murlock_guard.refresh_vitals()
murlock_guard.vitals_setter('water resist', 50)
murlock_guard.vitals_setter('shock resist', 0)
murlock_guard.exp_val_setter(15)
murlock_guard.add_gold(35)
murlock_guard.add_item(item_classes.fishing_trident)
murlock_guard.equip_item(item_classes.fishing_trident)
mana_potion = item_classes.consumable('mana potion', 'a vial of bubbly blue liquid', {'mana':20})
mana_potion.set_regex(r'^(mana|potion|mana potion)$')
mana_amulet = item_classes.equipment('mana charm', 'a plusing carved crystal rune', 'neck', {'mana max':20})
mana_amulet.set_regex(r'^(mana|amulet|mana amulet)$')
mana_amulet.change_price(50)
dreadclaw.add_item(mana_potion)
dreadclaw_chief.add_item(mana_amulet)
dreadclaw_chief.add_item(item_classes.west_door_key_green)
dreadclaw_chief.add_item(item_classes.fishing_trident)
dreadclaw_chief.equip_item(item_classes.fishing_trident)
snagletooth.add_gold(25)
dreadclaw.add_gold(25)
#farm creatures 
farm_boy =creature('a young boy', 'a small farmboy, wearing plain clothes, playing with a wooded sword')
farm_boy.refresh_vitals()
farm_boy.exp_val_setter(2)
farm_boy.set_regex(r'^(small )?boy$')
farm_boy.add_item(item_classes.wooden_sword)
farm_boy.equip_item(item_classes.wooden_sword)
sheep = creature('a bleating sheep', 'a small sheep wandering around, eating glass and bleating', exp_val=5, regex=(r'^(bleating )?sheep$'))
sheep.refresh_vitals()
sheep.set_combat_name('sheep')
sheep.add_n_equip(item_classes.sheep_skin)
cow = creature('a black and white cow', 'a large black and white cow lazily chewing', exp_val=20, regex=r"^(black and white )?cow$")
cow.set_combat_name('cow')
cow.refresh_vitals()
cow.add_n_equip(item_classes.cow_skin)
# these were built with the build_npc func works much better
bull = build_npc(creature,'angry bull', 'a large angry bull', 10, 0,2, r'^(angry )?bull$', 'bull')
bull.add_n_equip(item_classes.bull_skin)
farmer = build_npc(creature,'a strong farmer', 'a strong farmer who earns his living off the animals and land', 10, 20,2,r'^(strong )?farmer$','farmer')
farmer.add_n_equip(item_classes.farmers_hat, item_classes.farmers_knife, item_classes.farmers_pants)
farm_wife = build_npc(creature,'a hardworking farm woman', 'this woman works in both the fields and the house', 10,20,2,r'(farm )?woman$', 'woman')
farm_wife.add_n_equip(item_classes.kitchen_apron, item_classes.pot_holders,item_classes.faimly_necklace,item_classes.kitchen_knife)