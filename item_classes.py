import shelve
import asyncio
#items class
class item_class():
    def __init__(self, name, text):
        self.name = name
        self.text = text
        self.player = None
        self.regex = ''
    def __repr__(self) -> str:
        return self.name
    # link to player function
    def player_link(self, player):
        self.player = player
    def player_remove(self):
        self.player=None
    def set_regex(self, regex_pattern):
        self.regex = regex_pattern
# equipment subclass
class equipment(item_class):
    def __init__(self, name, text, stat=None, effect=None):
        super().__init__(name, text)
        self.stat = stat
        self.effect = effect
    def use(self):
        self.player.set_active(self.stat, self.effect)   
# consumable subclass 
class consumable(item_class):
    def __init__(self, name, text, stat=None, effect=None):
        super().__init__(name, text)
        self.stat = stat
        self.effect = effect 
    def use(self):
        self.player.get_n_set(self.stat, self.effect)
        print(f'plus {self.effect} to {self.stat}')
        print(f'{self.name} used')
class door(item_class):
    def __init__(self, name, text, exit_string, keys_needed = 1):
        super().__init__(name, text)
        self.keys = []
        self.exit = exit_string
        self.keys_needed = keys_needed
    def add_key(self, item_obj):
        if item_obj in self.keys:
            print('that key has already been used')
            return
        else:
            self.keys.append(item_obj)
            if len(self.keys) >= self.keys_needed:
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
    def add_items(self, item_obj):
        self.contents.append(item_obj)
    def add_key(self, item_obj):
        if item_obj in self.keys:
            print('that key has already been used')
            return
        else:
            self.keys.append(item_obj)
            if len(self.keys) >= self.keys_needed:
                self.unlock()
    def unlock(self):
        self.is_locked = False
        print(f'you unlock {self}')
    def lock(self):
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
class fountain(item_class):
    def __init__(self, name, text):
        super().__init__(name, text)
    def drink(self, player):
        self.player_link(player)
        player.get_n_set('mana', player.vitals_getter('mana max'))
        player.get_n_set('health', player.vitals_getter('health max'))
        self.player_remove()
        print('you are fully healed')
class key(item_class):
    def __init__(self, name, text):
        super().__init__(name, text)
        self.linked_obj = None
    def link_obj(self, target):
        self.linked_obj = target
    def use(self):
        if self.linked_obj in self.player.location.contents:
            self.linked_obj.add_key(self)
        else:
            print("you can't use that key here")
class save_altar(item_class):
    def __init__(self, name, text):
        super().__init__(name, text)
    def save(self, player):
        with shelve.open('player.db') as db:
            db[player.name] = player
# instancing obejects
sm_box_01 = container('small lockbox', 'a small lockbox for personal effects', True, 1)
sm_box_01.set_regex(r'^lock?box$')
sm_key_01 = key('a small key', 'a simple small brass key')
sm_key_01.set_regex(r'^(small )?key$')
sm_key_01.link_obj(sm_box_01)
sm_health_potion = consumable('health potion', 'a vial of red bubbly liquid', 'health', 50)
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