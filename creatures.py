import random
from enchantments import Tricked
from traits import Lazy, Determined
from materials import Rock
from enchantments import SaboteurSpell, Firestarter
from actions import ExploreAction, SleepAction, GoToAction


class Creature:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.char = '☺'
        self.mine = None
        self.color = (206,0)
        self.enchantments = []
        self.view_distance = 0
        self.actions = []
        self.items = []
        self.traits = []
        self.type = 'Creature'

    def place_in_mine(self, mine):
        self.mine = mine
        self.look()

    def get_char(self):
        c = self.char
        for e in self.enchantments:
            c = e.alter_char(c)
        return c

    def get_color(self):
        colors = [self.color]
        for e in self.enchantments:
            c = e.alter_color()
            if c is not None:
                colors.append(c)
        for i in self.items:
            c = i.alter_color()
            if c is not None:
                colors.append(c)
        return max(colors, key=lambda x: x[1])[0]

    def push_action(self, action):
        self.actions.insert(0, action)
        action.added_to_creature(self)

    def remove_action(self, action):
        self.actions.remove(action)

    def add_trait(self, trait):
        self.traits.append(trait)

    def has_trait(self, trait):
        for t in self.traits:
            if isinstance(t, trait):
                return True
        return False

    def remove_trait(self, trait):
        try:
            self.traits.remove(trait)
        except:  # ValueError:
            pass

    def add_item(self, item):
        self.items.append(item)
        self.mine.push_feedback('{} found a {}!'.format(self.type, item.type))
        item.found_by(self)

    def die(self):
        self.mine.remove_creature(self)
        self.mine.push_feedback('A {} died!'.format(self.type))

    def has_enchantment(self, enchantment):
        for e in self.enchantments:
            if isinstance(e, enchantment):
                return True
        return False

    def enchant(self, enchantment):
        self.enchantments.append(enchantment)
        enchantment.place_on_creature(self)

    def remove_enchantment(self, enchantment):
        self.enchantments.remove(enchantment)

    def move(self):
        for e in self.enchantments:
            e.action()

        if len(self.actions) > 0:
            self.actions[0].do()

    def look_at(self, x, y):
        pass

    def look(self):
        visible_cells = self.mine.get_visible_cells(self.x, self.y, self.view_distance)
        for c in visible_cells:
            if self.x == c[0] and self.y == c[1]:
                continue
            self.look_at(c[0], c[1])


class Wizard(Creature):
    def __init__(self, x, y):
        Creature.__init__(self, x, y)
        self.color = (11,8)
        self.view_distance = 5
        self.type = 'Wizard'

    def place_in_mine(self, mine):
        Creature.place_in_mine(self, mine)
        hole_size = random.randint(2, 6)
        mine.create_cave(self.x, self.y, hole_size)

    def move(self):
        Creature.move(self)
        self.look()

    def look_at(self, x, y):
        creature = self.mine.get_creature(x, y)
        if isinstance(creature, Miner):
            # put a spell on him, if he doesn't have one already
            if not creature.has_enchantment((Firestarter,Tricked)):
                seed = random.randint(1,1000)
                if seed < 50:
                    creature.enchant(Tricked())
                    self.mine.push_feedback('Wizard cast a trick on a {}!'.format(creature.type))
                elif seed < 80:
                    creature.enchant(Firestarter())
                    self.mine.push_feedback('Wizard cast Firestarter on a {}!'.format(creature.type))

class Miner(Creature):
    def __init__(self, x, y):
        Creature.__init__(self, x, y)
        self.likes_to_go_vertical = random.randint(10, 20)
        self.likes_to_go_horizontal = random.randint(10, 20)
        self.view_distance = 5
        self.push_action(ExploreAction())
        self.type = 'Miner'
        self.define_character()

    def define_character(self):
        if random.randint(1, 30) == 1:
            self.add_trait(Lazy())

    def place_in_mine(self, mine):
        Creature.place_in_mine(self, mine)
        mine.set_visibility(self.x, self.y, True)

    def can_move(self, x, y):
        for m in self.mine.creatures:
            if m == self:
                continue
            if m.x == x and m.y == y:
                return False
        return True

    def decided_to_dig(self, x, y):
        if self.has_trait(Determined) and random.randint(1, 2) == 1:
            return True

        if self.has_enchantment(Tricked):
            # he's motivated!
            return random.randint(1, 10) == 1

        toughness = self.mine.material(x, y).toughness
        if not toughness:
            return False

        return random.randint(1, toughness * (
            self.likes_to_go_horizontal * abs(self.x - x) + abs(self.y - y) * self.likes_to_go_vertical)) == 1

    def moved_from(self, x, y):
        if self.has_enchantment(Tricked):
            if random.randint(1, 5) == 1:
                self.mine.set_material(x, y, Rock())

    def move(self):
        if random.randint(1, 1000) <= (10 if self.has_trait(Lazy) else 1):
            self.push_action(SleepAction())

        Creature.move(self)

    def move_to(self, x, y):
        old_x = self.x
        old_y = self.y
        self.x = x
        self.y = y

        visible_cells = self.mine.get_visible_cells(x, y, self.view_distance)
        for c in visible_cells:
            self.mine.set_visibility(c[0], c[1], True)

        self.moved_from(old_x, old_y)
        self.look()

    def look_at(self, x, y):
        self.mine.set_visibility(x, y, True)

        item = self.mine.get_item(x, y)
        if item is not None:
            if item.is_attractive_to(self):
                already_going_there = False
                for a in self.actions:
                    if isinstance(a, GoToAction):
                        if a.x == x and a.y == y:
                            already_going_there = True
                            break
                if not already_going_there:
                    self.push_action(GoToAction(x, y))


class Saboteur(Miner):
    def __init__(self, x, y):
        Miner.__init__(self, x, y)
        self.char = '☺'
        self.color = (2,9)
        self.enchant(SaboteurSpell())
        self.type = 'Saboteur'