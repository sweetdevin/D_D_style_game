from class_test import creature 
from rooms import spawnnode
from random import randint
class player(creature):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.location = spawnnode
        self.basic_action = {'look' : self.look, 'travel': self.traverse,
                             'me': self.me, 'quit': self.quit, 'attack': self.enter_combat}
        self.health = 500
        self.active = False
        #fix this first tomorrow
        #self.attacks = self.attacks.update({'run': self.run,
        #                                    'calm': self.calm}) 
    #basic player specific commands
    # a travel function to move the play    
    def traverse(self):
        direction_list = [x for x in self.location.exits.keys()]
        print(direction_list)
        direction = input('which way? \n')
        if direction in direction_list:
            self.location = self.location.exits[direction]
            self.look()
            return
        else: print('cannot travel that way') 
        return self.traverse()
    # a simple look around or location command
    def look(self):
        print(self.location.description)
        exits = [x for x in self.location.exits.keys()]
        print(f'obvious exits are {exits}')
        print('this room contains')
        if self.location.creatures:
            for x in self.location.creatures:
                print(x)
        else: print('nothing')
    # an in game self status check
    def me(self):
        print(self)
    # an exit for the game loop
    def quit(self):
        self.active = False
        print('so long and thanks for all the fish')
    #combat target aquisition ends by calling combat loop
    def enter_combat(self):
        targets = [x for x in self.location.creatures.keys()]
        print(targets)
        target = input('attack what? \n')
        if target not in targets:
            print('that target does not exist here')
            return
        self.combat_loop(self.location.creatures[target])
    # the combat loop
    def combat_loop(self, target):
        attacks = [x for x in self.attacks.keys()]
        print(attacks)
        player_input = input('what action do you take? \n')
        if player_input in attacks:
           self.attacks[player_input](target)
        else:
            print(f'{self.name} is confused by your command and uses a basic attack')
            self.basic_attack(target)
        npc_attacks = [x for x in target.attacks.keys()]
        npc_index = randint(0, len(npc_attacks) -1)
        npc_attack = npc_attacks[npc_index]
        target.attacks[npc_attack](self)
        if target.health <= 0: 
            print(f'{self.name} is victorious')
            return
        if self.health <= 0:
            print(f'{self.name} has died')
            return
        return self.combat_loop(target)


# a basic play game loop
def play_game():
    play_name = input('what is your name? \n')
    character = player(play_name)
    character.active = True
    game_loop(character)
def game_loop(player):
    print(f'''you wake up suddenly in a new place and new time.
          with no memories of your past, only your name {player.name}''')
    player.look()
    while player.active == True:
        print('what action do you take?')
        actions = [x for x in player.basic_action.keys()]
        print(actions)
        user_action = input('')
        if user_action in actions:
            player.basic_action[user_action]()
        else: print('please select an action')

#proof of concept test functions
play_game()
