"""
former bug: 1. if fast_pos != Pos(col, slow - 1):
                   # 不知道为什么去掉会有bug
                   # 因为每次只更新了grid的position, 而没有改变pos
                   # 淦, 这个bug找了我好久
"""

from random import sample, choice, randint

from cocos.scene import Scene
from cocos.layer import Layer, ColorLayer
from cocos.sprite import Sprite
from pyglet.window import key
from cocos.draw import Line
from cocos.actions import FadeOut, FadeIn, ScaleTo

from settings import Settings
from grid import Grid
from position import Pos


class GameScene(Scene):
    def __init__(self):
        super(GameScene, self).__init__()

        self.add(ColorLayer(255, 255, 255, 255), z=1)  # 背景涂白
        self.add(GameLayer(), z=3)


class GameLayer(Layer):
    is_event_handler = True

    def __init__(self):
        super(GameLayer, self).__init__()

        self.draw_grids()
        self.grids = {Pos(col, row): None
                      for col in range(Settings.COLUMNS)
                      for row in range(Settings.ROWS)}
        self.grid_init()

    def on_key_press(self, k, *_):
        if k == key.UP or k == key.W:
            self.move_grid_up()
        elif k == key.DOWN or k == key.S:
            self.move_grid_down()
        elif k == key.LEFT or k == key.A:
            self.move_grid_left()
        elif k == key.RIGHT or k == key.D:
            self.move_grid_right()

    def move_grid_up(self):
        for col in range(Settings.COLUMNS):
            slow = Settings.ROWS - 1
            for fast in range(slow - 1, -1, -1):
                fast_pos = Pos(col, fast)
                slow_pos = Pos(col, slow)  # 都要不断更新
                if self.grids[fast_pos]:  # fast处是grid
                    if self.grids[slow_pos]:
                        if self.grids[fast_pos].power == self.grids[slow_pos].power:  # grid_num相同
                            self.del_grid(fast_pos)
                            self.double_grid(slow_pos)
                        else:  # grid_num不同
                            self.grids[fast_pos].move_to(Pos(col, slow - 1), self)
                        slow -= 1
                    else:
                        self.grids[fast_pos].move_to(slow_pos, self)  # 如果slow处没东西, 就把fast处的移过去
        self.random_grid()

    def move_grid_down(self):
        for col in range(Settings.COLUMNS):
            slow = 0
            for fast in range(slow + 1, Settings.ROWS):
                fast_pos = Pos(col, fast)
                slow_pos = Pos(col, slow)  # 都要不断更新
                if self.grids[fast_pos]:  # fast处是grid
                    if self.grids[slow_pos]:
                        if self.grids[fast_pos].power == self.grids[slow_pos].power:  # grid_num相同
                            self.del_grid(fast_pos)
                            self.double_grid(slow_pos)
                        else:  # grid_num不同
                            self.grids[fast_pos].move_to(Pos(col, slow + 1), self)
                        slow += 1
                    else:
                        self.grids[fast_pos].move_to(slow_pos, self)  # 如果slow处没东西, 就把fast处的移过去
        self.random_grid()

    def move_grid_left(self):
        for row in range(Settings.ROWS):
            slow = 0
            for fast in range(slow + 1, Settings.COLUMNS):
                fast_pos = Pos(fast, row)
                slow_pos = Pos(slow, row)  # 都要不断更新
                if self.grids[fast_pos]:  # fast处是grid
                    if self.grids[slow_pos]:
                        if self.grids[fast_pos].power == self.grids[slow_pos].power:  # grid_num相同
                            self.del_grid(fast_pos)
                            self.double_grid(slow_pos)
                        else:  # grid_num不同
                            self.grids[fast_pos].move_to(Pos(slow + 1, row), self)
                        slow += 1
                    else:
                        self.grids[fast_pos].move_to(slow_pos, self)  # 如果slow处没东西, 就把fast处的移过去
        self.random_grid()

    def move_grid_right(self):
        for row in range(Settings.ROWS):
            slow = Settings.COLUMNS - 1
            for fast in range(slow - 1, -1, -1):
                fast_pos = Pos(fast, row)
                slow_pos = Pos(slow, row)  # 都要不断更新
                if self.grids[fast_pos]:  # fast处是grid
                    if self.grids[slow_pos]:
                        if self.grids[fast_pos].power == self.grids[slow_pos].power:  # grid_num相同
                            self.del_grid(fast_pos)
                            self.double_grid(slow_pos)
                        else:  # grid_num不同
                            self.grids[fast_pos].move_to(Pos(slow - 1, row), self)
                        slow -= 1
                    else:
                        self.grids[fast_pos].move_to(slow_pos, self)  # 如果slow处没东西, 就把fast处的移过去
        self.random_grid()

    def grid_init(self):
        for pos in sample(list(self.grids), 16):
            self.set_grid(power=1, pos=pos)

    def set_grid(self, power, pos, is_inflate=False):
        temp = Grid(power=power, pos=pos)
        self.grids[pos] = temp
        self.add(temp, z=10)
        if is_inflate:
            temp.do(ScaleTo(1.2, 0.05) + ScaleTo(0.8, 0.1) + ScaleTo(1, 0.05))
        else:
            temp.do(FadeIn(Settings.fade_time))

    def del_grid(self, pos):
        self.grids[pos].do(FadeOut(Settings.fade_time))
        self.remove(self.grids[pos])
        self.grids[pos] = None

    def double_grid(self, pos):
        old_pow = self.grids[pos].power
        self.del_grid(pos)
        self.set_grid(power=old_pow + 1, pos=pos, is_inflate=True)

    def random_grid(self):
        chosen = [pos for pos in self.grids if self.grids[pos] is None]
        if chosen:
            times = 2 if len(chosen) > 2 else 1
            poses = sample(chosen, times)
            for pos in poses:
                if pos:
                    if randint(1, 10) <= 8:  # 80%出2
                        self.set_grid(1, pos)
                    else:  # 20%出4
                        self.set_grid(2, pos)
        else:  # 不是game_over
            print("sdkjf")

    def draw_grids(self):
        for x in range(Settings.COLUMNS + 1):
            self.add(Line(start=(Settings.ORIGIN[0] + x * Settings.GRID_SIZE, Settings.ORIGIN[1]),
                          end=(Settings.ORIGIN[0] + x * Settings.GRID_SIZE,
                               Settings.ORIGIN[1] + Settings.ROWS * Settings.GRID_SIZE),
                          color=(0, 0, 0, 255)))
        for y in range(Settings.ROWS + 1):
            self.add(Line(start=(Settings.ORIGIN[0], Settings.ORIGIN[1] + y * Settings.GRID_SIZE),
                          end=(Settings.ORIGIN[0] + Settings.COLUMNS * Settings.GRID_SIZE,
                               Settings.ORIGIN[1] + y * Settings.GRID_SIZE),
                          color=(0, 0, 0, 255)))