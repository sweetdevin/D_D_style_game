from class_test import snagletooth, health_potion, dreadclaw, rat, ring_of_health
from item_classes import fountain, sm_box_01, sm_key_01
import copy
#opposites direction dictionary needed for linking nodes via add exit method
opposites = {'gates': 'gates', 'up' : 'down', 'down':'up', 'east':'west', "west":'east',
             'north':'south', 'south':'north'}
#Roomnode class 
class roomnode:
    def __init__(self, description):
        self.description = description
        self.exits = {}
        self.hidden_exits = {}
        self.contents = []
        self.room_actions = {}
        self.hidden = []
        self.search = {}
    #add exit method links roomnodes together.
    def add_exits(self, linking_node, direction, hidden = False):
        op_dir = opposites[direction]
        if hidden == True:
            self.hidden_exits[direction]= linking_node
            linking_node.hidden_exits[op_dir] = self
            self.add_hidden(linking_node)
            linking_node.add_hidden(self)
        else:
            self.exits[direction] = linking_node
            linking_node.exits[op_dir] = self
    def get_exits(self):
        return [x for x in self.exits.keys()]
    #add object to room contents objects are item class objects and creature class objects
    def add_item(self, item_class):
        self.contents.append(item_class)
    #remove object from room
    def remove_item(self, item_key):
        self.contents.remove(item_key)
    #add method link to room methods
    def add_method(self, method_key, method_locations):
        self.room_actions[method_key] = method_locations
    #add hidden items to room
    def add_hidden(self, item_class):
        self.hidden.append(item_class)
    
    #move item from hidden to visable
    def discover(self, item_class):
        try:
            index = self.hidden.index(item_class)
        except ValueError:
            print('that has already been searched')
            return
        item_obj = self.hidden.pop(index)
        if type(item_obj) == roomnode:
            key_list = [k for k,v in self.hidden_exits.items() if v == item_obj]
            key = key_list[0]
            self.add_exits(item_obj, key)
            print(f'you found and exit {key}')
        else: 
            self.add_item(item_obj)
            print(f'you found {item_obj.name}')
    #add searchable targets to room
    def add_search(self, search_string, search_result):
        self.search[search_string] = search_result
#build rooms, linking rooms, adding objects, adding methods
tower_g_text = '''you stand at the gates outside of a large tower.
On one side of the gates there is a trashcan. On the other there is a pile of sticks'''
tower_g =roomnode(tower_g_text)
tower_g.add_item(rat)
tower_g.add_hidden(health_potion)
tower_g.add_search('pile', health_potion)
tower_g.add_search('trashcan', 'nothing of value, just trash')
tower_1_text = """you stand on the ground floor of a large stone tower.
There is a small lockbox by the door, and a wooden desk in the middle of the room"""
tower_1 = roomnode(tower_1_text)
tower_1.add_item(copy.copy(rat))
tower_1.add_item(sm_box_01)
tower_1.add_hidden(sm_key_01)
tower_1.add_search('desk', sm_key_01)
tower_2_text = 'you stand on the second floor of a large stone tower'
tower_2 = roomnode(tower_2_text)
tower_2.add_item(copy.copy(rat))
tower_3_text = '''you stand on the top floor of a large tower with large rats.
a large painting hangs slightly crooked on the wall.'''
tower_3 = roomnode(tower_3_text)
tower_3.add_item(copy.copy(rat))
tower_4_text = '''a small secret room at the parapit of the tower.
the view out the window is incredable. You can see a vast swamp 
with two small villages, a large mountain is beyond the swamp.
there is a chest at the far end of the room'''
tower_4 = roomnode(tower_4_text)
spawnnode_text = """a calm field with a large stone tower to the east.  
The calm fields turn to marshlands to the west. 
There is a large painted wood sign that reads 
'type "help" for a list of basic commands'"""
spawnnode = roomnode(spawnnode_text)
spawnnode.add_exits(tower_g, 'east')
tower_g.add_exits(tower_1,'gates')
tower_1.add_exits(tower_2,'up')
tower_2.add_exits(tower_3, 'up')
tower_3.add_exits(tower_4, 'up', True)
tower_3.add_hidden(tower_4)
tower_3.add_search('painting', tower_4)
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
spawnnode.add_method('drink', restore_fountain.drink)