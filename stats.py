from collections import defaultdict
from typing import List

from items import Treasure
from creatures import Miner
from message_box import MessageBox
from collections import Counter
from events import DeathEvent, FoundItemEvent, DeathByCreatureEvent


class Stats():

    def __init__(self, screen, mine):
        self.screen = screen
        self.treasures_collected = defaultdict(list)
        self.deaths = []
        self.mine = mine
        self.events: List['Event'] = []

    def item_collected(self, creature: 'Creature', item: 'Item'):
        if isinstance(item, Treasure) and isinstance(creature, Miner):
            self.treasures_collected[creature.get_tribe()].append(item.type)

    def creature_died(self, event: 'DeathEvent'):
        if event.victim.is_unique():
            self.mine.push_message(event.get_message())
            self.deaths.append((event.victim.get_identifier(), event.get_partial_message(False)))
        else:
            self.deaths.append((event.victim.type, event.get_partial_message(False)))

    def push_event(self, event: 'Event'):
        """
        Pushes an event which occurred
        """
        if isinstance(event, DeathEvent):
            self.creature_died(event)
        elif isinstance(event, FoundItemEvent):
            self.item_collected(self, event.item)

        self.events.append(event)

    def show_creatures(self):
        if self.show_unique_creatures():
            self.mine.print_current_level()

    def show(self):
        shown_something = False
        if self.show_treasures():
            shown_something = True
            self.mine.print_current_level()

        if self.show_items():
            shown_something = True
            self.mine.print_current_level()

        if self.show_knowledge():
            shown_something = True
            self.mine.print_current_level()

        if self.show_deaths():
            shown_something = True
            self.mine.print_current_level()

        if not shown_something:
            MessageBox(self.screen, 'Our story has just begun...')

    def show_teams(self):
        message = ['Teams','', '']
        for tribe in self.mine.tribes:
            message.append(f'{tribe.name} team')

        MessageBox(self.screen,'\n'.join(message))

    def show_unique_creatures(self) -> bool:

        all_creatures = [(c, None) for c in self.mine.creatures] \
                        +[(event.victim, event) for event in self.events if isinstance(event, DeathEvent)]

        for c, death_event in all_creatures:
            if not c.is_unique():
                continue

            title = c.type
            if death_event is not None:
                title += ' (RIP)'

            message = [title]
            if c.tribe:
                message.append(f'of the {c.tribe.name}')
            if death_event is not None:
                message.append(death_event.get_partial_message(True))

            message.extend([''])

            items_found = [event.item for event in self.events if isinstance(event, FoundItemEvent) and event.found_by==c]
            kills = [event for event in self.events if
                           isinstance(event, DeathByCreatureEvent) and event.killer == c]
            if (items_found or kills) and death_event is not None:
                message.append('While he lived he...')
            elif not items_found and not kills and death_event is not None:
                message.append('Did nothing at all before he died!')
            if items_found:
                message.append(f'Found {len(items_found)} items')
            if kills:
                message.append(f'Killed {len(kills)} creatures')

            message.extend([''])

            if c.items:
                message.append('Carrying:')
                counter = Counter([i.type for i in c.items])
                for t, count in counter.items():
                    if count == 1:
                        message.append('- A {}'.format(t))
                    else:
                        message.append('- {} {}s'.format(count, t))

                message.append('')

            if c.knowledge:
                message.append('Knowledge:')
                for i in c.knowledge:
                    message.append(f'- {i.type}')

                message.append('')

            if c.enchantments:
                message.append('Enchantments:')
                for i in c.enchantments:
                    message.append(f'- {i.type}')

                message.append('')

            if c.traits:
                message.append('Traits:')
                for i in c.traits:
                    message.append(f'- {i.type}')

                message.append('')

            if c.actions and not death_event:
                message.append('Currently:')
                for i in c.actions:
                    message.append(f'- {i.explanation()}')

                message.append('')

            MessageBox(self.screen,'\n'.join(message))
            self.mine.print_current_level()

    def show_items(self) -> bool:
        message = ['Items found','', '']
        found = False
        for tribe in self.mine.tribes:
            treasures = []
            for c in self.mine.creatures:
                if c.tribe == tribe:
                    treasures.extend(i.type for i in c.items if not isinstance(i, Treasure))

            if not treasures:
                continue

            found = True
            message.append(f'{tribe.name} team ({len(treasures)}):')
            c = Counter(treasures)
            for t, count in c.items():
                if count == 1:
                    message.append('- A {}'.format(t))
                else:
                    message.append('- {} {}s'.format(count, t))
            message.append('')

        if found:
            MessageBox(self.screen,'\n'.join(message))

        return found

    def show_treasures(self) -> bool:
        message = ['Treasures found','', '']
        found = False
        for tribe in self.mine.tribes:
            treasures = []
            for c in self.mine.creatures:
                if c.tribe == tribe:
                    treasures.extend(i.type for i in c.items if isinstance(i, Treasure))

            if not treasures:
                continue

            found = True

            message.append(f'{tribe.name} team ({len(treasures)}):')
            c = Counter(treasures)
            for t, count in c.items():
                if count == 1:
                    message.append('- A {}'.format(t))
                else:
                    message.append('- {} {}s'.format(count, t))
            message.append('')

        if found:
            MessageBox(self.screen,'\n'.join(message))
        return found

    def show_knowledge(self) -> bool:
        message = ['Things learnt','', '']
        found = False
        for tribe in self.mine.tribes:
            knowledge = []
            for c in self.mine.creatures:
                if c.tribe == tribe:
                    knowledge.extend(i.type for i in c.knowledge)

            if not knowledge:
                continue

            found = True

            message.append(f'{tribe.name} team ({len(knowledge)}):')
            c = Counter(knowledge)
            for t, count in c.items():
                if count == 1:
                    message.append('- {}'.format(t))
                else:
                    message.append('- {} {}s'.format(count, t))
            message.append('')

        if found:
            MessageBox(self.screen,'\n'.join(message))
        return found

    def show_deaths(self) -> bool:
        message = ['Creatures died','', '']
        c = Counter(self.deaths)
        found = False
        for t, count in c.items():
            found = True
            if count == 1:
                message.append('- A {} {}'.format(t[0], t[1]))
            else:
                message.append('- {} {}s {}'.format(count, t[0], t[1].replace('was','were')))
        if found:
            MessageBox(self.screen,'\n'.join(message))
        return found



