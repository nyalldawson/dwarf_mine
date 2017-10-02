import random
from materials import Space


class Action:
    def __init__(self):
        self.creature = None

    def added_to_creature(self, creature):
        self.creature = creature

    def do(self):
        pass


class SleepAction(Action):
    def __init__(self):
        Action.__init__(self)
        self.duration = random.randint(100, 300)
        self.original_char = None

    def added_to_creature(self, creature):
        Action.added_to_creature(self, creature)
        self.original_char = creature.char
        creature.char = 'Z'

    def do(self):
        self.duration -= 1
        if self.duration == 0:
            self.creature.char = self.original_char
            self.creature.remove_action(self)


class GoToAction(Action):
    def __init__(self, x, y):
        Action.__init__(self)
        self.x = x
        self.y = y

    def do(self):
        if self.creature.x == self.x and self.creature.y == self.y:
            self.creature.remove_action(self)

        new_x = self.creature.x
        new_y = self.creature.y
        if self.creature.x < self.x:
            new_x += 1
        elif self.creature.x > self.x:
            new_x -= 1

        def try_to_move_to(x, y):
            if not self.creature.mine.is_valid_location(x, y):
                return False
            elif not self.creature.can_move(x, y):
                return False
            elif self.creature.mine.is_empty(x, y):
                self.creature.move_to(x, y)
                return True
            elif self.creature.decided_to_dig(x, y):
                self.creature.move_to(x, y)
                self.creature.mine.set_material(x, y, Space())
                return True
            else:
                return False

        if not new_x == self.creature.x:
            if try_to_move_to(new_x, new_y):
                return
            else:
                new_x = self.creature.x

        if self.creature.y < self.y:
            new_y += 1
        elif self.creature.y > self.y:
            new_y -= 1

        if not new_y == self.creature.y:
            if try_to_move_to(new_x, new_y):
                return

        return


class ExploreAction(Action):
    def __init__(self):
        Action.__init__(self)
        self.x_dir = 0
        self.xx_dir = 1
        self.y_dir = 1
        self.yy_dir = 1
        self.frustration = 0

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