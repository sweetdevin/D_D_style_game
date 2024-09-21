from random import randint
class creature:
    def __init__(self, name,) -> None:
        self.name = name
        self.noise = 'uggh'
        self.health = 100
        self.mana = 25
        self.atk_val = 10
        self.def_val = 10
    def __repr__(self):
        return f'name is {self.name} \n health = {self.health} \n mana = {self.mana}'

    def basic_attack(self, target):
        damage = (self.atk_val + randint(0, 20)) - target.def_val
        target.health -= damage
        print(f'{self.name} hit {target.name} with {self.weapon} for {damage} damage')
    def speak(self):
        return f"Hi, my name is {self.name}"
    
    def sound(self):
        return self.noise
    
class murlock(creature):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.noise = 'blugbluglbuglbug'
        self.weapon = 'claws'
    def speak(self):
        return f'blugblug {self.name} blugblug'
    def bubble_atk(self, target):
        damage = randint(0, 20) + 20
        target.health -= damage
        print(f'{self.name} launches bubbles at {target.name} for {damage} damage')
    
dreadclaw = murlock('dreadclaw')
snagletooth = murlock('snagletooth')

dreadclaw.basic_attack(snagletooth)
snagletooth.bubble_atk(dreadclaw)
print(snagletooth)
print(dreadclaw)