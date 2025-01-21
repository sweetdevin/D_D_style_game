import class_test
import item_classes
import copy
import asyncio
import re
#opposites direction dictionary needed for linking nodes via add exit method
opposites = {'gates': 'gates', 'up' : 'down', 'down':'up', 'east':'west', "west":'east',
             'north':'south', 'south':'north', 'enter':'out', 'out':'enter'}
# regex exits dictionary
regex_exits_dict = {'east': r'^e(a(s(t)?)?)?$', 'west': r'^w(e(s(t)?)?)?$', 'north':r'^n(o(r(t(h)?)?)?)?$',
                    'south':r'^s(o(u(t(h)?)?)?)?$', 'gates': r'^g(a(t(e(s)?)?)?)?$', 'up':r'up?$', 'down':r'd(o(w(n)?)?)?$',
                    'enter': r'^en(t(e(r)?)?)?$', 'out': r'^o(u(t)?)?$'}
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
        self.gold = 0
    #reswpan the room
    async def respawn(self):
        #check is respawn already triggered if so return
        if self.respawn_triggered == True:
            return
        # if respawn not already triggered, trigger respawn and wait 5 mins
        #SET TO 5 MINS FOR DEVELOPMENT PURPOSES IN ACTUAL GAMEPLAY WAIT TIME WOULD BE LONGER
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
    # a get exits function, returns a list of visible exits
    def get_exits(self):
        return [x for x in self.exits.keys()]
    #add object to room contents at start of game. spawn items respawn. items added via add_item do not respawn
    def add_spawn_item(self, obj):
        self.spawn_contents.append(obj)
        self.add_item(obj)
    #add contents throughout game, items added with this method will not respawn
    def add_item(self, item_class):
        self.contents.append(item_class)
    #remove object from room
    def remove_item(self, item_key):
        self.contents.remove(item_key)
    #add gold
    def add_gold(self, num):
        self.gold += num
    #subtract gold
    def sub_gold(self, num):
        self.gold -= num
    #return gold
    def return_gold(self):
        return self.gold
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
        # item class obj should have already been validated by search.
        # if item not in hidden it has already been found, print and return
        try:
            index = self.hidden.index(item_class)
        except ValueError:
            print('that has already been searched')
            return
        # if item was in hidden remove from hidden
        item_obj = self.hidden.pop(index)
        #start respawn timer
        asyncio.create_task(self.respawn())
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
#creating a store subclass of room
class store(roomnode):
    def __init__(self, description):
        super().__init__(description)
        self.stock = []
    # add stock
    def add_stock(self, item_obj):
        self.stock.append(item_obj)
    # remove stock
    def remove_stock(self, item_obj):
        self.stock.remove(item_obj)
    #view stock
    def view(self, player):
        print('the shop has the following items for sale')
        printed = []
        for item in self.stock:
            if item in printed:
                continue
            else:
                print(f'{item} for {item.return_store_price()}')
                printed.append(item)
        print(f'your current gold : {player.gold}')

#build rooms, linking rooms, adding objects, adding methods
#looking to build efficiency I should make adding items and adding stock use *args. same way I did with NPCS for adding items and equiping item
tower_g_text = '''you stand at the gates outside of a small tower. the wrought iron gates are engraved 
with rats all up and down the sides, with one large rat on the top. On one side of the gates there is 
a trashcan, on the other there is a pile of sticks. Further east there is another larger tower'''
tower_g =roomnode(tower_g_text)
tower_g.add_spawn_item(item_classes.potion_of_experience)
tower_g.add_spawn_item(class_test.rat)
tower_g.add_spawn_hidden(class_test.health_potion)
tower_g.add_search(r'^pile', class_test.health_potion)
tower_g.add_search(r'^trashcan', 'nothing of value, just trash')
tower_1_text = """you stand on the ground floor of a large stone tower.
There is a small lockbox by the door, and a wooden desk in the middle of the room"""
tower_1 = roomnode(tower_1_text)
tower_1.add_spawn_item(copy.copy(class_test.rat))
tower_1.add_spawn_item(item_classes.sm_box_01)
tower_1.add_spawn_hidden(item_classes.sm_key_01)
tower_1.add_search(r'^desk', item_classes.sm_key_01)
tower_2_text = 'you stand on the second floor of a large stone tower'
tower_2 = roomnode(tower_2_text)
tower_2.add_spawn_item(copy.copy(class_test.rat))
tower_3_text = '''you stand on the top floor of a large tower with large rats.
a large painting hangs slightly crooked on the wall.'''
tower_3 = roomnode(tower_3_text)
tower_3.add_spawn_item(copy.copy(class_test.rat))
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
spawnnode.add_spawn_item(class_test.health_potion)
swamp_west = roomnode('the swampland splits here with passages going both north and south')
swamp_west_1 = roomnode('an alter in the middle of the swamp')
swamp_west.add_spawn_item(item_classes.west_door)
spawnnode.add_exits(swamp_west, 'west')
swamp_west.add_exits(swamp_west_1, 'west')
swamp_north_1_text = '''a large winding swamp with small stick and mud dwellings
the beginning of the snagletooth village'''
swamp_north_1 = roomnode(swamp_north_1_text)
swamp_north_1.add_spawn_item(class_test.young_murlock)
swamp_north_1.add_exits(swamp_west, 'south')
swamp_north_2 = roomnode('''you are on a winding path through the snaggletooth village. small dwellings made of mud, 
sticks, bone, and hide line your path. Many smaller murlocks run and hide when you approach''')
swamp_north_2.add_spawn_item(copy.copy(class_test.young_murlock))
swamp_north_1.add_exits(swamp_north_2, 'west')
swamp_north_3 = roomnode('''You are on a winding path through the snagletooth village. The dwellings look larger here 
and more sophisticated. Windows, doors, and chimneys are now present. The surrounding murlocks seem bigger and older,
more pronounced in their features.''')
swamp_north_3.add_spawn_item(class_test.snagletooth)
swamp_north_2.add_exits(swamp_north_3, 'north')
swamp_north_4 =roomnode('''You are on a winding path through the snagletooth village. The dwellings look larger here 
and more sophisticated. Windows, doors, and chimneys are now present. The surrounding murlocks seem bigger and older,
more pronounced in their features. To the north seems to be the end of the village with a longhouse.''')
swamp_north_4.add_spawn_item(copy.copy(class_test.snagletooth))
swamp_north_3.add_exits(swamp_north_4, 'east')
swamp_north_5 = roomnode('''You stand in front of a longhouse at the end of the snagletooth village. Older murlocks watch you 
wearily from their dwellings. The longhouse is made of wood and earth a solid structure looking like an overturned boat.''')
swamp_north_5.add_spawn_item(class_test.murlock_guard)
swamp_north_4.add_exits(swamp_north_5, 'north')
swamp_north_6 = roomnode('''You stand inside the longhouse. A large fire burns in the middle of the room and several 
hanging pyres shed light around the room. At one end of the longhouse is a ornamented chair used as a throne.''')
swamp_north_6.add_spawn_item(class_test.snagletoooth_cheif)
swamp_north_5.add_exits(swamp_north_6,'enter')
swamp_south_1_text = '''a large swamp with small stick and mud dwelling
this is the beginning of the dreadclaw village'''
swamp_south_1 = roomnode(swamp_south_1_text)
swamp_south_1.add_exits(swamp_west, 'north')
swamp_south_1.add_spawn_item(copy.copy(class_test.young_murlock))
swamp_south_2 = roomnode('''you are on a winding path through the dreadclaw village. small dwellings made of mud, 
sticks, bone, and hide line your path. Many smaller murlocks run and hide when you approach''')
swamp_south_2.add_spawn_item(copy.copy(class_test.young_murlock))
swamp_south_1.add_exits(swamp_south_2,'west')
swamp_south_3 = roomnode('''You are on a winding path through the dreadclaw village. The dwellings look larger here 
and more sophisticated. Windows, doors, and chimneys are now present. The surrounding murlocks seem bigger and older,
more pronounced in their features.''')
swamp_south_3.add_spawn_item(class_test.dreadclaw)
swamp_south_2.add_exits(swamp_south_3, 'south')
swamp_south_4 = roomnode('''You are on a winding path through the dreadclaw village. The dwellings look larger here 
and more sophisticated. Windows, doors, and chimneys are now present. The surrounding murlocks seem bigger and older,
more pronounced in their features. To the north seems to be the end of the village with a longhouse.''')
swamp_south_4.add_spawn_item(copy.copy(class_test.dreadclaw))
swamp_south_3.add_exits(swamp_south_4, 'east')
swamp_south_5 = roomnode('''You stand in front of a longhouse at the end of the dreadclaw village. Older murlocks watch you 
wearily from their dwellings. The longhouse is made of wood and earth a solid structure looking like an overturned boat.''')
swamp_south_5.add_spawn_item(copy.copy(class_test.murlock_guard))
swamp_south_4.add_exits(swamp_south_5,'south')
swamp_south_6 =roomnode('''You stand inside the longhouse. A large fire burns in the middle of the room and several 
hanging pyres shed light around the room. At one end of the longhouse is a ornamented chair used as a throne.''')
swamp_south_6.add_spawn_item(class_test.dreadclaw_chief)
swamp_south_5.add_exits(swamp_south_6, 'enter')


restore_fountain = item_classes.fountain('fountain of healing', 'a small stone fountain')
restore_fountain.set_regex(r'^((small )?stone )?fountain$')
spawnnode.add_spawn_item(restore_fountain)
spawnnode.add_method('drink', restore_fountain.drink)
spawnnode.add_spawn_item(item_classes.save_point)
spawnnode.add_method('save', item_classes.save_point.save)
shop_text = '''A large stone building with lots of wooded shelves and a large counter. Behind the
counter a large shopkeeper tends the store. This must be a store where you can 'buy' and 'sell' items.
you can also 'view' the stock the store has for sale'''
tower_shop = store(shop_text)
tower_shop.add_method('view', tower_shop.view)
tower_shop.add_stock(item_classes.sword_of_despair)
tower_shop.add_stock(class_test.health_potion)
tower_shop.add_stock(class_test.ring_of_health)
tower_shop.add_stock(item_classes.helm_of_atk)
tower_1.add_exits(tower_shop, 'enter')
farm_1_text = '''a narrow rode leading to a small farmhouse. There is a low wooden fence framing the road
to keep the livestock contained. To the east appears to be sheep pasture, to the west appears to be cows. The barn 
and farmhouse are further to the north'''
farm_1 = roomnode(farm_1_text)
spawnnode.add_exits(farm_1, 'north')
farm_1.add_spawn_item(class_test.farm_boy)
sheep_pasture_1 = roomnode('you stand in the sheep pasture among the grass, flowers, and sheep droppings')
farm_1.add_exits(sheep_pasture_1, 'east')
sheep_pasture_1.add_spawn_item(class_test.sheep)
sheep_pasture_2 = roomnode('the pasture ends here with a stone fence seperating the sheep from a thick forest')
sheep_pasture_1.add_exits(sheep_pasture_2,'north')
sheep_pasture_2.add_spawn_item(copy.copy(class_test.sheep))
cow_pasture_1 = roomnode('you stand in the cow pasture, lots of cow droppings and flies. the pasture continues north toward the barn')
farm_1.add_exits(cow_pasture_1,'west')
cow_pasture_1.add_spawn_item(class_test.cow)
cow_pasture_2 = roomnode('you are at the end of the cow pasture right before the entrance of the barn')
cow_pasture_1.add_exits(cow_pasture_2,'north')
cow_pasture_2.add_spawn_item(class_test.bull)
barn_1 = roomnode('''you stand in the barn at the farm. It is simple inside just some stables, a hay loft, milking stall, 
and some farm tools on the wall. you can exit to the pasture, road, or hayloft''')
barn_1.add_spawn_item(class_test.farmer)
barn_2 = roomnode('you stand in the hayloft of the barn, there is a lot of hay up here. hense the name hay loft')
barn_2.add_spawn_item(copy.copy(class_test.farmer))
barn_1.add_exits(barn_2, 'up')
cow_pasture_2.add_exits(barn_1, 'north')
farm_2_text = '''the road ends here between the barn and the farmhouse'''
farm_2 = roomnode(farm_2_text)
farm_2.add_exits(barn_1, 'west')
farm_1.add_exits(farm_2, 'north')
farm_2.add_spawn_item(copy.copy(class_test.farm_boy))
farm_house_1 = roomnode('''you stand in the farmhouse, there is a large table for meals and several chairs by the fire place. 
you can smell something wonderful cooking in the kitchen, stairs lead to what you can guess is the sleeping area.''')
farm_house_1.add_spawn_item(class_test.farm_wife)
farm_2.add_exits(farm_house_1, 'east')
farm_house_2 =roomnode('''you are in the sleeping area in the farm house. not really seperate rooms, more like one large loft 
broken up by beds, dressers, chests, and wardrobes. the only exit is back down''')
farm_house_1.add_exits(farm_house_2, 'up')
farm_house_2.add_spawn_item(copy.copy(class_test.farm_wife))
dev_room = roomnode("the secret developers room. have fun")
spawnnode.add_exits(dev_room, 'south')
dev_room.add_spawn_item(class_test.health_potion)
dev_room.add_spawn_item(class_test.health_potion)
dev_room.add_spawn_item(item_classes.potion_of_experience)
dev_room.add_spawn_item(item_classes.potion_of_experience)
dev_room.add_spawn_item(item_classes.sorc_chest)
dev_room.add_spawn_item(item_classes.mana_potion)
dev_room.add_spawn_item(item_classes.mana_potion)
dev_room.add_spawn_item(item_classes.rogue_chest)
dragon_tower_entry = roomnode('''You stand before a tall stone tower it has to be at least ten stories high. You can hear the occasional 
roar or growl coming from the tower. Looking through the windows you can occasionally catch a glimps of scaley skin 
or horns moving around inside.''')
tower_g.add_exits(dragon_tower_entry, 'east')
dragon_tower_1 = roomnode('''you are on the first floor of the tower of dragons. The floor is just open with no furniture, there is  
a beautiful seascape painted on one wall and there appears to be sand on the floor. who puts sand on the floor? 
there is a staircase running up the exterior wall. across from the entrance there is a large wooden post with 
shackles firmly bolted to the floor and blood stains all around''')
dragon_tower_entry.add_exits(dragon_tower_1, 'enter')
dragon_tower_1.add_spawn_item(class_test.piff_dragon)
dragon_tower_2 = roomnode('''you are on the second floor of the tower of dragons. This floor is cluttered with broken mirrors 
and painting of black cats, there are ladders leaning on most walls with upside down horses nailed everywhere. 
nearby the stairs there is table full of claws and bite marks it reeks of blood and decay.''')
dragon_tower_1.add_exits(dragon_tower_2, 'up')
dragon_tower_2.add_spawn_item(class_test.kalfor_dragon)
dragon_tower_3 = roomnode('''you are on the third floor of the tower of dragons. This floor is filled with broken furniture. chairs, 
tables, stools, chests, beds anything it's all smashed. this dragon seems to have a rage issue. the walls a covered with blood stains 
and scorch marks this place seems very unfriendly, the stairs continue up and down''')
dragon_tower_2.add_exits(dragon_tower_3, 'up')
dragon_tower_3.add_spawn_item(class_test.dortrog_dragon)
dragon_tower_4 = roomnode('''you are on the fouth floor of the tower of dragons. This floor has many carved stone glyphs and markers
there are pots growing plants that resemble bamboo, which is used to makes several tables and benches seen throughout the room.
the stairs continue both up and down''')
dragon_tower_3.add_exits(dragon_tower_4, 'up')
dragon_tower_4.add_spawn_item(class_test.mushy_dragon)
dragon_tower_5 = roomnode('''you are on the fifth floor of the tower of dragons. This floor is suprisingly happy, sun shines through the window
there are sheep in some pens eating grass and fun blocks that a happy young dragon could jump and climb. The stair continue up and down''')
dragon_tower_4.add_exits(dragon_tower_5, 'up')
dragon_tower_5.add_spawn_item(class_test.spiral_dragon)
dragon_tower_6 = roomnode('''you are on the sixth floor of the tower of dragons. This floor is bare and tiled like an arena made for fighting.
there is a logo in the middle of the floor, it's hard to tell while also standing on the floor but it appears to be a circle with half 
red and half white with a black line through the middle leading to a small outline a small white inner circle. The stairs continue up 
and down.''')
dragon_tower_5.add_exits(dragon_tower_6,'up')
dragon_tower_6.add_spawn_item(class_test.scorchard_dragon)
dragon_tower_7 =roomnode('''you stand on the seventh floor of the tower of dragons. This floor has large boulder looking decorations and the
builders managed a small stream flowing through the middle of the room. the walls are painted with forest scenes. the fireplace on the 
wall resembles a campfire, with a spit for roasting meat. The stairs continue up and down.''')
dragon_tower_6.add_exits(dragon_tower_7, 'up')
dragon_tower_7.add_spawn_item(class_test.lizco_dragon)
dragon_tower_8 = roomnode('''you stand on the eighth floor of the tower of dragons. This floor is glowing with gold and gems a true dragons hoard
The walls are dim and stone like the inside of a mountain. The light in the room seems to eminate from the pile of gold itself. The 
stairs continue up and down''')
dragon_tower_7.add_exits(dragon_tower_8, 'up')
dragon_tower_8.add_spawn_item(class_test.lyttire_dragon)
dragon_tower_9 = roomnode('''you stand on the ninth floor of the tower of dragon. The heat in this room in immense, you're supprised the walls and
floor don't errupt into flames. piles of chared objects, ash, and soot cover the room. shards of volcanic glass litter the floor. there
is an altar before a large raised platform. This much be where the dragon takes it's meals. the stairs continue up and down.''')
dragon_tower_8.add_exits(dragon_tower_9, 'up')
dragon_tower_9.add_spawn_item(class_test.warwing_dragon)
dragon_tower_10 = roomnode('''you are on the tenth floor of the tower of dragons. This is the final floor and is styled more as a throne room
of a palace pillars reach up to the ceiling and the raised plateform for the dragon is padded. several tables full of offerings of 
meat, wine, and gold are placed in front of the platform''')
dragon_tower_9.add_exits(dragon_tower_10, 'up')
dragon_tower_10.add_spawn_item(class_test.muthaba_dragon)
