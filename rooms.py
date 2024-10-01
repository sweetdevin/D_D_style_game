opposites = {'gates': 'gates', 'up' : 'down', 'down':'up'}
class roomnode:
    def __init__(self, description, creatures):
        self.description = description
        self.creatures = creatures
        self.exits = {}
    #def reverse(direction):
        #opposites = {'gates': 'gates', 'up' : 'down', 'down':'up'}
        #switched_direction = opposites[direction]
        #return switched_direction #
    def add_exits(self, linking_node, direction):
        self.exits[direction] = linking_node
        op_dir = opposites[direction]
        linking_node.exits[op_dir] = self
    def traverse(self, direction):
        next_node = self.exits[direction]
        if next_node:
            print(next_node.description)
            print(next_node.exits.keys)
        else: return 'cannot travel that way'
tower_g_text = 'you stand at the gates outside of a large tower'
tower_g =roomnode(tower_g_text, 'guard')
tower_1_text = "you stand on the ground floor of a large stone tower"
tower_1 = roomnode(tower_1_text, 'guard')
tower_2_text = 'you stand on the second floor of a large stone tower'
tower_2 = roomnode(tower_2_text, 'guard')

tower_g.add_exits(tower_1,'gates')
tower_1.add_exits(tower_2,'up')