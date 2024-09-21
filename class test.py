from random import randint
class creature:
    def __init__(self, name,) -> None:
        self.name = name
        self.noise = 'uggh'
        self.health = 100
        self.mana = 0
        self.atk_val = 10
        self.def_val = 10
        self.weapon = 'body'
        self.attacks = [self.basic_attack]
    def __repr__(self):
        return f'name is {self.name} \n health = {self.health} \n mana = {self.mana}'

    def basic_attack(self, target):
        damage = (self.atk_val + randint(0, 20)) - target.def_val
        target.health -= damage
        print(f'{self.name} hit {target.name} with {self.weapon} for {damage} damage')
    def speak(self):
        return f"Hi, my name is {self.name}"
    def mana_check(self, cost):
        if self.mana < cost:
            print('you lack the mind to perform this ability and falter')
            return False
        return True
    def sound(self):
        return self.noise
    def enter_combat(self, target):
        count = 0
        for x in self.attacks:
            print(f'{count} for {x} ')
        player_input = input('what do you do?')
        attack = self.attacks[int(player_input)]
        attack(target)
        npc_attack = target.attacks[randint(0, len(target.attacks))]
        npc_attack(self)
        if target.health <= 0: 
            print(f'{self.name} is victorious')
            return
        if self.health <= 0:
            print(f'{self.name} has died')
            return
        return self.enter_combat(target)
class murlock(creature):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.noise = 'blugbluglbuglbug'
        self.weapon = 'claws'
        self.mana = 25
        self.attacks = [self.basic_attack, self.bubble_atk]
    def speak(self):
        return f'blugblug {self.name} blugblug'
    def bubble_atk(self, target, cost = 10):
        if self.mana_check(cost) == True:
            self.mana -= 10
            damage = randint(0, 20) + 20
            target.health -= damage
            print(f'{self.name} launches bubbles at {target.name} for {damage} damage')

class barbarian(creature):
    def __init__(self, name,):
        super().__init__(name)
        self.health = 500
        self.noise = 'AAARRRGGGGHHHH!!!'
        self.weapon = 'club'
        self.mana = 15
        self.attacks = [self.basic_attack, self.leaping_smash]
    def leaping_smash(self, target, cost = 5):
        if self.mana_check(cost) == True:
            self.mana -= 5
            damage = randint(0, 20) + 35 
            target.health -= damage 
            print(f'{self.name} leaps into the air and smashes his club down on {target.name} for {damage} damage')

dreadclaw = murlock('dreadclaw')
snagletooth = murlock('snagletooth')
hulk = barbarian('hulk')
hulk.enter_combat(dreadclaw)