from allegiance import Allegiance


class Tribe:

    def __init__(self, id):
        self.id = id
        self.color = None
        self.name = ''
        self.min_x = 0
        self.max_x = 0

        self.creatures = []
        self.add_creature_types()

    def add_creature_types(self):
        from creatures import Miner, DwarfKing, Snake, Wizard

        self.creatures = [Miner, Snake]

    def allegiance_to(self, tribe):
        if tribe == self:
            return Allegiance.Friendly
        else:
            return Allegiance.Hostile
