from class_test import snagletooth, health_potion, dreadclaw, rat
from item_classes import fountain
import copy
opposites = {'gates': 'gates', 'up' : 'down', 'down':'up', 'east':'west', "west":'east',
             'north':'south', 'south':'north'}
class roomnode:
    def __init__(self, description):
        self.description = description
        self.exits = {}
        self.contents = []
        self.room_actions = {}
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
tower_g.add_item(rat)
tower_1_text = "you stand on the ground floor of a large stone tower"
tower_1 = roomnode(tower_1_text)
tower_1.add_item(copy.copy(rat))
tower_2_text = 'you stand on the second floor of a large stone tower'
tower_2 = roomnode(tower_2_text)
tower_2.add_item(copy.copy(rat))
tower_3_text = 'you stand on the top floor of a large tower with large rats'
tower_3 = roomnode(tower_3_text)
tower_3.add_item(copy.copy(rat))
spawnnode_text = """a calm field with a large stone tower to the east.  
The calm fields turn to marshlands to the west. 
There is a large painted wood sign that reads 
'type "help" for a list of basic commands'"""
spawnnode = roomnode(spawnnode_text)
spawnnode.add_exits(tower_g, 'east')
tower_g.add_exits(tower_1,'gates')
tower_1.add_exits(tower_2,'up')
tower_2.add_exits(tower_3, 'up')
spawnnode.add_item(health_potion)
swamp_west = roomnode('the swampland splits here with passages going both north and south')
spawnnode.add_exits(swamp_west, 'west')
swamp_north_1_text = '''a large swamp with small stick and mud dwellings
the beginning of the snagletooth village'''
swamp_north_1 = roomnode(swamp_north_1_text)
swamp_north_1.add_item(snagletooth)
swamp_north_1.add_exits(swamp_west, 'south')
swamp_south_1_text = '''a large swamp with small stick and mud dwelling
this is the beginning of the dreadclaw village'''
swamp_south_1 = roomnode(swamp_south_1_text)
swamp_south_1.add_exits(swamp_west, 'north')
swamp_south_1.add_item(dreadclaw)
restore_fountain = fountain('fountain of healing', 'a small stone fountain')
spawnnode.add_item(restore_fountain)
spawnnode.room_actions['drink'] = restore_fountain.drink