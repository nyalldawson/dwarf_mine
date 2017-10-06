from items import Treasure
from creatures import Miner
from message_box import MessageBox
from collections import Counter


class Stats():

    def __init__(self, screen, mine):
        self.screen = screen
        self.treasures_collected = []
        self.deaths = []
        self.mine = mine

    def item_collected(self, creature, item):
        if isinstance(item, Treasure) and isinstance(creature, Miner):
            self.treasures_collected.append(item.type)

    def creature_died(self, creature, death):
        self.deaths.append((creature.type, death))

    def show(self):
        self.show_treasures()
        self.mine.print_current_level()
        self.show_deaths()

    def show_treasures(self):
        message = ['Treasures found','', '']
        c = Counter(self.treasures_collected)
        for t, count in c.items():
            if count == 1:
                message.append('- A {}'.format(t))
            else:
                message.append('- {} {}s'.format(count, t))
        MessageBox(self.screen,'\n'.join(message))

    def show_deaths(self):
        message = ['Creatures died','', '']
        c = Counter(self.deaths)
        for t, count in c.items():
            if count == 1:
                message.append('- A {} {}'.format(t[0], t[1]))
            else:
                message.append('- {} {}s {}'.format(count, t[0], t[1].replace('was','were')))
        MessageBox(self.screen,'\n'.join(message))



