import pygame as pg

import game
from visualizer import Visualizer


class OneVsOne():
    def __init__(self):
        self.game = game.Game()
        self.vis = Visualizer()

        self.game.start()
        self.vis.set_game(self.game)

    def run(self):
        self.vis.draw()
        status = True

        while(status):
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    status = False
            
                if e.type == pg.MOUSEBUTTONUP:
                    point = self.vis.coordinate_to_point(e.pos)
                    if point is None: continue

                    if self.game.remove:
                        # REMOVE
                        self.game.try_remove(point)
                        self.from_point = None
                    else:
                        phase = self.game.phase(self.game.turn)
                        if phase == game.PHASE_PLACING:
                            # PLACE
                            self.game.try_put(point, self.game.turn)
                            self.from_point = None
                        else:
                            # MOVE
                            if self.game.board.value(point) == self.game.turn:
                                self.from_point = point
                                self.vis.highlight(point)
                            elif self.from_point is not None:
                                self.game.try_move(self.from_point, point)
                                self.from_point = None
                            
                    self.vis.draw()

        pg.quit()