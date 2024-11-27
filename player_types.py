import asyncio
from player_class import player
from class_test import creature, murlock
creature_list = [creature, murlock]
# a sorcerer subclass
class sorcerer(player):
    def __init__(self, name, text=...) -> None:
        super().__init__(name, text)
        self.attacks = self.attacks | {'grasp': self.grasp, 'armour': self.armour, 'fireball': self.fireball,
                                       'enchant': self.enchant}
    # a shocking grasp spell
    async def grasp(self, target = None):
        '''# check occupied attribute and level. if checks fail return
        if not self.busy_n_level_check(1):
            return
        #validate target, assign default target if none passed. returns bool or target object
        target_obj = self.validate_default_target(self.location.contents, target, creature_list)
        # if validate returns bool returj
        if type(target_obj) == bool:
            return
        #run mana check, if success subtracts mana, starts cast time, sets occupied status
        mana_check = await self.mana_check_n_set(5)
        # if mana check was sucessful print
        if mana_check:'''
        #validate target, default target, mana, and cast time. returns target object or False
        target_obj = await self.ability_prep(1,5,'target', target, creature_list)
        #if target object, print
        if target_obj:
            if target_obj not in self.location.contents:
                print('that target is not here anymore')
            else:    
                print(f'you grab {target_obj.name}, and shock them with magical energy')
                # calculate damage and print
                damage = self.stats_getter('int') * 7
                print(f'you deal {damage} damage to {target_obj.name}')
                # deal damage to target
                target_obj.get_n_set('health', damage, True)
                self.combat_check_n_set(target_obj)
        # resest occupied status
        self.occupied = False
    # armour spell 
    async def armour(self, target = None):
        '''# run occuiped and level check, if failed return
        if not self.busy_n_level_check(1):
            return
        # validate target if passed if not assign default, returns target object or bool
        target_obj = self.validate_default_self(self.location.contents, target, creature_list)
        # if validate failed return 
        if not target_obj:
            return
        # run mana check 
        mana_check = await self.mana_check_n_set(5)
        # if mana check
        if mana_check:'''
        #validate target, default target, cost, and cast time. returns target object or False
        target_obj = await self.ability_prep(1,5,'self', target, creature_list)
        if not target_obj:
            self.occupied = False
            return
        #if target object, print
        if target_obj == self or target_obj in self.location.contents:
            print(f'a glowing magical armour surrounds {target_obj.name}')
            # set spell effects
            self.get_n_set('defence value', 10)
            #set occuiped to false
            self.occupied = False
            #wait spell duration
            await asyncio.sleep(60)
            # print and remove spell effects
            print(f'the magical aura around {target_obj.name} shimmers and disapears')
            self.get_n_set('defence value', 10, True)
        else: self.occupied = False
    # a fireball spell
    async def fireball(self, target = None):
        '''# check occuiped and level if fail return
        if not self.busy_n_level_check(2):
            return
        # vaalidate target if passed, if not assign defaut target, returns target object or bool
        target_obj = self.validate_default_target(self.location.contents, target, creature_list)
        # if False return
        if not target_obj:
            return
        # run mana check
        mana_check = await self.mana_check_n_set(10)
        # if success
        if mana_check:'''
        # validate target, assign default, cost, and cast time, returns target object or bool
        target_obj = await self.ability_prep(2, 10, 'target', target, creature_list)
        if target_obj:   # make certain target is still present, if not print
            if target_obj not in self.location.contents:
                print('that target is no longer here')
            # if target is here print
            else:
                print(f'you throw a ball of hot fire at {target_obj.name}')
                #calaculate damage
                damage = self.stats_getter('int') * 9
                #apply damage
                target_obj.get_n_set('health', damage, True)
            # set occupied to False
        self.occupied = False
    # a enchant weapon spell
    async def enchant(self, target = None):
        # validate target, assign default, cost, and cast time, returns target object or bool
        target_obj = await self.ability_prep(2, 10, 'self', target, creature_list)
        #if validate failed return
        if not target_obj:
            return
        # if target object is self or in self.location, print
        if target_obj == self or target_obj in self.location.contents:
            print(f"{target_obj.name}'s {target_obj.weapon} beging glow with a magical aura")
            # self value for spell, and set occuiped to false
            target_obj.get_n_set('attack value', 15)
            self.occupied = False
            #wait spell duration
            await asyncio.sleep(60)
            # print and remove spell effect
            print(f'the magical aura around {target_obj}\'s weapon fades away')
            target_obj.get_n_set('attack value', 15, True)
        #if spell fail turn occupied to false
        else: self.occupied = False