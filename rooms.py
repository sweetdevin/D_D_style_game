from class_test import snagletooth, health_potion, dreadclaw, rat, ring_of_health
from item_classes import fountain, sm_box_01, sm_key_01, west_door, west_door_key_blue, west_door_key_green, save_point, helm_of_atk
import copy
import asyncio
import re
#opposites direction dictionary needed for linking nodes via add exit method
opposites = {'gates': 'gates', 'up' : 'down', 'down':'up', 'east':'west', "west":'east',
             'north':'south', 'south':'north'}
# regex exits dictionary
regex_exits_dict = {'east': r'^e(a(s(t)?)?)?$', 'west': r'^w(e(s(t)?)?)?$', 'north':r'^n(o(r(t(h)?)?)?)?$',
                    'south':r'^s(o(u(t(h)?)?)?)?$', 'gates': r'^g(a(t(e(s)?)?)?)?$', 'up':r'up?$', 'down':r'd(o(w(n)?)?)?$'}
#Roomnode class 
class roomnode:
    def __init__(self, description):
        self.description = description
        self.exits = {}
        self.hidden_exits = {}
        self.exits_regex = {}
        self.contents = []
        self.spawn_contents = []
        self.room_actions = {}
        self.hidden = []
        self.spawn_hidden = []
        self.search = {}
        self.respawn_triggered = False
    #reswpan the room
    async def reswpawn(self):
        #check is respawn already triggered if so return
        if self.respawn_triggered == True:
            return
        # if respawn not already triggered, trigger respawn and waith 5 mins
        self.respawn_triggered = True
        await asyncio.sleep(300)
        # if an exit in both hidden exits and visable exits, remove from visible exits, 
        #this should reset discovered exits
        for key in self.hidden_exits.keys():
            if key in self.exits.keys():
                self.remove_exit(key)
        # If obj in spawn contents but not in room contents add it to room contents,
        # this should reset visible contents
        for obj  in self.spawn_contents:
            if obj not in self.contents:
                self.add_item(obj)
        # if obj in spawn hidden but not in hidded add it to spawn hidden,
        # this should reset hidden objs, I remove hidden objs when discovered to track them, 
        #if i come with with another way to track discovered objects this will be superflous 
        for  obj in self.spawn_hidden:
            if obj not in self.hidden:
                self.add_hidden(obj)
        # ture respawn tiggered back to false 
        self.respawn_triggered = False 
    #add exit method links roomnodes together.
    def add_exits(self, linking_node, direction, hidden = False):
        # find opposite direction from opposite dict.
        op_dir = opposites[direction]
        # if room is hidden
        if hidden == True:
            # link node to self via hidden_exits dict. direction key, node value
            self.hidden_exits[direction]= linking_node
            # link self to node in opposite directions
            linking_node.hidden_exits[op_dir] = self
            # add node hidden list
            self.add_hidden(linking_node)
            # add self to linking node's hidden list
            linking_node.add_hidden(self)
        # if room is visible
        else:
            #THIS SEEMS INEFFICIENT REGEX DICT WITH DIRECTION AS VALUE SO I CAN USE 
            # VALUE AS A KEY IN THE EXITS DICT. COULD EXITS_REGEX LINK DIRECTLY TO ROOM NODES?
            # i RUN INTO A PROBELM WITH DISPLAYING MY OBVIOUS EXITS
            # link node to self via exits dict. direction key, node value
            self.exits[direction] = linking_node
            # pull direction regex from regex dict, compile regexg pattern.
            compiled_regex = re.compile(regex_exits_dict[direction])
            # use complied regex as dict key, value string direction
            self.exits_regex[compiled_regex] = direction
            # same thing but in reverse to make a doubley linked nodes
            linking_node.exits[op_dir] = self
            op_compiled_regex = re.compile(regex_exits_dict[op_dir])
            linking_node.exits_regex[op_compiled_regex] = op_dir
    # a remove exits function
    def remove_exit(self, key):
        self.exits.pop(key)
    # a get exits function returns a list of visible exits
    def get_exits(self):
        return [x for x in self.exits.keys()]
    #add object to room contents at spawn
    def add_spawn_item(self, obj):
        self.spawn_contents.append(obj)
        self.add_item(obj)
    #add contents throughout game
    def add_item(self, item_class):
        self.contents.append(item_class)
    #remove object from room
    def remove_item(self, item_key):
        self.contents.remove(item_key)
    #add method link to room methods
    def add_method(self, method_key, method_locations):
        self.room_actions[method_key] = method_locations
    #add spawn hidden
    def add_spawn_hidden(self, obj):
        self.spawn_hidden.append(obj)
        self.add_hidden(obj)
    #add hidden items to room
    def add_hidden(self, item_class):
        self.hidden.append(item_class)   
    #move item from hidden to visable
    def discover(self, item_class):
        # item class should have already been validated by search should be a none string object
        # if item not in hidden ithas already been found, print and return
        try:
            index = self.hidden.index(item_class)
        except ValueError:
            print('that has already been searched')
            return
        # if item was in hidden remove from hidden
        item_obj = self.hidden.pop(index)
        #start respawn timer
        asyncio.create_task(self.reswpawn())
        # if object was room
        if type(item_obj) == roomnode:
            #get key from hidden exits, key should be a direction string 
            key_list = [k for k,v in self.hidden_exits.items() if v == item_obj]
            key = key_list[0]
            #link nodes via add exits function, and prints
            self.add_exits(item_obj, key)
            print(f'you found an exit {key}')
        # if object not a roomnode
        else: 
            # add object to room, and print
            self.add_item(item_obj)
            print(f'you found {item_obj.name}')
    #add searchable targets to room, search string should be regex pattern, 
    # search result should be string or object
    def add_search(self, search_string, search_result):
        #  compile regex pattern
        compiled_str = re.compile(search_string)
        # use compiled regex as key in search dict.
        self.search[compiled_str] = search_result
#build rooms, linking rooms, adding objects, adding methods
tower_g_text = '''you stand at the gates outside of a large tower.
On one side of the gates there is a trashcan. On the other there is a pile of sticks'''
tower_g =roomnode(tower_g_text)
tower_g.add_spawn_item(rat)
tower_g.add_spawn_hidden(health_potion)
tower_g.add_search(r'^pile', health_potion)
tower_g.add_search(r'^trashcan', 'nothing of value, just trash')
tower_1_text = """you stand on the ground floor of a large stone tower.
There is a small lockbox by the door, and a wooden desk in the middle of the room"""
tower_1 = roomnode(tower_1_text)
tower_1.add_spawn_item(copy.copy(rat))
tower_1.add_spawn_item(sm_box_01)
tower_1.add_spawn_hidden(sm_key_01)
tower_1.add_search(r'^desk', sm_key_01)
tower_2_text = 'you stand on the second floor of a large stone tower'
tower_2 = roomnode(tower_2_text)
tower_2.add_spawn_item(copy.copy(rat))
tower_3_text = '''you stand on the top floor of a large tower with large rats.
a large painting hangs slightly crooked on the wall.'''
tower_3 = roomnode(tower_3_text)
tower_3.add_spawn_item(copy.copy(rat))
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
tower_3.add_spawn_hidden(tower_4)
tower_3.add_search(r'^painting', tower_4)
spawnnode.add_spawn_item(health_potion)
swamp_west = roomnode('the swampland splits here with passages going both north and south')
swamp_west_1 = roomnode('an alter in the middle of the swamp')
swamp_west.add_spawn_item(west_door)
swamp_west.add_spawn_item(helm_of_atk)
spawnnode.add_exits(swamp_west, 'west')
swamp_west.add_exits(swamp_west_1, 'west')
swamp_north_1_text = '''a large swamp with small stick and mud dwellings
the beginning of the snagletooth village'''
swamp_north_1 = roomnode(swamp_north_1_text)
snagletooth.add_item(west_door_key_blue)
swamp_north_1.add_spawn_item(snagletooth)
swamp_north_1.add_exits(swamp_west, 'south')
swamp_south_1_text = '''a large swamp with small stick and mud dwelling
this is the beginning of the dreadclaw village'''
swamp_south_1 = roomnode(swamp_south_1_text)
swamp_south_1.add_exits(swamp_west, 'north')
dreadclaw.add_item(west_door_key_green)
swamp_south_1.add_spawn_item(dreadclaw)
restore_fountain = fountain('fountain of healing', 'a small stone fountain')
restore_fountain.set_regex(r'^((small )?stone )?fountain$')
spawnnode.add_spawn_item(restore_fountain)
spawnnode.add_method('drink', restore_fountain.drink)
spawnnode.add_spawn_item(save_point)
spawnnode.add_method('save', save_point.save)