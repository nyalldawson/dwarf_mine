COLORS = [(206, 0),(209,0),(154,0),(142,0)]
class Tribe:

    def __init__(self, id):
        self.id = id
        self.color = COLORS[id]

        self.min_x = 0
        self.max_x = 0

