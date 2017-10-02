class Trait:
    """
    A creature character trait
    """
    def __init__(self):
        self.type = ''


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