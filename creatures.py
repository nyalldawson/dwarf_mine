from typing import List, Optional

import random
from copy import deepcopy
from enchantments import Tricked
from traits import Lazy, Sneaky, Determined, Contagious, Leader
from materials import Boulder
from enchantments import Enchantment, SaboteurSpell, Firestarter, Frozen, SleepSpell
from actions import ExploreAction, SleepAction, PickUpAction, AttackAction, CallToArms, SearchAction, FollowAction
from allegiance import Allegiance


class Creature:
    def __init__(self, x, y, tribe: Optional['Tribe']=None):
        self.x = x
        self.y = y
        self.char = '☺'
        self.mine = None
        self.color = (206, 0)
        self.enchantments = []
        self.view_distance = 0
        self.actions = []
        self.traits = []
        self.type: str = 'Creature'
        self.friends = []
        self.friendly_types = []
        self.enemies = []
        self.enemy_types = []
        self.alive = True
        self.able_to_dig = False
        self.die_callbacks = []
        self.health = 200
        self.knowledge = []
        self.items: List['Item'] = []
        self.tribe: Optional['Tribe'] = tribe

        d = self.default_action()
        if d is not None:
            self.push_action(d)

        if self.tribe is not None:
            self.color = tribe.color

    def place_in_mine(self, mine):
        self.mine = mine
        self.look()

    def default_action(self):
        return None

    def get_identifier(self) -> str:
        """
        Returns a identifier string for the character, eg "blue snake", "evil wizard", etc
        """
        if self.get_tribe() is not None:
            return f'{self.get_tribe().name} {self.type.lower()}'
        return self.type

    def get_char(self):
        c = self.char
        assert len(c) == 1, c
        for e in self.enchantments:
            c = e.alter_char(c)
            assert len(c) == 1, (c, e)
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

    def get_tribe(self):
        return self.tribe

    def push_action(self, action):
        # TODO - avoid duplicate actions
        # assert action not in self.actions
        # if len(self.actions) > 10:
        #    assert False,self.actions
        self.actions.insert(0, action)
        action.added_to_creature(self)

    def remove_action(self, action):
        if action in self.actions:
            action.removed_from_creature(self)
            self.actions.remove(action)

    def add_trait(self, trait):
        self.traits.append(trait)

    def has_trait(self, trait):
        for t in self.traits:
            if isinstance(t, trait):
                return True
        return False

    def get_matching_trait(self, trait):
        for t in self.traits:
            if isinstance(t, trait):
                return t
        return None

    def remove_trait(self, trait):
        try:
            self.traits.remove(trait)
        except:  # ValueError:
            pass

    def learn(self, skill):
        self.knowledge.append(skill)

    def add_item(self, item: 'Item'):
        self.items.append(item)
        self.mine.push_feedback('{} found a {}!'.format(self.get_identifier(), item.type))
        item.found_by(self)
        self.mine.stats.item_collected(self, item)

    def hit(self, damage, message):
        self.health -= damage
        if self.health <= 0:
            self.die(message)
            if isinstance(self, DwarfKing):
                self.mine.push_message(self.tribe.name + ' King ' + message)

    def die(self, message):
        for i in self.items:
            i.x = self.x
            i.y = self.y
            self.mine.add_item(i)
        self.items = []

        self.mine.stats.creature_died(self, message)
        self.mine.remove_creature(self)
        self.mine.push_feedback(f'{self.get_identifier()} {message}!')
        self.alive = False
        for c in self.die_callbacks:
            c(self)

    def replace_with(self, new_creature: 'Creature'):
        self.mine.remove_creature(self)
        new_creature.x = self.x
        new_creature.y = self.y
        self.mine.add_creature(new_creature)
        self.mine.push_feedback(f'{self.get_identifier()} was turned into a {new_creature.get_identifier()}!')

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

    def can_dig(self):
        return self.able_to_dig

    def decided_to_dig(self, x, y):
        return self.can_dig()

    def can_look(self):
        for a in self.actions:
            if a.blocks_looking:
                return False

        for e in self.enchantments:
            if e.blocks_looking:
                return False

        return True

    def move(self):
        for e in self.enchantments:
            e.action()

        if len(self.actions) > 0:
            self.actions[0].do()

    def move_to(self, x, y):
        for t in self.traits:
            res = t.affect_move_to(x, y)
            if res is None:
                return False
            (x, y) = res
        for e in self.enchantments:
            res = e.affect_move_to(x, y)
            if res is None:
                return False
            (x, y) = res

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
        elif creature is not None and self.allegiance_to(creature) == Allegiance.Friendly:
            self.met_friend(creature)

    def attack_with_spell(self, creature):
        spell = self.choose_spell_to_attack_with(creature)
        if spell and spell.try_cast():
            s = deepcopy(spell)

            def remove_allegiance(spell, creature):
                try:
                    creature.friends.remove(self)
                except ValueError:
                    pass
                try:
                    self.friends.remove(creature)
                except ValueError:
                    pass

            spell.add_removal_callback(remove_allegiance)
            creature.enchant(s)
            creature.friends.append(self)
            self.friends.append(creature)
            return True

        return False

    def target_attack_at(self, creature):
        self.push_action(AttackAction(creature))

    def attack(self, creature):
        pass

    def met_friend(self, creature):
        if [a for a in creature.actions if isinstance(a, SleepAction)]:
            return

        for a in self.actions:
            if isinstance(a, SearchAction):
                if not [x for x in creature.actions if isinstance(x, SearchAction)]:
                    creature.push_action(SearchAction(a.target, a.search_rect))
                    #                    self.mine.push_message('miner told his friend')
                    return

        # leaders never follow leaders
        creature_is_leader = False
        for t in creature.traits:
            if isinstance(t, Leader):
                creature_is_leader = True

        if not creature_is_leader:
            for t in self.traits:
                if isinstance(t, Leader):
                    creature.push_action(FollowAction(self))
                    creature.add_trait(Determined())

    def look(self):
        if not self.can_look():
            return

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
        elif self.get_tribe() and creature.get_tribe():
            return self.get_tribe().allegiance_to(creature.get_tribe())
        elif creature.__class__ in self.friendly_types:
            return Allegiance.Friendly
        elif creature.__class__ in self.enemy_types:
            return Allegiance.Hostile
        else:
            return Allegiance.Neutral

    def learnt_offensive_spells(self):
        return [s for s in self.knowledge if issubclass(s.__class__, Enchantment) and s.is_offensive()]

    def choose_spell_to_attack_with(self, creature):
        choices = self.learnt_offensive_spells()
        if choices:
            return random.choice(choices)

        return None


class Snake(Creature):

    def __init__(self, x=-1, y=-1, can_be_contagious=True, tribe=None):
        super().__init__(x, y, tribe=tribe)
        self.color = (23, 8)
        self.view_distance = 4
        self.type = 'Snake'
        self.char = 'S'
        self.health = 10
        self.enemy_types.append(Miner)
        self.enemy_types.append(Wizard)
        self.enemy_types.append(Saboteur)
        self.enemy_types.append(Saboteur)

        if can_be_contagious and random.randint(1, 10) == 1:
            self.add_trait(Contagious())
            self.health = 200
            self.color = (47, 8)

    def place_in_mine(self, mine):
        super().place_in_mine(mine)
        hole_size = 2
        mine.create_cave(self.x, self.y, hole_size)

    def move(self):
        super().move()
        self.look()

    def attack(self, creature):
        super().attack(creature)
        self.mine.show_temp_char(self.x, self.y, '!')
        if self.has_trait(Contagious):
            if random.randint(1, 10) == 1:
                new_snake = Snake(can_be_contagious=False)
                creature.replace_with(new_snake)
        else:
            damage = random.randint(1, 50)
            creature.hit(damage, 'was killed by a {}'.format(self.type))


class Wizard(Creature):
    def __init__(self, x, y, tribe=None):
        super().__init__(x, y, tribe=tribe)
        self.color = (11, 8)
        self.view_distance = 5
        self.type = 'Wizard'
        self.enemy_types.append(Miner)
        self.enemy_types.append(Snake)

        # initial spells
        self.learn(Tricked())
        self.learn(Firestarter())
        self.learn(Frozen())
        self.learn(SleepSpell())

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
        self.attack_with_spell(creature)

    def die(self, message):
        super().die(message)

        from book_of_spells import BookOfSpells

        self.mine.add_item(BookOfSpells(self.x, self.y))


class Miner(Creature):
    def __init__(self, x, y, tribe: Optional['Tribe']=None):
        super().__init__(x, y, tribe=tribe)
        self.likes_to_go_vertical = random.randint(10, 20)
        self.likes_to_go_horizontal = random.randint(10, 20)
        self.view_distance = 5
        self.type = 'Miner'
        self.enemy_types.extend((Wizard, Saboteur, Snake))
        # self.friendly_types.append(Miner)
        self.define_character()
        self.able_to_dig = True

    def default_action(self):
        return ExploreAction()

    def define_character(self):
        if random.randint(1, 30) == 1:
            self.add_trait(Lazy())
        if random.randint(1, 30) == 1:
            self.add_trait(Sneaky())

    def place_in_mine(self, mine):
        super().place_in_mine(mine)
        mine.set_visibility(self.x, self.y, True)

    def decided_to_dig(self, x, y):
        d = self.get_matching_trait(Determined)
        if d is not None and random.randint(1, d.level) == 1:
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
        already_asleep = [a for a in self.actions if isinstance(a, SleepAction)]
        if not already_asleep and random.randint(1, 1000) <= (10 if self.has_trait(Lazy) else 1):
            self.push_action(SleepAction())

        super().move()

    def move_to(self, x, y):
        if super().move_to(x, y):
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
                    if isinstance(a, PickUpAction):
                        if a.item == item:
                            already_going_there = True
                            break
                if not already_going_there:
                    self.push_action(PickUpAction(item))

        super().look_at(x, y)

    def target_attack_at(self, creature: Creature):
        if self.learnt_offensive_spells():
            self.attack_with_spell(creature)

        super().target_attack_at(creature)
        self.mine.push_feedback(f"Help! There's a {creature.get_identifier()} over here!")
        self.push_action(CallToArms(creature))

    def attack(self, creature: Creature):
        super().attack(creature)
        self.mine.show_temp_char(self.x, self.y, '!')
        damage = random.randint(1, 5)
        creature.hit(damage, f'was killed by a {self.get_identifier()}')
        if not creature.alive and isinstance(creature, DwarfKing):
            self.mine.push_message(f'{self.get_identifier()} killed a {creature.get_identifier()}')


class DwarfKing(Miner):

    def __init__(self, x, y, tribe=None):
        super().__init__(x, y, tribe=tribe)
        self.char = '☻'
        self.color = (221, 9)
        self.type = 'Dwarf King'
        self.add_trait(Determined(level=4))
        self.add_trait(Leader())


class Saboteur(Miner):
    def __init__(self, x, y, tribe: Optional['Tribe']=None):
        super().__init__(x, y, tribe=tribe)
        self.char = '☺'
        self.color = (2, 9)
        self.enchant(SaboteurSpell())
        self.type = 'Saboteur'
        self.enemy_types = [Miner]
        self.friendly_types = [Saboteur]
