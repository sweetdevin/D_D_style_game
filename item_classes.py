import shelve
import asyncio
#items class bases class for all items
class item_class():
    def __init__(self, name, text, weight = 1):
        self.name = name
        self.text = text
        self.player = None
        self.regex = ''
        self.weight = weight
    def __repr__(self) -> str:
        return self.name
    # link to player function
    def player_link(self, player):
        self.player = player
    # remove player function
    def player_remove(self):
        self.player=None
    # set regex pattern for item
    def set_regex(self, regex_pattern):
        self.regex = regex_pattern
# equipment subclass
class equipment(item_class):
    def __init__(self, name, text, equipment_type, effect_dict):
        super().__init__(name, text)
        self.effect_dict = effect_dict
        self.equipment_type = equipment_type
    # use function, activates effect on player, equipment currently binds and uses on pickup
    #def use(self):
    #    self.player.set_active(self.name, self.effect_dict)   
# consumable subclass 
class consumable(item_class):
    def __init__(self, name, text, effect_dict):
        super().__init__(name, text)
        self.effect_dict = effect_dict 
    # a use function for consumables applies effect to player.
    def use(self):
        #add effect to player
        for key, value in self.effect_dict.items():
            self.player.get_n_set(key, value)
            print(f'{value} added to {key}')
        print(f'{self.name} used')
        # remove consumable from players inventory
        self.player.items.remove(self)
        self.player.load -= self.weight
# a door class
class door(item_class):
    def __init__(self, name, text, exit_string, keys_needed = 1):
        super().__init__(name, text)
        self.keys = []
        self.exit = exit_string
        self.keys_needed = keys_needed
    # an add key function
    def add_key(self, item_obj):
        # if has already been used been used print and return
        if item_obj in self.keys:
            print('that key has already been used')
            return
        # if key has not been used
        else:
            # add key to list of keys
            self.keys.append(item_obj)
            # if len of key list equal to or greater than keys_needed attribute 
            if len(self.keys) >= self.keys_needed:
                #print and remove exit from door. this should unblock to exit
                print(f'you unlock the {self.exit} door')
                self.exit = None        
# item subclass container
class container(item_class):
    def __init__(self, name, text, is_locked=False, keys_needed = 0):
        super().__init__(name, text)
        self.contents = []
        self.is_locked = is_locked
        self.keys =[]
        self.keys_needed = keys_needed
    # add items function, adds item objects to contents
    def add_items(self, item_obj):
        self.contents.append(item_obj)
    # add key function
    def add_key(self, item_obj):
        # if key has already been used print and return
        if item_obj in self.keys:
            print('that key has already been used')
            return
        # if key has not been uses
        else:
            # add key to list of keys
            self.keys.append(item_obj)
            # if list of keys equal to or greater than keys_needed attribute
            if len(self.keys) >= self.keys_needed:
                # call unlock function
                self.unlock()
    # unlock function
    def unlock(self):
        # change is locked attribute and print
        self.is_locked = False
        print(f'you unlock {self}')
    # locking function
    def lock(self):
        # set locked attribute to True. not intened for players to use. used when building
        self.is_locked = True
    # a decay method for corpses so they don't stack up
    async def decay(self, location):
        #replacement names for corpses 
        decay_names = ['a new corpse', 'a old corpse', 'a rotten corpse']
        count = 0
        # while corpse has decay names left
        while count < len(decay_names):
            #wait 30 seconds
            await asyncio.sleep(30)
            #assing new name to corpse
            self.name = decay_names[count]
            #advance count
            count += 1
        #when names have been exhausted drop all contents
        self.drop_contents(location)
        #remove corpse from room
        location.contents.remove(self)
    # drops all contents in the room, designed for corpses at end of thier decay
    def drop_contents(self, location):
        for obj in self.contents:
            location.add_item(obj)
# a healing fountain class
class fountain(item_class):
    def __init__(self, name, text):
        super().__init__(name, text)
    # a drink or use functions
    def drink(self, player):
        # links to player
        self.player_link(player)
        # set mana to max
        player.get_n_set('mana', player.vitals_getter('mana max'))
        # set health to max
        player.get_n_set('health', player.vitals_getter('health max'))
        # unlink from player
        self.player_remove()
        # print
        print('you are fully healed')
# a key class
class key(item_class):
    def __init__(self, name, text):
        super().__init__(name, text)
        self.linked_obj = None
    # key holds the link to whatever it opens
    def link_obj(self, target):
        # link item to key
        self.linked_obj = target
    # a use function for keys
    def use(self):
        # if the keys linked object is in the room
        if self.linked_obj in self.player.location.contents:
            # call linked objects add key function
            self.linked_obj.add_key(self)
            self.player.items.remove(self)
        # if linked object is not in the room, Print
        else:
            print("you can't use that key here")
# a save altar class
class save_altar(item_class):
    def __init__(self, name, text):
        super().__init__(name, text)
    # save player function
    def save(self, player):
        # saves player using shelve module
        # THIS SAVES MORE THAN I INTENDED. I MIGHT NEED TO MODIFY HOW I'M SAVING PLAYERS
        with shelve.open('player.db') as db:
            db[player.name] = player
# instancing obejects
sm_box_01 = container('small lockbox', 'a small lockbox for personal effects', True, 1)
sm_box_01.set_regex(r'^lock?box$')
sm_key_01 = key('a small key', 'a simple small brass key')
sm_key_01.set_regex(r'^(small )?key$')
sm_key_01.link_obj(sm_box_01)
sm_health_potion = consumable('health potion', 'a vial of red bubbly liquid', {'health':50})
sm_health_potion.set_regex(r'^(health|potion|health potion)$')
sm_box_01.add_items(sm_health_potion)
west_door = door('a large door to the west', 'a large door made of woven brances', 'west', 2)
west_door.set_regex(r'^(west )?door$')
west_door_key_green =key('green key', 'a key made of a strange green rock')
west_door_key_green.set_regex(r'^(green )?key$')
west_door_key_green.link_obj(west_door)
west_door_key_blue = key('a blue key', 'a key made of a strange blue rock')
west_door_key_blue.set_regex(r'^(blue )?key$')
west_door_key_blue.link_obj(west_door)
save_point = save_altar('a stange glowing altar', 'you sense this altar would "save" your current state')
save_point.set_regex(r'^(stange |glowing )?altar$')
helm_of_atk = equipment('helm of attack', 'a thin light helmet studded with gems', 'head', {'attack value':10})
helm_of_atk.set_regex(r'^helm(et)?( of attack)?')