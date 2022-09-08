import pygame as pg

import game

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BOARD_WIDTH = 400
BOARD_HEIGHT = 400
BG_COLOR = '#e8ce90'
LINE_COLOR = '#523323'
POINT_COLOR = '#523323'

TEXT_COLOR = '#000000'

PLAYER_ONE_COLOR = '#FFFFFF'
PLAYER_TWO_COLOR = '#000000'

PIECE_RADIUS = 25
HIGHLIGHTED_RADIUS = 33

class Visualizer():
    def __init__(self):
        self._board_offset = (50, 50)
        self._game : game.Game = None
        self._highlighted = None

        pg.init()
        pg.display.set_caption("Nine Men's Morris")
        self._screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        # all the coordinates of the points
        self._cs = { f: self.point_to_coordinate(f) for f in game.points }

    def point_to_coordinate(self, point):
        ox, oy = self._board_offset
        x, y = point

        return (BOARD_WIDTH / 7 * x + ox, BOARD_HEIGHT / 7 * y + oy)

    def coordinate_to_point(self, coordinate):
        x, y = coordinate

        best = None
        best_dist = None
        for p in self._cs:
            c = self._cs[p]
            cx, cy = c
            dist = (x - cx)**2 + (y - cy)**2
            if (best == None or dist < best_dist) and dist <= PIECE_RADIUS*PIECE_RADIUS:
                best = p
                best_dist = dist

        return best

    def _draw_bg(self):
        self._screen.fill(BG_COLOR)
        
        lines = [
            ((0, 6), (6, 6)),
            ((1, 5), (5, 5)),
            ((2, 4), (4, 4)),
            ((0, 3), (2, 3)),
            ((4, 3), (6, 3)),
            ((2, 2), (4, 2)),
            ((1, 1), (5, 1)),
            ((0, 0), (6, 0)),

            ((0, 6), (0, 0)),
            ((1, 5), (1, 1)),
            ((2, 4), (2, 2)),
            ((3, 6), (3, 4)),
            ((3, 2), (3, 0)),
            ((4, 4), (4, 2)),
            ((5, 5), (5, 1)),
            ((6, 6), (6, 0))
        ]

        for s,t in lines:
            pg.draw.line(self._screen, LINE_COLOR, self._cs[s], self._cs[t], width=2)

        for p in game.points:
            pg.draw.circle(self._screen, POINT_COLOR, self._cs[p], 10, 0)
        
    def _draw_game(self):
        for p in game.points:
            value = self._game.board.value(p)
            radius = HIGHLIGHTED_RADIUS if p == self._highlighted else PIECE_RADIUS
            if value == game.PLAYER_ONE:
                pg.draw.circle(self._screen, PLAYER_ONE_COLOR, self._cs[p], radius, 0)
            elif value == game.PLAYER_TWO:
                pg.draw.circle(self._screen, PLAYER_TWO_COLOR, self._cs[p], radius, 0)

    def _draw_state(self):
        font = pg.font.SysFont('monospace', 20, True)

        lbl_turn = font.render('Player:', True, TEXT_COLOR)
        
        ox, oy = self._board_offset
        x = ox + BOARD_WIDTH
        y = oy

        self._screen.blit(lbl_turn, (x, y))

        turn = self._game.turn
        pg.draw.circle(self._screen, PLAYER_ONE_COLOR if turn == game.PLAYER_ONE else PLAYER_TWO_COLOR, (x + lbl_turn.get_width() + 20, y + lbl_turn.get_height() / 2), 10, 0)

        next_move = 'remove'
        if not self._game.remove:
            phase = self._game.phase(self._game.turn)
            phases = {
                game.PHASE_PLACING: 'placing',
                game.PHASE_NORMAL: 'move',
                game.PHASE_WILD: 'wild'
            }

            next_move = phases[phase]
        
        y += lbl_turn.get_height() + 10
        lbl_phase = font.render(f'Phase: {next_move}', True, TEXT_COLOR)
        self._screen.blit(lbl_phase, (x, y))

        y += lbl_phase.get_height() + 50
        for i in range(0, self._game.to_place(game.PLAYER_ONE)):
            pg.draw.circle(self._screen, PLAYER_ONE_COLOR, (x + 10 + 25 * i, y), 10, 0)
        
        for i in range(0, self._game.to_place(game.PLAYER_TWO)):
            pg.draw.circle(self._screen, PLAYER_TWO_COLOR, (x + 10 + 25 * i, y + 25), 10, 0)
        

    def draw(self):
        self._draw_bg()
        self._draw_game()
        self._draw_state()

        pg.display.flip()

    def highlight(self, point):
        self._highlighted = point

    def set_game(self, game):
        self._game = game
        self.draw()
