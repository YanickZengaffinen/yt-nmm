from abc import abstractmethod
import pygame as pg
import random
import time

import game
from visualizer import Visualizer

# Exectutes controllers turnwise
class AController():
    def __init__(self):
        self.game = game.Game()
        self.vis = Visualizer()

        self.quit = False

        self.game.start()
        self.vis.set_game(self.game)

    def run(self):
        self.vis.draw()

        while(not self.quit):
            self.update()
            self.vis.draw()

        pg.quit()

    @abstractmethod
    def update(self):
        pass

    def player(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.quit = True
        
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
    
    def ai_random_choice(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.quit = True

        possible_moves = self.game.possible_moves(self.game.turn)

        if self.game.remove:
            # REMOVE
            self.game.try_remove(random.choice(possible_moves))
        else:
            phase = self.game.phase(self.game.turn)
            if phase == game.PHASE_PLACING:
                # PLACE
                self.game.try_put(random.choice(possible_moves), self.game.turn)
            else:
                # MOVE
                from_point, to_point = random.choice([(tuple(k), random.choice(possible_moves[k])) for k in possible_moves if len(possible_moves[k]) > 0])
                self.game.try_move(from_point, to_point)

        time.sleep(.5)

class OneVsOne(AController):
    def update(self):
        self.player()


class OneVsAI(AController):
    def update(self):
        if self.game.turn == game.PLAYER_ONE:
            self.player()
        else:
            self.ai_random_choice()

class AIVsAI(AController):
    def update(self):
            self.ai_random_choice()