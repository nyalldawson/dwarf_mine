class Event:
    """
    Something which happened
    """
    def get_message(self) -> str:
        return ''

    def get_partial_message(self) -> str:
        return ''


class DeathEvent(Event):
    """
    Someone/something died
    """

    def __init__(self, victim: 'Creature'):
        super().__init__()
        self.victim = victim


class DeathByCreatureEvent(DeathEvent):
    """
    Someone/something was killed by a creature
    """

    def __init__(self, victim: 'Creature', killer: 'Creature'):
        super().__init__(victim)
        self.killer = killer

    def get_partial_message(self) -> str:
        if self.killer.is_unique():
            return f'was killed by {self.killer.get_identifier()}'
        else:
            return f'was killed by a {self.killer.type}'

    def get_message(self) -> str:
        if self.killer.is_unique():
            return f'{self.victim.get_identifier()} was killed by {self.killer.get_identifier()}'
        else:
            return f'{self.victim.get_identifier()} was killed by a {self.killer.type}'


class DrownedEvent(DeathEvent):
    """
    Someone/something drowned
    """

    def get_partial_message(self) -> str:
        return f'drowned'

    def get_message(self) -> str:
        return f'{self.victim.get_identifier()} drowned'


class BurntToDeathEvent(DeathEvent):
    """
    Someone/something was burnt to death
    """
    def __init__(self, victim:'Creature', cause: str):
        super().__init__(victim=victim)
        self.cause = cause

    def get_partial_message(self) -> str:
        return f'was burnt by {self.cause}'

    def get_message(self) -> str:
        return f'{self.victim.get_identifier()} was burnt by {self.cause}'
