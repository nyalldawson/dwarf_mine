
class Item:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.char = 'X'
        self.color = 1
        self.mine = None
        self.type = 'thing'

    def add_to_mine(self, mine):
        self.mine = mine

    def is_attractive_to(self, creature: 'Creature'):
        return False

    def found_by(self, creature: 'Creature'):
        pass

    def alter_color(self):
        return None