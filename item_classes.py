import shelve
import asyncio
#items class bases class for all items
class item_class():
    def __init__(self, name, text, weight = 1, price = 10):
        self.name = name
        self.text = text
        self.player = None
        self.regex = ''
        self.weight = weight
        self.price = price
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
    # change item weight method
    def change_weight(self, new_weight):
        self.weight = new_weight
    # change item price method
    def change_price(self, new_price):
        self.price = new_price
    # item price getter
    def return_price(self):
        return self.price
    # store price getter
    def return_store_price(self):
        return self.price + round(self.price * .25)
    def weight_getter(self):
        return self.weight    
# equipment subclass
class equipment(item_class):
    def __init__(self, name, text, equipment_type, effect_dict):
        super().__init__(name, text)
        self.effect_dict = effect_dict
        self.equipment_type = equipment_type  
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
        self.player.get_n_set('load', self.weight_getter())
class exp_potion(item_class):
    def __init__(self, name, text, amount, weight=1, price=10,):
        super().__init__(name, text, weight, price)
        self.amount = amount
    def use(self):    
        self.player.gain_experience(self.amount)
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
        self.gold = 0
    # add items function, adds item objects to contents
    def add_items(self, item_obj):
        self.contents.append(item_obj)
    #return gold
    def return_gold(self):
        return self.gold
    #add gold
    def add_gold(self, num):
        self.gold += num
    #subtract gold
    def sub_gold(self, num):
        self.gold -= num

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
        location.add_gold(self.return_gold())
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
potion_of_experience = exp_potion('experience potion','a vial of yellow liquid', 10000 )
potion_of_experience.set_regex(r'^(experience|potion|experience potion)$')
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
helm_of_atk = equipment('helm of attack', 'a thin light helmet studded with gems', 'head', {'attack value':5})
helm_of_atk.set_regex(r'^helm(et)?( of attack)?')
helm_of_atk.change_weight(2)
helm_of_atk.change_price(25)
sword_of_despair = equipment('sword of despair', 'an evil looking curved sword', 'weapon', {'attack value':25})
sword_of_despair.set_regex(r'^sword( of despair)?')
sword_of_despair.change_weight(3)
sword_of_despair.change_price(150)
wooden_sword = equipment('wooden sword', 'a small toy wooden sword', 'weapon', {'attack value':3})
wooden_sword.set_regex(r'^(wooden )?sword$')
bubble_sword = equipment('bubble sword', 'a strange sword seemingly made of bubbles', 'weapon', {'attack value': 3, 'damage type': 'water'})
bubble_sword.set_regex(r'^(bubble )?sword$')
sorc_chest = container('a sorcerer\'s chest', 'a large chest filled with basic sorcerer gear')
sorc_chest.set_regex(r'^(sorcerer )?chest$')
sorc_helm = equipment('a magical circlet', 'a simple wire circlet with a large greyish blue stone', 'head', {'defense value': 5, 'mana max': 20})
sorc_helm.set_regex(r'^(magical )?circlet')
sorc_helm.change_weight(2)
sorc_chest.add_items(sorc_helm)
sorc_amulet = equipment('a blue amulet', 'an amulet for sorcerers', 'neck', {'defense value': 10})
sorc_amulet.set_regex(r'^(blue )?amulet')
sorc_chest.add_items(sorc_amulet)
sorc_shoulders = equipment('frilled epaulets', 'colorful epaulets with frills and embelishments', 'shoulders', {'defense value': 5})
sorc_shoulders.set_regex(r'^(frilled )?epaulets$')
sorc_chest.add_items(sorc_shoulders)
sorc_plate = equipment('embellished robes', 'an almost iridescent embellished robe','chest', {'defense value': 10})
sorc_plate.set_regex(r'^(embellished )?robes$')
sorc_plate.change_weight(3)
sorc_chest.add_items(sorc_plate)
sorc_cloak = equipment('a dark blue cloak', 'a thin dark blue cloak with white trim', 'back', {'defense value': 5})
sorc_cloak.set_regex(r'^((dark )?blue )?cloak$')
sorc_cloak.change_weight(2)
sorc_chest.add_items(sorc_cloak)
sorc_arms = equipment('cloth sleeves', 'color-shifting cloth sleeves', 'arms', {'defense value': 5})
sorc_arms.set_regex(r'(cloth )?sleeves$')
sorc_chest.add_items(sorc_arms)
sorc_gloves = equipment('black gloves', 'midnight black gloves', 'hands', {'defense value': 5})
sorc_gloves.set_regex(r'^(black )?gloves$')
sorc_chest.add_items(sorc_gloves)
sorc_ring = equipment('a bright blue ring', 'a gold right with a bright blue stone', 'finger', {'defense value': 10, 'mana max': 20})
sorc_ring.set_regex(r'^((bright )?blue )?ring$')
sorc_chest.add_items(sorc_ring)
sorc_belt=equipment('a jeweled belt', 'a think belt studded with many jewels', 'waist', {'defense value': 5})
sorc_belt.set_regex(r'^(jeweled )?belt$')
sorc_chest.add_items(sorc_belt)
sorc_leggings = equipment('cloth pants', 'light, loose, light_blue pants', 'legs', {'defense value': 5})
sorc_leggings.set_regex(r'^(cloth )?pants$')
sorc_leggings.change_weight(2)
sorc_chest.add_items(sorc_leggings)
sorc_boots = equipment('fancy slippers', 'fancy slippers with the toes curled up', 'feet', {'defense value': 5})
sorc_boots.set_regex(r'^(fancy )?slippers$')
sorc_boots.change_weight(2)
sorc_chest.add_items(sorc_boots)
sorc_staff = equipment('a sorcerers staff', 'a hard wooden staff with a charm at one end', 'weapon', {'attack value': 10, 'mana max': 20})
sorc_staff.set_regex(r'^(sorcerers )?staff$')
sorc_staff.change_weight(4)
sorc_staff.change_price(25)
sorc_chest.add_items(sorc_staff)
mana_potion = consumable('mana potion', 'a vial of shimmering liquid', {'mana': 30})
mana_potion.set_regex(r'^(mana )?potion$')