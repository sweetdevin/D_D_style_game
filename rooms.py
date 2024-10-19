from class_test import snagletooth, health_potion
from class_test import dreadclaw
opposites = {'gates': 'gates', 'up' : 'down', 'down':'up', 'east':'west', "west":'east'}
class roomnode:
    def __init__(self, description):
        self.description = description
        self.exits = {}
        self.contents = []
    def add_exits(self, linking_node, direction):
        self.exits[direction] = linking_node
        op_dir = opposites[direction]
        linking_node.exits[op_dir] = self
    def add_item(self, item_class):
        self.contents.append(item_class)
    def remove_item(self, item_key):
        self.contents.remove(item_key)
tower_g_text = 'you stand at the gates outside of a large tower'
tower_g =roomnode(tower_g_text)
tower_1_text = "you stand on the ground floor of a large stone tower"
tower_1 = roomnode(tower_1_text)
tower_1.add_item(snagletooth)
tower_2_text = 'you stand on the second floor of a large stone tower'
tower_2 = roomnode(tower_2_text)
tower_2.add_item(dreadclaw)
spawnnode_text = """a calm field with a large stone tower to the east.  
The calm fields turn to marshlands to the west. 
There is a large painted wood sign that reads 
'type "help" for a list of basic commands'"""
spawnnode = roomnode(spawnnode_text)
spawnnode.add_exits(tower_g, 'east')
spawnnode.add_item(snagletooth)
tower_g.add_exits(tower_1,'gates')
tower_1.add_exits(tower_2,'up')
spawnnode.add_item(health_potion)
