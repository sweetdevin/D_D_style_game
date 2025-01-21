import asyncio
from random import randint
from player_class import player, ReporterMethod, asyncReporterMethod
from class_test import creature, murlock
from string import Template
creature_list = [creature, murlock]
# a sorcerer subclass

class sorcerer(player):
    def __init__(self, name, text=...) -> None:
        super().__init__(name, text)
        self.attacks = self.attacks | {'grasp': self.grasp, 'armour': self.armour, 'fireball': self.fireball,
                                       'enchant': self.enchant, 'tsunami': self.tsunami, 'chaos': self.chaos_magic,
                                       'weaken': self.weaken, 'bolt': self.bolt, 'firestorm': self.firestorm, 
                                       'trance': self.trance}
    # a shocking grasp spell, nuke base, damage based on int, shock damage
    async def grasp(self, target = None):
        damage = randint(0,6) + self.stats_getter('int') * 4
        template_string = Template("you grab $name and shock them with your grasp")
        await self.nuke(1, 5, damage, 'shock', template_string, target)
    grasp = asyncReporterMethod(grasp, 'level 1 \nmana cost 5 \ngrab a target and deal shock damage through your grasp. \nsyntax: "grasp" or "grasp *target*"')
    # armour spell, buff base, amount based on int, time based on int, increases defense value
    async def armour(self, target = None):
        effect_dict = {'defense value': self.stats_getter('int') * 4}
        flavor_template = Template('a magical aura surrounds $name')
        duration = 15 + self.stats_getter('int') * 15
        await self.buff(2,5, effect_dict, 'mage armour', flavor_template, duration, target)
    armour = asyncReporterMethod(armour, 'level 2 \nmana cost 5 \nmagically enhance defenses for your or your target. \nsyntax: "armour" or "armour *target*"')  
    # a fireball spell, nuke base, amount based on int, fire damage
    async def fireball(self, target = None):
        #calaculate damage
        damage = randint(0, 10) + self.stats_getter('int') * 6
        flavor_template = Template('you hurl a red hot ball of fire at $name')
        await self.nuke(3,10,damage, 'fire', flavor_template, target)
    fireball = asyncReporterMethod(fireball, 'level 3 \nmana cost\ncreate and hurl a ball of fire at your target. \nsyntax: "fireball" or "fireball *target*"')
    # a enchant weapon spell, buff base, amount based on int, time base on int, increases attack value
    async def enchant(self, target = None):
        amount = randint(6, 12) + self.stats_getter('int') * 2
        effect_dict = {'attack value': amount}
        falvor_template=Template('$name $weapon starts to glow with magical energy')
        duration = 15 + self.stats_getter('int') * 15
        await self.buff(4,15,effect_dict, 'enchant weapon', falvor_template, duration, target, True)
    enchant = asyncReporterMethod(enchant, 'level 4\nmana cost 15\nyou use magic to enhance the offences of you or your tagert.\nsyntax: "enchant" or "enchant *target*"')
    # a tsunami spell, nuke base, amount based on int, water damage,
    async def tsunami(self, target = None):
        damage = randint(8, 24) + self.stats_getter('int') * 7
        flavor_template = Template('you summon a massive wall of water to crash down upon $name')
        await self.nuke(5,25,damage,'water',flavor_template,target)
    tsunami = asyncReporterMethod(tsunami, 'level 5\nmana cost 25\ncreate a tidal wave to crash into your target\nsyntax: "tsunami" or "tsunami *target*"')
    # a chaos dmg buff, buff base, time based on int, changes damage type to chaos
    async def chaos_magic(self, target = None):
        duration = 30 + self.stats_getter('int') * 20
        effect_dict = {'damage type': 'chaos'}
        flavor_template = Template('$name $weapon warps a burls with a distorted magic')
        await self.buff(6,40,effect_dict,'chaos magic', flavor_template, duration, target, True)
    chaos_magic = asyncReporterMethod(chaos_magic, 'level 6\nmana cost 40\nneither fire, shock, water, or earth, but something more twisted. you enchant your or your target with chaos magic\nsyntax: "chaos" or "chaos target"')
    # a lightning bolt spell, nuke base, amount based on int, shock damage
    async def bolt(self, target = None):
        dmg = randint(25, 45) + self.stats_getter('int') * 9
        falvor_template = Template('you summon a lighting bolt form the sky to hit $name')
        await self.nuke(7,40,dmg,'shock', falvor_template, target)
    bolt = asyncReporterMethod(bolt, 'level 7\nmana cost 40\nyou call a lightning bolt from the sky to strike your target\nsyntax: "bolt" or "bolt *target*"')
    # weak spell, debuff base, amount based on int, time based in int, decreases target attack and defense value
    async def weaken(self, target = None):
        amount =  randint(0, 9) + self.stats_getter('int') * 3
        effect_dict = {'attack value': -amount//2, 'defense value': -amount}
        duration = 10 + self.stats_getter('int') * 5
        flavor_template = '$name strength and courage fade away'
        await self.debuff(8,50,effect_dict,'weaken', flavor_template, duration, target,True)
    weaken = asyncReporterMethod(weaken, 'level 8\nmana cost 50\nyou use your magic to drain the strength form your target\nsyntax: "weaken" or "weaken *target*"')
    #firestorm spell, multi nuke base, amount based on int, rounds, based on int, fire damage
    # might add an earth damage element 
    async def firestorm(self, target = None):
        damage_range = [self.stats_getter('int') * 7 + 15, self.stats_getter('int') * 7 + 35]
        flavor_template = Template('fireballs rain down from the sky on $name')
        rounds = round(1 + self.stats_getter('int') //3)
        interval = 5
        await self.multi_nuke(9,60,damage_range,'fire',rounds,interval,flavor_template,target)
    firestorm = asyncReporterMethod(firestorm, '''level 9\nmana cost 60\nyour create a firestorm and let fireballs rain down on your target
                                    \nsyntax: "firestorm" or "firestorm *target*"''')
    #trance spell, buff base, amount based on int, time based on int, raises all defense 
    async def trance(self, target = None):
        amount = randint(0, 10) + self.stats_getter('int') * 3
        effect_dict = {'shock resist': amount, 'fire resist': amount, 'water resist': amount,
                         'chaos resist': amount, 'posion resist': amount, 'defense value': amount}
        duration = 10 + self.stats_getter('int') * 12
        flavor_template = Template('raw magical energy courses through $name body, greatly enhancing all resistance')
        await self.buff(10,75,effect_dict,'trance',flavor_template,duration,target,True)
    trance = asyncReporterMethod(trance, 'level 10\nmana cost 75\nyou let magical energy flow through your body making you resiliant toward any damage\nsyntax: "trance" or "trance *target*"')
#rouge class
class rogue(player):
    def __init__(self, name, text=...):
        super().__init__(name, text)
        self.attacks = self.attacks | {'slash': self.slash, 'sharpen': self.sharpen, 'thrust': self.thrust,
                                       'poison': self.poison_weapon, 'ignore': self.ignore_armour, 'fire': self.fire_weapon,
                                       'cripple': self.cripple, 'bandage': self.bandage_wounds, 'counter':self.counter_attack,
                                       'lightweight': self.light_weight}
    # slash spell, nuke base, damage based on attack value, damage type passes through
    async def slash(self, target = None):
        damage = randint(10, 20) + self.vitals_getter('attack value')
        flavor_template = Template('you quickly slash your $weapon into $name')
        damage_type = self.vitals_getter('damage type')
        await self.nuke(1,5,damage,damage_type,flavor_template,target)
    slash = asyncReporterMethod(slash, 'level 1\nmana cost 5\nslash with your weapon at your target\nsyntax: "slash" or "slash *target*"')
    # sharpen weapon ability, buff base, amount base on int and agi, time based on int and agi, raises attack value
    async def sharpen(self, target = None):
        amount = randint(6, 12) + self.stats_getter('int') + self.stats_getter('agi')
        effect_dict = {'attack value': amount}
        duration = 30 + (self.stats_getter('agi') * 10) + (self.stats_getter('int') * 10)
        flavor_template = Template("you sharpen $name $weapon improving it's damage")
        await self.buff(2,5,effect_dict,'sharpen',flavor_template,duration,target,True)
    sharpen = asyncReporterMethod(sharpen, 'level 2\nmana cost 5\nevery good rogue always has a sharp blade. use your skills to improve a weapons damage\n syntax: "sharpen" or "sharpen *tagert*"')
    # a stab ability, multi nuke base, amount based on attack value, rounds based on attack value, damage type passes through
    async def thrust(self, target = None):
        rounds = round(1 + self.stats_getter('agi')/2)
        interval = 1 
        damage_range =[self.vitals_getter('attack value'), self.vitals_getter('attack value') + 10]
        flavor_template = Template('you quickly stab $name with your $weapon')
        damage_type = self.vitals_getter('damage type')
        await self.multi_nuke(3,15,damage_range,damage_type,rounds,interval,flavor_template,target)
    thrust = asyncReporterMethod(thrust, '''level 3\nmana cost 15\nspeed is a rogues ally. summon your speed and rage to quickly stab your target multiple times
                                 \nsyntax: "thrust" or "thrust *target*"''')
    # a posion weapon ability, buff base, time based on int and agi, changes damage type to poison
    async def poison_weapon(self, target = None):
        effect_dict = {'damage type': 'poison'}
        duration = 15 + (self.stats_getter('int') * 10) + (self.stats_getter('agi') * 10)
        flavor_template = Template("you pour a small vial of black liquid over $name $weapon poisoning it")
        await self.buff(4,10,effect_dict,'poison weapon',flavor_template,duration,target,True)
    poison_weapon = asyncReporterMethod(poison_weapon, '''level 4\nmana cost 10
                                        \npoison isn't underhanded, it's just strategy
                                        \nany good rogue always has some poison on hand and the knowledge of how to use it
                                        \nsyntax: "poison" or "poison *target*"''')
    # ignore armour spell, pierce defense base, damage based on attack, pierce percent base on agi
    async def ignore_armour(self, target = None):
        damage = randint(0, 10) + self.vitals_getter('attack value')
        flavor_template = Template('with keen eyes and quick feet you see a weakness in $name armour and strike')
        damage_type = self.vitals_getter('damage type')
        pierce_percent = self.stats_getter('agi') * .05
        if  pierce_percent > 1.0 :
            pierce_percent = 1.0
        await self.pierce_defense(5,10,damage,damage_type,pierce_percent,flavor_template,target,True)
    ignore_armour = asyncReporterMethod(ignore_armour, '''level 5\nmana cost 10
                                        \nevery armour has it's weakness, every rouge is practiced in seeing it
                                        \nyou will strike at that unarmoured part of your target cutting through their defense
                                        \nsyntax: "ignore" or "ignore *target*"''')
    # fire weapon ability, buff base, time based on int and agi, changes damage type to fire
    async def fire_weapon(self, target = None):
        effect_dict = {'damage type': 'fire'}
        duration = 15 + (self.stats_getter('int') * 10) + (self.stats_getter('agi') * 10)
        flavor_template = Template("you pour a small vial of red liquid over $name $weapon and it errupts into flames")
        await self.buff(6,10,effect_dict,'fire weapon',flavor_template,duration,target,True)
    fire_weapon = asyncReporterMethod(fire_weapon, '''level 6\nmana cost 10\nfire in a bottle has enchanted many scientists and sorcerers
                                    \nfire in a bottle on poured on a weapon is the crazy only a rogue would do
                                    \nsyntax: "fire" or "fire *target*"''')
    #cripple spell, nuke and debuff base, damage based on attack, debuff based on int and agi, duration based on int and agi, reduces attack value
    async def cripple(self, target = None):
        damage = randint(20,40) + self.vitals_getter('attack value')
        damage_type = self.vitals_getter('damage type')
        amount = randint(0, 10) + (self.stats_getter('int') * 2) + (self.stats_getter('agi') * 2)
        effect_dict = {'attack value': -amount}
        duration = (self.stats_getter('int') + self.stats_getter('agi')) * 5
        flavor_template = Template('you string at $name joints, crippling their attacks')
        await self.nuke_n_debuff(7,25,damage,damage_type,'cripple',effect_dict,duration,flavor_template,target,True)
    cripple = asyncReporterMethod(cripple, '''level 7\nmana cost 25\njoints are suprisingly delicate things
                                  \nwarriors honor doesn't apply to rogues so attack to elbows, wrists, and shoulders are encuraged
                                  \nsyntax: "cripple" or "cripple *target*"''')
    # bandage wounds spell, heal base, heals half of missing health
    async def bandage_wounds(self, target = None):
        amount = round((self.vitals_getter('health max') - self.vitals_getter('health')) / 2)
        flavor_template =Template('you carefully bandage some of $name wounds')
        await self.heal(8,20,amount,'health',flavor_template,target,True)
    bandage_wounds = asyncReporterMethod(bandage_wounds, '''level 8\nmana cost 20\nif life healing is just as important as fighting
as such a rogue is practiced in using bandages and dressing wounds\nsyntax: "bandage" or "bandage target"''')
    # counter attack ability, buff base, duration based on int and agi, counter attack incoming attacks
    #COUNTER ATTACK ONLY WORKS ON SELF VIA DEFAULT TARGET HENCE THE LOGIC CHECK
    async def counter_attack(self,target = None):
        if target != None:
            print('you cannot make someone else counterattack')
            return
        effect_dict = {'counter attack': 'active'}
        duration = (self.stats_getter('int') + self.stats_getter('agi')) * 12
        flavor_template = Template('you become tense and alert ready to counter attack incoming blows')
        await self.buff(9,40,effect_dict,'counter attack',flavor_template,duration,target)
    counter_attack = asyncReporterMethod(counter_attack, '''level 9\nmana cost 40\ngetting hit is part of life
make hitting back an even greater part\nsyntax: "counter"''')
    # lightweight spell, buff base, amount based on current encumbrance, duration based on int and agi, increases attack and defense
    #LIGHTWEIGHT SHOULD ONLY EFFECT THE PLAYER, HENCE THE EXTRA LOGIC CHECK
    async def light_weight(self, target = None):
        if target != None:
            print('you cannot use this ability on anything but yourself')
        amount = self.vitals_getter('load max') - self.vitals_getter('load')
        effect_dict = {'attack value': amount, 'defense value': amount}
        duration = (self.stats_getter('int') + self.stats_getter('agi')) * 15
        flavor_template = Template('your light load helps you, but attack and defened')
        await self.buff(10,50,effect_dict,'light weight', flavor_template, duration,target)
    light_weight = asyncReporterMethod(light_weight, '''level 10\nmana cost 50\nto be effective in combat one must be light on thier feet
rogues take that to the extreme and gain extra damage and defense based on how light thier load is\nsyntax: "lightweight"''')