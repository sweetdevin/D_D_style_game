from random import randint
# initial living creature class all player and 
# npc will have this super class as of right now
class creature:
    def __init__(self, name,) -> None:
        self.name = name
        self.noise = 'uggh'
        self.health = 100
        self.mana = 0
        self.atk_val = 10
        self.def_val = 10
        self.weapon = 'body'
        self.attacks = {'basic attack': self.basic_attack}
        self.aggressive = False
    def __repr__(self):
        return f'name is {self.name} \n health = {self.health} \n mana = {self.mana}'
    #basic attack function
    def basic_attack(self, target):
        damage = (self.atk_val + randint(0, 20)) - target.def_val
        target.health -= damage
        print(f'{self.name} hit {target.name} with {self.weapon} for {damage} damage')
    def speak(self):
        return f"Hi, my name is {self.name}"
    #mana check to be used before all mana costing attacks, 
    #makes sure self has mana if it does not it performs basic attck
    def mana_check(self, target, cost):
        if self.mana < cost:
            print(f'{self.name} lacks the mind to perform this ability and does a basic attack')
            self.basic_attack(target)
            return False
        return True
    def sound(self):
        return self.noise
    #combat function engages an npc in combat collect input and calls attacks
    #repeats until someone's health reaches 0
    #stringed out while testing
    """def enter_combat(self):
        print(self.location.creatures)
        target = input('attack what?')
        if target not in self.location.creatures:
            print('that target does not exist here')
            return
        index = self.location.creatures.index(target)
        self.combat_loop(self.location.creatures[index])
    def combat_loop(self, target):
        attacks = [x for x in self.attacks.keys()]
        print(attacks)
        player_input = input('what action do you take? \n')
        if player_input in attacks:
           self.attacks[player_input](target)
        else:
            print(f'{self.name} is confused by your command and uses a basic attack')
            self.basic_attack(target)
        npc_attack = randint(0, len(target.attacks.keys()) -1)
        target.attacks[target.attacks.keys()[npc_attack]](self)
        if target.health <= 0: 
            print(f'{self.name} is victorious')
            return
        if self.health <= 0:
            print(f'{self.name} has died')
            return
        return self.combat_loop(target)
    """
#murlock subclass
class murlock(creature):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.noise = 'blugbluglbuglbug'
        self.weapon = 'claws'
        self.mana = 25
        self.attacks = {'basic attack': self.basic_attack, 
                        'bubble attack': self.bubble_atk}
    def speak(self):
        return f'blugblug {self.name} blugblug'
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
        self.noise = 'AAARRRGGGGHHHH!!!'
        self.weapon = 'club'
        self.mana = 15
        self.attacks = [self.basic_attack, self.leaping_smash]
        self.attacks_str = ['basic attack', 'leaping attack']
    #barbarian special attacks
    def leaping_smash(self, target, cost = 5):
        if self.mana_check(target, cost) == True:
            self.mana -= cost
            damage = randint(0, 20) + 35 
            target.health -= damage 
            print(f'{self.name} leaps into the air and smashes his club down on {target.name} for {damage} damage')

#testing code
dreadclaw = murlock('dreadclaw')
snagletooth = murlock('snagletooth')
hulk = barbarian('hulk')



#saving characters experiment
#import pickle


#with open('character_db_2.pkl', 'wb') as file:
#    pickle.dump(hulk, file)
#    pickle.dump(dreadclaw, file)


