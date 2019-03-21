from allegiance import Allegiance


class Tribe:

    def __init__(self, id):
        self.id = id
        self.color = None
        self.name = ''
        self.min_x = 0
        self.max_x = 0

    def allegiance_to(self, tribe):
        if tribe == self:
            return Allegiance.Friendly
        else:
            return Allegiance.Hostile
