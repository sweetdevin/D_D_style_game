from class_test import creature 
from rooms import roomnode
from rooms import spawnnode

class player(creature):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.location = spawnnode
        self.basic_action = {'look' : self.look, 'travel': self.traverse,
                             'me': self.me, 'quit': self.quit}
        self.active = False
    #basic player specific commands
    # a travel function to move the play    
    def traverse(self):
        direction_list = [x for x in self.location.exits.keys()]
        print(direction_list)
        direction = input('which way? \n')
        next_node = self.location.exits[direction]
        if next_node:
            self.location = next_node
            self.look()
        else: return 'cannot travel that way'
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
        print('what action do you that?')
        actions = [x for x in player.basic_action.keys()]
        print(actions)
        user_action = input('')
        if player.basic_action[user_action]:
            player.basic_action[user_action]()
        else: print('please select an action')

#proof of concept test functions
play_game()
