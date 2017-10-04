import random

class Trait:
    """
    A creature character trait
    """
    def __init__(self):
        self.type = ''

    def affect_visibility(self, visible):
        return visible


class Determined(Trait):
    """
    Creature is determined, and more likely to succeed or die trying
    """
    def __init__(self):
        Trait.__init__(self)
        self.type = 'determined'


class Lazy(Trait):
    """
    Creature is lazy, less likely to push themselves and more sleepy
    """
    def __init__(self):
        Trait.__init__(self)
        self.type = 'lazy'


class Sneaky(Trait):
    """
    Creature is sneaky, less likely to be seen
    """
    def __init__(self):
        Trait.__init__(self)
        self.type = 'lazy'

    def affect_visibility(self, visible):
        if random.randint(1,10) < 9:
            return False
        return visible