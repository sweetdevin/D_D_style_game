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
# equipment subclass
class equipment(item_class):
    def __init__(self, name, text, stat=None, effect=None):
        super().__init__(name, text, stat, effect)
    def use(self):
        if self.stat == 'health':
            self.player.health += self.effect
        elif self.stat == 'mana':
            self.player.mana += self.effect    
# consumable subclass
class consumable(equipment):
    def __init__(self, name, text, stat=None, effect=None):
        super().__init__(name, text, stat, effect) 
# item subclass container
class container(item_class):
    def __init__(self, name, text):
        super().__init__(name, text)
        self.contents = []
    def add_items(self, item_obj):
        self.contents.append(item_obj)