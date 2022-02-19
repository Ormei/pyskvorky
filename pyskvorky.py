import time
import subprocess
import re
import argparse
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame


class Pyskvorky:
    def __init__(self, size):
        self.size = size
        self.field = [[0] * size for _ in range(size)]

    def draw(self, screen):
        screen_x, screen_y = screen.get_size()
        pygame.draw.rect(screen, (192, 192, 192), pygame.Rect(0, 0, screen_x, screen_x))
        for x in range(self.size-1):
            step = int((x + 1) / self.size * screen_x)
            pygame.draw.line(screen, (160, 160, 160), (0, step), (screen_x, step), 1)
            pygame.draw.line(screen, (160, 160, 160), (step, 0), (step, screen_x), 1)
        for x in range(self.size):
            for y in range(self.size):
                if self.field[x][y] == 1:
                    center = int((x + 0.5) / self.size * screen_x), int((y + 0.5) / self.size * screen_x)
                    radius = int(0.4 / self.size * screen_x)
                    pygame.draw.circle(screen, (255, 0, 0), center, radius, 3)
                elif self.field[x][y] == 2:
                    corner0 = int((x + 0.2) / self.size * screen_x), int((y + 0.2) / self.size * screen_x)
                    corner1 = int((x + 0.8) / self.size * screen_x), int((y + 0.2) / self.size * screen_x)
                    corner2 = int((x + 0.8) / self.size * screen_x), int((y + 0.8) / self.size * screen_x)
                    corner3 = int((x + 0.2) / self.size * screen_x), int((y + 0.8) / self.size * screen_x)
                    pygame.draw.line(screen, (0, 0, 255), corner0, corner2, 5)
                    pygame.draw.line(screen, (0, 0, 255), corner1, corner3, 5)

    def put(self, position, player):
        x, y = position
        self.field[x][y] = player


def main():
    parser = argparse.ArgumentParser(description='Piskvorky')
    parser.add_argument('size', type=int, help='field size')
    parser.add_argument('--p1', help='call this process as player 1')
    parser.add_argument('--p2', help='call this process as player 2')
    args = parser.parse_args()

    pygame.init()
    screensize = 800
    screen = pygame.display.set_mode((screensize, screensize))
    field_size = args.size
    p = Pyskvorky(field_size)

    running = True
    players = [True, None, None]
    current_player = 1

    last_move = "start"

    if args.p1:
        players[1] = subprocess.Popen(
            args.p1.split(' ') + [str(field_size), str(field_size)],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE)

    if args.p2:
        players[2] = subprocess.Popen(
            args.p2.split(' ') + [str(field_size), str(field_size)],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not players[current_player]:
                    position = tuple(map(lambda a: int(a * field_size / screensize), pygame.mouse.get_pos()))
                    last_move = f"{position[0]} {position[1]}"
                    print(f'player{current_player} (player) move "{last_move.strip()}"')
                    p.put(position, current_player)
                    current_player = 3 - current_player

        p.draw(screen)

        pygame.display.flip()

        time.sleep(0.1)

        if isinstance(players[current_player], subprocess.Popen):
            print(f'player{current_player} (AI) reacts to "{last_move}"')
            players[current_player].stdin.write(bytes(last_move+"\n", encoding='ASCII'))
            players[current_player].stdin.flush()
            last_move = str(players[current_player].stdout.readline(), encoding='ASCII').strip()
            print(f'player{current_player} (AI) responded "{last_move}"')
            if not re.match(r"^[0-9]+ [0-9]+", last_move):
                print(f'Game over!')
                if players[1]:
                    players[1].stdin.write(bytes("exit\n", encoding='ASCII'))
                    players[1].stdin.flush()
                    players[1] = None
                if players[2]:
                    players[2].stdin.write(bytes("exit\n", encoding='ASCII'))
                    players[2].stdin.flush()
                    players[2] = None
                current_player = 0
            else:
                position = map(lambda a: int(a), last_move.split(' '))
                p.put(position, current_player)
                current_player = 3 - current_player


if __name__ == "__main__":
    main()
