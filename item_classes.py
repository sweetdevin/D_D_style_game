#items class
class item_class():
    def __init__(self, name, text, stat = None, effect = None):
        self.name = name
        self.text = text
        self.stat = stat
        self.effect = effect
        self.player = None
    def __repr__(self) -> str:
        return self.name
    # link to player function
    def player_link(self, player):
        self.player = player
    def player_remove(self):
        self.player=None
# equipment subclass
class equipment(item_class):
    def __init__(self, name, text, stat=None, effect=None):
        super().__init__(name, text, stat, effect)
    def use(self):
        self.player.set_active(self.stat, self.effect)   
# consumable subclass 
class consumable(item_class):
    def __init__(self, name, text, stat=None, effect=None):
        super().__init__(name, text, stat, effect) 
    def use(self):
        self.player.get_n_set(self.stat, self.effect)
        print(f'plus {self.effect} to {self.stat}')
        print(f'{self.name} used')
# item subclass container
class container(item_class):
    def __init__(self, name, text):
        super().__init__(name, text)
        self.contents = []
    def add_items(self, item_obj):
        self.contents.append(item_obj)
class fountain(item_class):
    def __init__(self, name, text, stat=None, effect=None):
        super().__init__(name, text, stat, effect)
    def drink(self, player):
        self.player_link(player)
        player.get_n_set('mana', player.vitals_getter('mana max'))
        player.get_n_set('health', player.vitals_getter('health max'))
        self.player_remove()
        print('you are fully healed')