import random
from materials import Space
from allegiance import Allegiance
from utils import Utils


class Action:
    def __init__(self):
        self.creature = None
        self.blocks_looking = False

    def added_to_creature(self, creature):
        self.creature = creature

    def removed_from_creature(self, creature):
        pass

    def do(self):
        pass

    def explanation(self) -> str:
        """
        Explains the action
        """
        return ''

    def can_remove(self) -> bool:
        return False


class SleepAction(Action):
    def __init__(self):
        Action.__init__(self)
        self.duration = random.randint(100, 300)
        self.original_char = None
        self.blocks_looking = True

    def explanation(self) -> str:
        return 'sleeping'

    def added_to_creature(self, creature):
        super().added_to_creature(creature)
        self.original_char = creature.char
        creature.char = 'Z'

        # creatures forget all other actions when they sleep
        creature.actions = [self]

    def remove_other_actions(self, creature):
        for a in creature.actions:
            if a == self:
                continue
            creature.remove_action(a)

    def removed_from_creature(self, creature):
        super().removed_from_creature(creature)
        creature.char = self.original_char

        # creatures forget all other actions when they wake and go back to default action
        creature.actions = [self]
        d = creature.default_action()
        if d is not None:
            creature.push_action(d)

    def do(self):
        self.duration -= 1
        if self.duration == 0:
            self.creature.remove_action(self)


class GoToAction(Action):
    def __init__(self, x, y):
        Action.__init__(self)
        self.x = x
        self.y = y

    def explanation(self) -> str:
        return 'going somewhere'

    def get_target_locations(self):
        return [(self.x,self.y)]

    def can_remove(self):
        if self.creature.x == self.x and self.creature.y == self.y:
            return True
        else:
            return False

    def score_move(self,x,y):
        #less is better
        return Utils.exact_distance(self.x, self.y, x, y)

    def do(self):
        if self.can_remove():
            self.creature.remove_action(self)
            return

        valid_locations = []
        target_locations = self.get_target_locations()
        if len(target_locations) == 0:
            return
        for t in target_locations:
            if self.creature.x != t[0]:
                if self.creature.x < t[0]:
                    valid_locations.append((self.creature.x+1,self.creature.y))
                else:
                    valid_locations.append((self.creature.x-1,self.creature.y))

            if self.creature.y != t[1]:
                if self.creature.y < t[1]:
                    valid_locations.append((self.creature.x,self.creature.y+1))
                else:
                    valid_locations.append((self.creature.x,self.creature.y-1))

            if self.creature.x != t[0]:
                valid_locations.extend([(self.creature.x, self.creature.y-1),
                                        (self.creature.x, self.creature.y + 1)])
            if self.creature.y != t[1]:
                valid_locations.extend([(self.creature.x - 1, self.creature.y),
                                    (self.creature.x + 1, self.creature.y)])

        valid_locations.sort(key=lambda x: self.score_move(x[0],x[1]))

        def try_to_move_to(x, y):
            if not self.creature.mine.is_valid_location(x, y):
                return False
            elif not self.creature.can_move(x, y):
                return False
            elif self.creature.mine.is_empty(x, y):
                self.creature.move_to(x, y)
                return True
            elif self.creature.can_dig() and self.creature.decided_to_dig(x, y):
                self.creature.move_to(x, y)
                self.creature.mine.set_material(x, y, Space())
                return True
            else:
                return False

        for location in valid_locations:
            if try_to_move_to(location[0], location[1]):
                return

        return


class PickUpAction(GoToAction):
    def __init__(self, item):
        super().__init__(item.x, item.y)
        self.item = item

    def explanation(self) -> str:
        return f'picking up an {self.item.type}'

    def can_remove(self):
        if self.item not in self.creature.mine.items:
            return True
        else:
            return False


class AttackAction(GoToAction):
    def __init__(self, target):
        super().__init__(target.x,target.y)
        self.target = target
        self.boredness = 0

        def die_callback(creature):
            self.creature.remove_action(self)
        self.target.push_die_callback(die_callback)

    def explanation(self) -> str:
        return f'attacking a {self.target.get_identifier()}'

    def can_remove(self):
        if self.creature.allegiance_to(self.target) != Allegiance.Hostile:
            return True
        elif self.boredness > 20:
            return True
        else:
            return False

    def can_attack(self):
        return not self.can_remove() and (abs(self.creature.x - self.target.x) <= 1) and (abs(self.creature.y - self.target.y) <= 1)

    def get_target_locations(self):
        if self.can_attack():
            return []

        return [(self.target.x,self.target.y),
                (self.target.x-1,self.target.y),
                (self.target.x+1,self.target.y),
                (self.target.x,self.target.y-1),
                (self.target.x,self.target.y+1)]

    def score_move(self,x,y):
        #less is better
        return Utils.exact_distance(self.target.x, self.target.y, x, y)

    def do(self):
        self.boredness += 1
        if self.can_attack():
            self.creature.attack(self.target)
            self.boredness = 0
            return

        super().do()


class SearchAction(GoToAction):

    def __init__(self, target, search_rect):
        super().__init__(*search_rect.center())
        self.target = target
        self.search_rect = search_rect
        self.cells = []

    def explanation(self) -> str:
        return f'searching for a {self.target.type}'

    def can_remove(self):
        if self.target is not None and self.target not in self.creature.mine.items:
            return True
        else:
            return False

    def added_to_creature(self, creature):
        super().added_to_creature(creature)
        self.search_rect.remove_invalid(creature.mine)
        self.cells = self.search_rect.get_cells()

    def score_move(self,x,y):
        return 1

    def get_target_locations(self):
        for c in self.cells:
            if self.creature.mine.is_visible(c[0],c[1]) and self.creature.mine.is_empty(c[0],c[1]):
                self.cells.remove(c)
        random.shuffle(self.cells)
        return self.cells


class CallToArms(Action):

    def __init__(self, target, loudness=10):
        super().__init__()
        self.target = target
        self.loudness = loudness

    def explanation(self) -> str:
        return 'calling for reinforcements'

    def can_remove(self):
        if self.creature.allegiance_to(self.target) != Allegiance.Hostile:
            return True
        else:
            return False

    def do(self):
        super().do()

        if self.can_remove():
            self.creature.remove_action(self)
            return

        for c in self.creature.mine.creatures:
            if c == self.creature:
                continue

            if Utils.distance(c.x,c.y,self.creature.x,self.creature.y) > self.loudness:
                continue

            if c.allegiance_to(self.creature) == Allegiance.Friendly\
                and c.allegiance_to(self.target) != Allegiance.Friendly:

                has_attack = False
                for a in c.actions:
                    if isinstance(a, AttackAction):
                        has_attack = True
                        break

                if not has_attack:
                    c.push_action(AttackAction(self.target))

        self.creature.remove_action(self)


class ExploreAction(Action):
    def __init__(self):
        Action.__init__(self)
        self.x_dir = 0
        self.xx_dir = 1
        self.y_dir = 1
        self.yy_dir = 1
        self.frustration = 0

    def explanation(self) -> str:
        return 'exploring'

    def think_about_changing_vertical_direction(self):
        if self.creature.y == 0:
            self.yy_dir = 1
            self.y_dir = 1
            return
        if self.creature.y == self.creature.mine.height - 1:
            self.yy_dir = -1
            self.y_dir = -1
            return

        if random.randint(1, 1000) < self.frustration:
            self.yy_dir *= -1
            self.y_dir += self.yy_dir
            self.y_dir = max(min(self.y_dir, 1), -1)
            self.frustration *= 0.5
            return

        if random.randint(1, 1000) == 1:
            self.y_dir += self.yy_dir
            self.y_dir = max(min(self.y_dir, 1), -1)

        # 'general' direction trend is hard to change
        if random.randint(1, 10000) == 1:
            self.yy_dir *= -1

    def think_about_changing_horizontal_direction(self):
        if self.creature.x == 0:
            self.xx_dir = 1
            self.x_dir = 1
            return
        if self.creature.x == self.creature.mine.width - 1:
            self.xx_dir = -1
            self.x_dir = -1
            return

        if random.randint(1, 1000) < self.frustration:
            self.xx_dir *= -1
            self.x_dir += self.xx_dir
            self.x_dir = max(min(self.x_dir, 1), -1)
            self.frustration *= 0.5
            return

        if random.randint(1, 1000) == 1:
            self.x_dir += self.xx_dir
            self.x_dir = max(min(self.x_dir, 1), -1)

        # 'general' direction trend is hard to change
        if random.randint(1, 10000) == 1:
            self.xx_dir *= -1

    def do(self):
        new_x = self.creature.x
        new_y = self.creature.y

        self.think_about_changing_vertical_direction()
        self.think_about_changing_horizontal_direction()

        changed_level = False
        if not changed_level and random.randint(1, 2) == 1:
            new_x += self.x_dir
            changed_level = True

        if not changed_level and random.randint(1, 2) == 1:
            new_y += self.y_dir

        if new_x == self.creature.x and new_y == self.creature.y:
            return

        if not self.creature.mine.is_valid_location(new_x, new_y):
            self.frustration += 1
            return

        if not self.creature.can_move(new_x, new_y):
            self.frustration += 1
            return

        if self.creature.mine.is_empty(new_x, new_y):
            self.creature.move_to(new_x, new_y)
            self.frustration = 0

        else:
            # reluctant to dig
            if self.creature.decided_to_dig(new_x, new_y):
                self.creature.move_to(new_x, new_y)
                self.creature.mine.set_material(new_x, new_y, Space())
                self.frustration = 0
            else:
                self.frustration += 1


class FollowAction(ExploreAction):
    def __init__(self, target):
        super().__init__()
        self.target = target

    def explanation(self) -> str:
        return f'following {self.target.get_identifier()}'

    def can_remove(self):
        if not self.target.alive:
            return True
        else:
            return False

    def think_about_changing_vertical_direction(self):
        return

    def think_about_changing_horizontal_direction(self):
        return

    def do(self):
        self.x_dir = 1 if self.target.x > self.creature.x else -1
        self.y_dir = 1 if self.target.y > self.creature.y else -1

        if self.can_remove():
            self.creature.remove_action(self)
            return
        super().do()
