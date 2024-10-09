from class_test import snagletooth
from class_test import dreadclaw
opposites = {'gates': 'gates', 'up' : 'down', 'down':'up', 'east':'west', "west":'east'}
class roomnode:
    def __init__(self, description):
        self.description = description
        self.creatures = {}
        self.exits = {}
   
    def add_exits(self, linking_node, direction):
        self.exits[direction] = linking_node
        op_dir = opposites[direction]
        linking_node.exits[op_dir] = self
    def add_creature(self, creature):
        self.creatures[creature.name] = creature
tower_g_text = 'you stand at the gates outside of a large tower'
tower_g =roomnode(tower_g_text)
tower_1_text = "you stand on the ground floor of a large stone tower"
tower_1 = roomnode(tower_1_text)
tower_1.add_creature(snagletooth)
tower_2_text = 'you stand on the second floor of a large stone tower'
tower_2 = roomnode(tower_2_text)
tower_2.add_creature(dreadclaw)
spawnnode_text = "a calm field with a large stone tower in the distance"
spawnnode = roomnode(spawnnode_text)
spawnnode.add_exits(tower_g, 'east')
spawnnode.add_creature(snagletooth)
tower_g.add_exits(tower_1,'gates')
tower_1.add_exits(tower_2,'up')

