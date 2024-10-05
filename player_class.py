from class_test import creature 
from rooms import roomnode
from rooms import spawnnode
class player(creature):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.location = spawnnode
        
    def traverse(self, direction):
        next_node = self.location.exits[direction]
        if next_node:
            self.location = next_node
            self.look()
        else: return 'cannot travel that way'
    def look(self):
        print(self.location.description)
        exits = [x for x in self.location.exits.keys()]
        print(f'obvious exits are {exits}')
        print('this room contains')
        if self.location.creatures:
            for x in self.location.creatures:
                print(x)
        else: print('nothing')
dev = player('dev')

dev.look()
dev.traverse('east')
dev.traverse('gates')