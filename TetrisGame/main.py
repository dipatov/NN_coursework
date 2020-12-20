import pygame
import random
from random import choice, randrange
import tetrisnet
import numpy as np
import torch
pygame.font.init()

s_width = 800
s_height = 700
play_width = 300
play_height = 600
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height

# shape formats

S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
#shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]
shape_colors = lambda : (randrange(30, 256), randrange(30, 256), randrange(30, 256))

class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors()
        self.rotation = random.randint(0,len(shape) - 1)


def create_grid(locked_pos={}):
    grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_pos:
                c = locked_pos[(j,i)]
                grid[i][j] = c
    return grid


def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(shape, grid):
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]

    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True


#проверка на проигрыш (не находится ли какая-либо позиция в данном списке над сеткой)
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


def get_shape():
    return Piece(5, 0, random.choice(shapes))


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont("comicsans", size, bold=True)
    label = font.render(text, 1, color)
    surface.blit(label, (top_left_x + play_width /2 - (label.get_width()/2), top_left_y + play_height/2 - label.get_height()/2))


def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y
    for i in range(len(grid)):
        pygame.draw.line(surface, (128, 128, 128), (sx, sy + i*block_size), (sx+play_width, sy+ i*block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128), (sx + j*block_size, sy),(sx + j*block_size, sy + play_height))


#удаление строки при заполнении
def clear_rows(grid, locked):
    inc = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if (0,0,0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j,i)]
                except:
                    continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    return inc


def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j*block_size, sy + i*block_size, block_size, block_size), 0)

    surface.blit(label, (sx + 10, sy - 30))


def update_score(nscore):
    score = max_score()

    with open('scores.txt', 'w') as f:
        if int(score) > nscore:
            f.write(str(score))
        else:
            f.write(str(nscore))


def max_score():
    with open('scores.txt', 'r') as f:
        lines = f.readlines()
        score = lines[0].strip()
    return score


def draw_window(surface, grid, score=0, last_score = 0):
    surface.fill((0, 0, 0))

    pygame.font.init()
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('AI Tetris', 1, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

    # current score
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Score: ' + str(score), 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100

    surface.blit(label, (sx + 20, sy + 160))
    # last score
    label = font.render('High Score: ' + last_score, 1, (255,255,255))

    sx = top_left_x - 200
    sy = top_left_y + 200

    surface.blit(label, (sx + 20, sy + 160))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j*block_size, top_left_y + i*block_size, block_size, block_size), 0)

    pygame.draw.rect(surface, (255, 255, 255), (top_left_x, top_left_y, play_width, play_height), 2)

    draw_grid(surface, grid)

def get_fig(fig):
    min_x = 100
    min_y = 100
    max_x = -1
    max_y = -1
    for i in range(len(fig)):
        for j in range(len(fig[0])):
            if fig[i][j] == 1:
                min_x = min(j,min_x)
                min_y = min(i,min_y)
                max_x = max(j,max_x)
                max_y = max(i,max_y)
    return fig[min_y:max_y+1,min_x:max_x+1].copy()
    
def get_field_with_fig(field, fig, i):
    max_y = -1
    for j in range(0,len(field)-len(fig)+1):
        flag = True
        for y in range(len(fig)):
            for x in range(len(fig[0])):
                if field[j+y][x+i] == 1 and fig[y][x] == 1:
                    flag = False
        if flag:
            max_y = j
        else:
            break
    if max_y == -1:
        return field.copy()
    else:
        temp_field = field.copy()
        for y in range(len(fig)):
            for x in range(len(fig[0])):
                if fig[y][x] == 1:
                    temp_field[y+max_y][x+i] = 1
        return temp_field
        
def get_height(field, i):
    for j in range(len(field)):
        if field[j][i] == 1:
            return len(field) - j
    return 0

def get_differences(heights):
    return sum([abs(heights[i] - heights[i+1]) for i in range(len(heights)-1)])

def get_amount_lines(field):
    nums = 0
    for j in range(len(field)):
        flag = True
        for i in range(len(field[0])):
            if field[j][i] == 0:
                flag = False
                break
        if flag:
            nums += 1
    return nums
    
def get_holes(field, heights):
    holes = 0
    for i in range(len(heights)):
        for j in range(len(field) - heights[i], len(field)):
            if(field[j][i] == 0):
                holes += 1
    return holes

def get_step(grid, current_piece, TNN):
    scores = -1e10
    x = 0
    rota = 0
    for rot in range(len(current_piece.shape)):
        field = np.zeros((20,10))
        for i in range(20):
            for j in range(10):
                if grid[i][j] == (0,0,0):
                    field[i][j] = 0.
                else:
                    field[i][j] = 1.
        fig = np.zeros((5,5))
        
        for i in range(5):
            for j in range(5):
                if current_piece.shape[rot][i][j] == '0':
                    fig[i][j] = 1.
                else:
                    fig[i][j] = 0.
        fig = get_fig(fig)
        
        for i in range(len(field[0])-len(fig[0])+1):
            temp_field = get_field_with_fig(field,fig,i)
            heights = [get_height(temp_field, j) for j in range(len(temp_field[0]))]
            differences = get_differences(heights)
            amount_lines = get_amount_lines(temp_field)
            holes = get_holes(temp_field, heights)
            max_height = max(heights)
            min_height = min(heights)
            score = TNN.forward(np.array([float(differences), float(holes), float(amount_lines), float(min_height), float(max_height)]))
            if score > scores:
                x = i
                rota = rot
                scores = score
    return x, rota
        
def get_current_pos(current_piece):
    if current_piece.shape == S:
        if current_piece.rotation == 0:
            return 4
        else:
            return 5
    elif current_piece.shape == I:
        if current_piece.rotation == 0:
            return 5
        else:
            return 3
    elif current_piece.shape == J:
        if current_piece.rotation == 1:
            return 5
        else:
            return 4
    elif current_piece.shape == L:
        if current_piece.rotation == 1:
            return 5
        else:
            return 4
    elif current_piece.shape == T:
        if current_piece.rotation == 1:
            return 5
        else:
            return 4
    else:
        return 4


def main(win):




    last_score = max_score()
    locked_positions = {}
    grid = create_grid(locked_positions)
    TNN = tetrisnet.TetrisNet()
    TNN.m1 = np.matrix([[-0.874313, 0.302529, -1.1421, -0.257178, -0.869937, ],
[1.13769, 1.6891, -0.0688631, -1.35793, -1.66535, ],
[0.0370188, -0.515627, -1.25191, 0.627983, -0.532746, ],
[-0.0497609, -0.371445, -0.89942, 2.01398, 2.18431, ],
[-0.350091, 0.0531693, -1.6935, -1.37114, 0.13328, ],
])
    TNN.bias1 = np.matrix([[0.299143, 0.745956, -0.769967, -0.155007, -0.149685, ],
])
    TNN.m2 = np.matrix([[-0.304138, ],
[-1.89745, ],
[0.43527, ],
[0.0803377, ],
[-0.0400605, ],
])
    TNN.bias2 = np.matrix([[0.476275, ],
])
    
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    change_time = 0
    fall_speed = 0.27
    level_time = 0
    score = 0
    grid = create_grid(locked_positions)
    step, rota = get_step(grid, current_piece, TNN)
    current_pos_x = get_current_pos(current_piece)
    flag = 0
    
    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        change_time += clock.get_rawtime()
        
        clock.tick()
        
        if level_time/1000 > 5:
            level_time = 0
            if level_time > 0.12:
                level_time -= 0.005
       
        if fall_time/1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            flag += 1
            if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True
        
        if change_time/1000 > fall_speed/30:
            change_time = 0
            if current_piece.rotation != rota:
                up(current_piece, grid)
                current_pos_x = get_current_pos(current_piece)
            elif current_pos_x > step:
                current_pos_x -=1
                left(current_piece, grid)
            elif current_pos_x < step:
                current_pos_x += 1
                right(current_piece, grid)
            else:
                down(current_piece, grid)
       
        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            flag = 0
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10
            grid = create_grid(locked_positions)
            step, rota = get_step(grid, current_piece, TNN)
            current_pos_x = get_current_pos(current_piece)

        draw_window(win, grid, score, last_score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        if check_lost(locked_positions):
            draw_text_middle(win, "GAME OVER", 80, (255,255,255))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
            update_score(score)

def right(current_piece, grid):
    current_piece.x += 1
    if not (valid_space(current_piece, grid)):
        current_piece.x -= 1

def left(current_piece, grid):
    current_piece.x -= 1
    if not (valid_space(current_piece, grid)):
        current_piece.x += 1

def down(current_piece, grid):
    current_piece.y += 1
    if not (valid_space(current_piece, grid)):
        current_piece.y -= 1

def up(current_piece, grid):
    current_piece.rotation = (current_piece.rotation+1)%(len(current_piece.shape))
    if not (valid_space(current_piece, grid)):
        current_piece.rotation = (len(current_piece.shape)+current_piece.rotation-1)%(len(current_piece.shape))

def main_menu(win):  # *
    run = True
    while run:
        win.fill((0,0,0))
        draw_text_middle(win, 'Press Any Key To Play', 60, (255,255,255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(win)

    pygame.display.quit()

win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('AI Tetris')
main_menu(win)