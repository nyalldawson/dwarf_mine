from typing import List
import random
from allegiance import Allegiance


class Tribe:

    def __init__(self, id):
        self.id = id
        self.color = None
        self.leader_color = None
        self.name = ''
        self.min_x = 0
        self.max_x = 0

    def populate(self, population: int) -> List['Creatures']:
        res = []

        # every tribe has a king
        king_x = random.randint(self.min_x, self.max_x)
        from creatures import DwarfKing
        king = DwarfKing(king_x, 0, tribe=self)
        king.color = self.leader_color
        res.append(king)

        for p in range(population-1):
            x = random.randint(self.min_x, self.max_x)
            creature = self.create_creature(x=x, y=0, tribe=self)
            self.apply_traits_to_character(creature)
            res.append(creature)

        return res

    def create_creature(self, **kwargs):
        from creatures import Miner
        return Miner(**kwargs)

    def allegiance_to(self, tribe):
        if tribe == self:
            return Allegiance.Friendly
        else:
            return Allegiance.Hostile

    def apply_traits_to_character(self, character: 'Character'):
        """
        Applies the tribe's traits to a character
        """

class Builders(Tribe):
    """
    A tribe of builders, good at digging
    """
    def __init__(self, id):
        super().__init__(id)
        self.name = 'Builders'

    def apply_traits_to_character(self, character: 'Character'):
        from creatures import Miner
        from traits import Determined
        if isinstance(character, Miner):
            character.traits.append(Determined(10))


class Rangers(Tribe):
    """
    A tribe of ranges, work with animals
    """
    def __init__(self, id):
        super().__init__(id)
        self.name = 'Rangers'

    def create_creature(self, **kwargs):
        from creatures import Miner, Snake
        from actions import ExploreAction
        from traits import Contagious

        creature= random.choice([Miner, Snake])(**kwargs)
        if isinstance(creature, Snake):
            creature.default_action = ExploreAction()
            creature.push_action(ExploreAction())
            if creature.has_trait(Contagious):
                creature.color = self.leader_color
            else:
                creature.color = self.color

        return creature

TRIBE_CLASSES = [Tribe, Builders, Rangers]