from class_test import creature, container, item_class
from rooms import spawnnode
from random import randint

class player(creature):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.location = spawnnode
        self.basic_action = {'look' : self.look, 'travel': self.traverse,
                             'me': self.me, 'quit': self.quit, 'attack': self.enter_combat,
                             'examine': self.examine, 'take': self.take_item,
                             'use': self.use}
        self.health = 500
        self.active = False
        self.in_combat = False
        self.attacks = self.attacks | {'run': self.run,
                                            'calm': self.calm}
        self.items = []
    #basic player specific commands
    # a travel function to move the play    
    def traverse(self):
        direction_list = [x for x in self.location.exits.keys()]
        print(direction_list)
        direction = input('which way? \n')
        if direction in direction_list:
            self.location = self.location.exits[direction]
            self.look()
            for value in self.location.creatures.values():
                if value.aggressive == True:
                    print(f'{value.name} attacks you')
                    self.in_combat = True
                    self.combat_loop(value)
            return
        else: print('cannot travel that way') 
    # a simple look around or location command
    def look(self):
        print(self.location.description)
        exits = [x for x in self.location.exits.keys()]
        print(f'obvious exits are {exits}')
        if self.location.creatures:
            for x in self.location.creatures:
                print(f'creature - {x}')
        else: print('no creatures')
        if self.location.items:
            for x in self.location.items:
                print(f'item - {x}')
        else: print('no items')        
    # an in game self status check
    def me(self):
        print(self)
        print(f'i am holding, {self.items}')
    # an exit for the game loop
    def quit(self):
        self.active = False
        print('so long and thanks for all the fish')
    #combat target aquisition ends by calling combat loop
    def enter_combat(self):
        #print targets
        targets = [x for x in self.location.creatures.keys()]
        if len(targets) == 0:
            print('there is nothing here to attack')
            return 
        print(targets)
        #select and validate targets
        target = input('attack what? \n')
        if target not in targets:
            print('that target does not exist here')
            return
        self.in_combat = True
        print(f'you attack {target}')
        self.combat_loop(self.location.creatures[target])
    # the combat loop
    def combat_loop(self, target):
        # turn target agressive
        target.aggressive = True
        if self.in_combat == False: 
            return
        #print attacks
        attacks = [x for x in self.attacks.keys()]
        print(attacks)
       #select, validate, and call attack 
        player_input = input('what action do you take? \n')
        if player_input in attacks:
           self.attacks[player_input](target)
        else:
            print(f'{self.name} is confused by your command and uses a basic attack')
            self.basic_attack(target)
        #still in combat check
        if self.in_combat == False:
            return
        #npc attack phase
        npc_attacks = [x for x in target.attacks.keys()]
        npc_index = randint(0, len(npc_attacks) -1)
        npc_attack = npc_attacks[npc_index]
        target.attacks[npc_attack](self)
        #health check
        if target.health <= 0: 
            print(f'{self.name} is victorious')
            self.in_combat = False
            target.aggressive = False
            corpse = container(f'corpse of {target.name}', 'a bloody mangled corpse')
            for item in target.items:
                corpse.add_items(item)
            self.location.remove_creature(target.name)
            self.location.add_item(corpse)
            return
        if self.health <= 0:
            print(f'{self.name} has died')
            self.in_combat = False
            target.aggressive = False
            return
        return self.combat_loop(target)
    # a run away command
    def run(self, target):
        self.in_combat = False
        self.traverse()
    # an end combat command
    def calm(self, target):
        chance = randint(0, 1)
        if chance == 0:
            print(f'{target.name} fails to calm down')
        if chance == 1:
            self.in_combat = False
            target.aggressive = False
            print(f'{target.name} calms down')
    # examine items and take items functions
    def examine(self):
        items = [x.name for x in self.location.items]
        print(items)
        item_to_examine = input('examine what?')
        if item_to_examine in items:
            index = [x.name for x in self.location.items].index(item_to_examine)
            item = self.location.items[index]
            print(item)
            print(item.text)
            if type(item) == container:
                print('contains')
                print([x.name for x in item.contents])
        else: print("that item isn't here")
    def take_item(self):
        names = [x.name for x in self.location.items if type(x) == item_class]
        print(names)
        item = input('take what? \n')
        if item in names:
            index = names.index(item)
            item_obj = self.location.items[index]
            self.location.items.remove(item_obj)
            self.items.append(item_obj)
            item_obj.player_link(self)
        else: print('item is not here')
    def use(self):
        consumables = [x for x in self.items if type(x) == item_class]
        if len(consumables) == 0:
            print('you have no items')
            return
        consumables_names = [x.name for x in consumables]
        print(consumables_names)
        choice = input('use what?')
        if choice in consumables_names:
            index = consumables_names.index(choice)
            item =self.items.pop(index)
            item.use()
        else: print("you don't have that item")
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
