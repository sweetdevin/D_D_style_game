import asyncio
from random import randint
from player_class import player
from class_test import creature, murlock
creature_list = [creature, murlock]
# a sorcerer subclass
class sorcerer(player):
    def __init__(self, name, text=...) -> None:
        super().__init__(name, text)
        self.attacks = self.attacks | {'grasp': self.grasp, 'armour': self.armour, 'fireball': self.fireball,
                                       'enchant': self.enchant, 'tsunami': self.tsumani, 'chaos': self.chaos_magic,
                                       'weaken': self.weaken, 'bolt': self.bolt, 'firestorm': self.firestorm, 
                                       'trance': self.trance}
    # a shocking grasp spell
    async def grasp(self, target = None):
        #validate target, default target, mana, and cast time. returns target object or False
        target_obj = await self.ability_prep(1,5,'target', target, creature_list)
        #if target object, print
        if target_obj:
            if self.target_location_check(target_obj):    
                print(f'you grab {target_obj.name}, and shock them with magical energy')
                # calculate damage and print
                damage = randint(0, 6) + self.stats_getter('int') * 4
                final_dmg = self.calc_dmg(target_obj, damage, 'shock')
                print(f'you deal {final_dmg} of shock damage to {target_obj.name}')
                # deal damage to target
                target_obj.get_n_set('health', final_dmg, True)
                self.combat_check_n_set(target_obj)
        # resest occupied status
        self.occupied = False
    # armour spell 
    async def armour(self, target = None):
        #validate target, default target, cost, and cast time. returns target object or False
        target_obj = await self.ability_prep(2,5,'self', target, creature_list)
        if target_obj:
        #if target object, print
            if self.target_location_check(target_obj):
                print(f'a glowing magical armour surrounds {target_obj.name}')
                # set spell effects
                amount = randint(0,8) + self.stats_getter('int') * 5
                target_obj.set_active('mage armour', {'defense value':amount})
                #set duration
                duration = 15 + self.stats_getter('int') * 15
                #wait spell duration
                asyncio.create_task(self.ability_countdown_timer(target_obj, 'mage armour',duration))
                # print and remove spell effects
                #print(f'the magical aura around {target_obj.name} shimmers and disapears')
                #target_obj.remove_active('mage armour')
        self.occupied = False
    # a fireball spell
    async def fireball(self, target = None):
        # validate target, assign default, cost, and cast time, returns target object or bool
        target_obj = await self.ability_prep(3, 10, 'target', target, creature_list)
        if target_obj:   
            # make certain target is still present, if not print
            if self.target_location_check(target_obj):
            # if target is here print
                print(f'you throw a ball of hot fire at {target_obj.name}')
                #calaculate damage
                damage = randint(0, 10) + self.stats_getter('int') * 7
                final_dmg = self.calc_dmg(target_obj, damage, 'fire')
                #apply damage
                target_obj.get_n_set('health', final_dmg, True)
                print(f'you deal {final_dmg} fire damage to {target_obj.name}')
                self.combat_check_n_set(target_obj)
            # set occupied to False 
        self.occupied = False
    # a enchant weapon spell
    async def enchant(self, target = None):
        # validate target, assign default, cost, and cast time, returns target object or bool
        target_obj = await self.ability_prep(4, 15, 'self', target, creature_list)
        # if target object is self or in self.location, print
        if target_obj:
            if self.target_location_check(target_obj):
                print(f"{target_obj.name}'s weapon beging glow with a magical aura")
                # self value for spell, and set occuiped to false
                amount = randint(6, 12) + self.stats_getter('int') * 3
                target_obj.set_active('enchant weapon', {'attack value': amount})
                #set duration
                duration = 15 + self.stats_getter('int') * 15
                #wait spell duration
                asyncio.create_task(self.ability_countdown_timer(target_obj, 'enchant weapon', duration))
        #if spell fail turn occupied to false
        self.occupied = False
    # a tsunami spell
    async def tsumani(self, target = None):
        target_obj = await self.ability_prep(5, 25, 'target', target, creature_list)
        if target_obj:   # make certain target is still present, if not print
            if self.target_location_check(target_obj):
                print(f'you summon a massive wall of water to crash down upon {target_obj.name}')
                dmg = randint(8, 24) + self.stats_getter('int') * 8
                final_dmg = self.calc_dmg(target_obj, dmg, 'water')
                target_obj.get_n_set('health', final_dmg, True)
                print(f'you deal {final_dmg} water damage to {target_obj.name}')
                self.combat_check_n_set(target_obj)
        self.occupied = False
    # a  chaos dmg buff
    async def chaos_magic(self, target = None):
        #ability prep: checks level, target, mana, subtracts mana, set target, casting delay 
        target_obj = await self.ability_prep(6, 40, 'self', target, creature_list)
        # if target obj exists,
        if target_obj:
            # check to make sure target is still at current location
            if self.target_location_check(target_obj):
                #print spell text
                print(f"{target_obj.name}'s weapon warps and blurs with a twisted distored magic")
                #set spell effects
                target_obj.set_active('chaos', {'damage type': 'chaos'})
                #set duration
                duration = 30 + self.stats_getter('int') * 20
                #wait spell duration
                asyncio.create_task(self.ability_countdown_timer(target_obj, 'chaos magic', duration))
        #set occupied status to false
        self.occupied = False
    # a lightning bolt spell
    async def bolt(self, target = None):
        # ability prep checks level, target, mana, subtracts mana, sets target, casting delay
        target_obj = await self.ability_prep(7, 45, 'target', target, creature_list)
        # if target obj exists
        if target_obj:
            # check to make sure target is still in current location.
            if self.target_location_check(target_obj):
                # print spell text
                print(f'you summon a lighting bolt for the sky to hit {target_obj.name}')
                # calc damage
                dmg = randint(25, 45) + self.stats_getter('int') * 10
                final_dmg = self.calc_dmg(target_obj, dmg, 'shock')
                #set spell damage
                target_obj.get_n_set('health', final_dmg, True)
                # print spell damage
                print(f'you deal {final_dmg} shock damage to {target_obj.name}')
                self.combat_check_n_set(target_obj)
        # set occupied status
        self.occupied = False
    async def weaken(self, target = None):
        #ability prep: checks level, target, mana, subtracts mana, set target, casting delay 
        target_obj = await self.ability_prep(8, 50, 'target', target, creature_list)
        # if target obj exists,
        if target_obj:
            # check to make sure target is still at current location
            if self.target_location_check(target_obj):
                #print spell text
                print(f"{target_obj.name}'s stength and courage fade away")
                #set spell effects
                amount = randint(0, 10) + self.stats_getter('int') * 3
                target_obj.set_active('weaken', {'attack value': -amount//2, 'defense value': amount})
                #set duration
                duration = 10 + self.stats_getter('int') * 10
                #wait spell duration
                asyncio.create_task(self.ability_countdown_timer(target_obj, 'weaken', duration))
                self.combat_check_n_set(target_obj)
        #set occupied status to false
        self.occupied = False
        #firestorm spell
    async def firestorm(self, target = None):
        # ability prep checks level, target, mana, subtracts mana, sets target, casting delay
        target_obj = await self.ability_prep(9, 60, 'target', target, creature_list)
        # if target obj exists
        if target_obj:
            for num in range(self.stats_getter('int')//3):
                # check to make sure target is still in current location.
                if self.target_location_check(target_obj):
                    # print spell text
                    print(f'fireballs rain down in a massive firestorm on {target_obj.name}')
                    # calc damage
                    dmg = randint(25, 45) + self.stats_getter('int') * 7
                    final_dmg = self.calc_dmg(target_obj, dmg, 'shock')
                    #set spell damage
                    target_obj.get_n_set('health', final_dmg, True)
                    # print spell damage
                    print(f'you deal {final_dmg} fire damage to {target_obj.name}')
                    self.combat_check_n_set(target_obj)
                    await asyncio.sleep(5)
        # set occupied status
        self.occupied = False
    async def trance(self, target = None):
        #ability prep: checks level, target, mana, subtracts mana, set target, casting delay 
        target_obj = await self.ability_prep(10, 75, 'self', target, creature_list)
        # if target obj exists,
        if target_obj:
            # check to make sure target is still at current location
            if self.target_location_check(target_obj):
                #print spell text
                print(f"raw magical energy flows through {target_obj.name}, greatly enhancing all resistance")
                #set spell effects
                amount = randint(0, 10) + self.stats_getter('int') * 3
                target_obj.set_active('trance', {'shock resist': amount, 'fire resist': amount, 'water resist': amount,
                                                 'chaos resist': amount, 'defense value': amount})
                #set duration
                duration = 10 + self.stats_getter('int') * 12
                #wait spell duration
                asyncio.create_task(self.ability_countdown_timer(target_obj, 'weaken', duration))
        #set occupied status to false
        self.occupied = False
        #firestorm spell