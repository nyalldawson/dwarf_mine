import random
from enchantments import Tricked
from traits import Lazy, Sneaky, Determined
from materials import Boulder
from enchantments import SaboteurSpell, Firestarter, Frozen, SleepSpell
from actions import ExploreAction, SleepAction, GoToAction, AttackAction, CallToArms
from allegiance import Allegiance

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
        self.friends = []
        self.friendly_types = []
        self.enemies = []
        self.enemy_types = []
        self.alive = True
        self.die_callbacks = []

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
        if action in self.actions:
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
        self.mine.stats.item_collected(self, item)

    def die(self, message):
        self.mine.stats.creature_died(self,message)
        self.mine.remove_creature(self)
        self.mine.push_feedback('A {} {}!'.format(self.type, message))
        self.alive = False
        for c in self.die_callbacks:
            c(self)

    def push_die_callback(self, callback):
        self.die_callbacks.append(callback)

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

    def can_move(self, x, y):
        for m in self.mine.creatures:
            if m == self:
                continue
            if m.x == x and m.y == y:
                return False
        return True

    def move(self):
        for e in self.enchantments:
            e.action()

        if len(self.actions) > 0:
            self.actions[0].do()

    def move_to(self, x, y):
        for t in self.traits:
            res = t.affect_move_to(x,y)
            if res is None:
                return False
            (x,y)=res
        for e in self.enchantments:
            res = e.affect_move_to(x,y)
            if res is None:
                return False
            (x,y)=res

        old_x = self.x
        old_y = self.y
        self.x = x
        self.y = y
        self.moved_from(old_x, old_y)
        return True

    def moved_from(self, x, y):
        pass

    def look_at(self, x, y):
        creature = self.mine.get_creature(x, y)
        if creature is not None and creature.is_visible() and self.allegiance_to(creature) == Allegiance.Hostile:
            self.target_attack_at(creature)

    def target_attack_at(self, creature):
        self.push_action(AttackAction(creature))

    def attack(self, creature):
        pass

    def look(self):
        visible_cells = self.mine.get_visible_cells(self.x, self.y, self.view_distance)
        for c in visible_cells:
            if self.x == c[0] and self.y == c[1]:
                continue
            self.look_at(c[0], c[1])

    def is_visible(self):
        visible = True
        for t in self.traits:
            visible = t.affect_visibility(visible)
        for e in self.enchantments:
            visible = e.affect_visibility(visible)
        return visible

    def allegiance_to(self, creature):
        if creature in self.friends:
            return Allegiance.Friendly
        elif creature in self.enemies:
            return Allegiance.Hostile
        elif creature.__class__ in self.friendly_types:
            return Allegiance.Friendly
        elif creature.__class__ in self.enemy_types:
            return Allegiance.Hostile
        else:
            return Allegiance.Neutral


class Wizard(Creature):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = (11,8)
        self.view_distance = 5
        self.type = 'Wizard'
        self.enemy_types.append(Miner)

    def place_in_mine(self, mine):
        super().place_in_mine(mine)
        hole_size = random.randint(2, 6)
        mine.create_cave(self.x, self.y, hole_size)

    def move(self):
        super().move()
        self.look()

    def can_move(self, x, y):
        return False

    def target_attack_at(self, creature):
        seed = random.randint(1,1300)
        spell = None
        if seed < 50:
            spell = Tricked()
            self.mine.push_feedback('Wizard cast a trick on a {}!'.format(creature.type))
        elif seed < 80:
            spell = Firestarter()
            self.mine.push_feedback('Wizard cast Firestarter on a {}!'.format(creature.type))
        elif seed < 130:
            spell = Frozen()
            self.mine.push_feedback('Wizard cast Freeze on a {}!'.format(creature.type))
        elif seed < 160:
            spell = SleepSpell()
            self.mine.push_feedback('Wizard cast Sleep on a {}!'.format(creature.type))
        if spell is not None:
            def remove_allegiance(spell,creature):
                creature.friends.remove(self)
                self.friends.remove(creature)

            spell.add_removal_callback(remove_allegiance)
            creature.enchant(spell)
            creature.friends.append(self)
            self.friends.append(creature)


class Miner(Creature):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.likes_to_go_vertical = random.randint(10, 20)
        self.likes_to_go_horizontal = random.randint(10, 20)
        self.view_distance = 5
        self.push_action(ExploreAction())
        self.type = 'Miner'
        self.enemy_types.extend((Wizard, Saboteur))
        self.friendly_types.append(Miner)
        self.define_character()

    def define_character(self):
        if random.randint(1, 30) == 1:
            self.add_trait(Lazy())
        if random.randint(1, 30) == 1:
            self.add_trait(Sneaky())

    def place_in_mine(self, mine):
        super().place_in_mine(mine)
        mine.set_visibility(self.x, self.y, True)

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
                self.mine.set_material(x, y, Boulder())

    def move(self):
        if random.randint(1, 1000) <= (10 if self.has_trait(Lazy) else 1):
            self.push_action(SleepAction())

        super().move()

    def move_to(self, x, y):
        if super().move_to(x,y):
            visible_cells = self.mine.get_visible_cells(x, y, self.view_distance)
            for c in visible_cells:
                self.mine.set_visibility(c[0], c[1], True)
            self.look()
            return True
        return False

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

        super().look_at(x,y)

    def target_attack_at(self, creature):
        super().target_attack_at(creature)
        self.mine.push_feedback("Help! There's a {} over here!".format(creature.type))
        self.push_action(CallToArms(creature))

    def attack(self, creature):
        super().attack(creature)
        self.mine.screen.addstr(self.y, self.x, '!')
        if random.randint(1,1000) == 1:
            creature.die('was killed by a Miner')
            self.mine.push_message('Miner killed a {}'.format(creature.type))


class Saboteur(Miner):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.char = '☺'
        self.color = (2,9)
        self.enchant(SaboteurSpell())
        self.type = 'Saboteur'
