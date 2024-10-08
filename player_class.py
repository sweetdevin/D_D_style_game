from class_test import creature 
from rooms import spawnnode

class player(creature):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.location = spawnnode
        self.basic_action = {'look' : self.look, 'travel': self.traverse,
                             'me': self.me, 'quit': self.quit, 'attack': self.enter_combat}
        self.health = 500
        self.active = False
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
    
    def enter_combat(self):
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
