from random import randint
from item_classes import consumable, equipment
# initial living creature class all player and 
# npc will have this super class as of right now
class creature:
    def __init__(self, name,) -> None:
        self.name = name
        self.health = 100
        self.mana = 0
        self.atk_val = 10
        self.def_val = 10
        self.weapon = 'body'
        self.attacks = {'basic attack': self.basic_attack}
        self.aggressive = False
        self.items = []
    def __repr__(self):
        return f'name is {self.name} \n health = {self.health} \n mana = {self.mana}'
    #basic attack function
    def basic_attack(self, target):
        damage = (self.atk_val + randint(0, 20)) - target.def_val
        target.health -= damage
        print(f'{self.name} hit {target.name} with {self.weapon} for {damage} damage')
    #mana check to be used before all mana costing attacks, 
    #makes sure self has mana if it does not it performs basic attck
    def mana_check(self, target, cost):
        if self.mana < cost:
            print(f'{self.name} lacks the mind to perform this ability and does a basic attack')
            self.basic_attack(target)
            return False
        return True
    # add_tiem function
    def add_item(self, item):
        self.items.append(item)
#murlock subclass
murlock_text = "A scaley frog-like humanoid walking upright with thin limbs and an enormous mouth."
class murlock(creature):
    def __init__(self, name, text) -> None:
        super().__init__(name)
        self.text = text
        self.weapon = 'claws'
        self.mana = 25
        self.attacks = {'basic attack': self.basic_attack, 
                        'bubble attack': self.bubble_atk}
    #murlocks special attack
    def bubble_atk(self, target, cost = 10):
        if self.mana_check(target, cost) == True:
            self.mana -= cost
            damage = randint(0, 20) + 20
            target.health -= damage
            print(f'{self.name} launches bubbles at {target.name} for {damage} damage')
# barbarian subclass
class barbarian(creature):
    def __init__(self, name,):
        super().__init__(name)
        self.health = 500
        self.weapon = 'club'
        self.mana = 15
        self.attacks = self.attacks | {'leaping smash':self.leaping_smash}
    #barbarian special attacks
    def leaping_smash(self, target, cost = 5):
        if self.mana_check(target, cost) == True:
            self.mana -= cost
            damage = randint(0, 20) + 35 
            target.health -= damage 
            print(f'{self.name} leaps into the air and smashes his club down on {target.name} for {damage} damage')

#testing code
dreadclaw = murlock('dreadclaw', murlock_text + " this murlock has massive claws.")
ring_of_health = equipment('ring of health', 'a glowing red ring', 'health', 300)
health_potion = consumable('health potion', 'a vial of a red bubbly liquid', 'health', 50)
dreadclaw.add_item(health_potion)
snagletooth = murlock('snagletooth', murlock_text + " This murlock has long snarly teeth.")
snagletooth.add_item(health_potion)
snagletooth.add_item(ring_of_health)
hulk = barbarian('hulk')



