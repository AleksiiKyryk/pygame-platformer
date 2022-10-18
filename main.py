import pygame
import sys
import random
import noise
from pygame.locals import *

pygame.init()
pygame.display.set_caption("Fun platformer")
pygame.font.init()
myfont = pygame.font.SysFont("San Francisco", 16)
smallfont = pygame.font.SysFont("San Francisco", 14)

# Classes
class Tile:
    def __init__(self, tile_type, rect, position):
        self.tile_type = tile_type
        self.rect = rect
        self.position = position

class Player:
    def __init__(self, rect):
        self.rect = rect
        self.current_health = 100
        self.max_health = 100
        self.health_bar_length = 100
        self.health_bar_ratio = self.max_health / self.health_bar_length
        self.score = 0
        self.current_objective = "Find rare gems"
    
    def basic_health_bar(self):
        pygame.draw.rect(display, (255,0,0),(10,10,self.current_health/self.health_bar_ratio, 8))
        pygame.draw.rect(display, (0,0,0), (10,10,self.health_bar_length,8),1)
        
    def update_health_bar(self):
        self.basic_health_bar()

    def get_damage(self, amount):
        if self.current_health > 0:
            self.current_health -= amount
        if self.current_health <= 0:
            self.current_health = 0
    
    def get_health(self, amount):
        if self.current_health < self.max_health:
            self.current_health += amount
        if self.current_health >= self.max_health:
            self.current_health = self.max_health

    def show_score(self):
        score_text = 'Score: {}'.format(int(self.score))
        textsurface = myfont.render(score_text, False, (0,0,0))
        display.blit(textsurface,(300 - textsurface.get_width() - 10 ,5))
    
    def show_objective(self):
        objective_text = self.current_objective
        obj_text_surface = myfont.render(objective_text, False, (0,0,0))
        display.blit(obj_text_surface, (10, 20))


# Variables
clock = pygame.time.Clock()
FPS = 90
WINDOW_SIZE = (600, 400)
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
display = pygame.Surface((300, 200))

# Objects related
# Images loading
player_image = pygame.image.load('player2.png')
player_image.set_colorkey((255,255,255))
grass_image = pygame.image.load('grass.png')
dirt_image = pygame.image.load('dirt.png')
plant_image = pygame.image.load('plant.png').convert()
plant_image.set_colorkey((255,255,255))
coin_image = pygame.image.load('coin.png')
spike_image = pygame.image.load('spike.png').convert()
spike_image.set_colorkey((255,255,255))
bg_image = pygame.image.load('bg1.png')
heart_image = pygame.image.load('heart.png')

tile_index = {1:grass_image, 2: dirt_image, 3: plant_image, 4: spike_image, 5: heart_image}
TILE_SIZE = dirt_image.get_width()
player_rect = pygame.Rect(50,50, player_image.get_width(), player_image.get_height())
player = Player(player_rect)
background_objects = [[0.25,[120,10,70,400]],[0.25,[280,30,40,400]],[0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[0.5,[300,80,120,400]]]

# Map related
game_map = {}
CHUNK_SIZE = 8
constant = random.randint(3,5)



# Movement related
moving_right = False
moving_left = False
player_y_momentum = 0
air_timer = 0

# Scroll
true_scroll = [0,0]

# Functions

# Return list of tiles collided with
def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile.rect):
            if tile.tile_type == 1 or tile.tile_type == 2 or tile.tile_type == 4:
                hit_list.append(tile.rect)
            if tile.tile_type == 4:
                player.get_damage(1)
                player.update_health_bar()
                print(player.current_health)
            if tile.tile_type == 5:
                # print('Heart found')            
                if player.current_health < 100:
                    # print("Healing by 10 hp")
                    player.get_health(10)
                    remove_tile(5)
                    
                
    return hit_list

# Remove the tile from map by given type
def remove_tile(type):
    for y in range(4):
        for x in range(4):
            target_x = x - 1 + int(round(scroll[0] / (CHUNK_SIZE*16)))
            target_y = y - 1 + int(round(scroll[1] / (CHUNK_SIZE*16)))
            target_chunk = str(target_x) + ';' + str(target_y)
            if target_chunk not in game_map:
                print("lol")
                
            for tile in game_map[target_chunk]:
                if tile[1] == type:
                    # print(tile[0],tile[1])
                    game_map[target_chunk].remove(tile)

# Return new position and direction of collisions that happened
def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    
    rect.y += movement[1]
    hit_list = collision_test(rect,tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
            
    return rect, collision_types

# Generate new chunk 
def generate_chunk(x,y,constant):
    chunk_data = []
    heart_spawned = False
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + x_pos
            target_y = y *CHUNK_SIZE + y_pos 
            tile_type = 0   # nothing
            height = int(noise.pnoise1(target_x * 0.1, repeat=1024) * constant)
            if target_y > 8 - height:
                tile_type = 2   # dirt
            elif target_y == 8 - height:
                tile_type = 1   # grass
            elif target_y == 8 - height - 1:
                if random.randint(1,5) == 1:
                    tile_type = 3   # plant
                elif random.randint(1,8) == 1:
                    tile_type = 4   # spike   
                elif random.randint(1,48) == 1 and not heart_spawned:
                    tile_type = 5 # heart
                    heart_spawned = True        
                    
            if tile_type != 0:
                chunk_data.append([[target_x, target_y], tile_type])

    return chunk_data

def show_instructions():    # instructions
    myfont2 = pygame.font.SysFont("San Francisco", 22)
    inst_surf = myfont2.render('Explore the world to get high score', False, (0,0,0))
    display.blit(inst_surf,((300 - inst_surf.get_width()) / 2 , (120 - inst_surf.get_height()) / 2))
    inst_surf2 = myfont2.render('Avoid the spikes to not lose health', False, (0,0,0))
    display.blit(inst_surf2,((300 - inst_surf2.get_width()) / 2 , (150 - inst_surf2.get_height()) / 2) )
    # display.blit(inst_surf, (120, 80))
    


# def show_game_over_screen():
#     myfont2 = pygame.font.SysFont("San Francisco", 48)
#     gameover_text = myfont2.render('GAME OVER!', False, (255,255,255))
#     screen.blit(gameover_text,((600 - gameover_text.get_width()) / 2 , (320 - gameover_text.get_height()) / 2))
#     gameover_text2 = myfont2.render('GAME OVER!', False, (255,255,255))
#     screen.blit(gameover_text2,((600 - gameover_text2.get_width()) / 2 , (280 - gameover_text2.get_height()) / 2))
#     pygame.display.flip()
#     waiting = True
#     while waiting:
#         clock.tick(FPS)
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()
#             if event.type == pygame.KEYUP:
#                 waiting = False

def regenerate():
    global game_map, constant
    game_map.clear()
    player.current_health = 100
    player.score = 0
    constant = random.randint(3,5)

running = True
gameover = False
# Game loop
while running:
    if gameover:
        show_game_over_screen()
        gameover = False
    if (player.current_health == 0):
        regenerate()


    # Bg color
    display.fill((146,244,255))

    # Camera stuff
    true_scroll[0] += (player_rect.x - true_scroll[0] - 138 ) / 16
    true_scroll[1] += (player_rect.y - true_scroll[1] - 92) / 16
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    # Parallax bg stuff
    # pygame.draw.rect(display, (7,80,75), pygame.Rect(0,120,300,80))
    display.blit(bg_image, (0,0))
    # for background_object in background_objects:
    #     obj_rect = pygame.Rect(background_object[1][0] - (scroll[0]*background_object[0]), background_object[1][1] - (scroll[1]*background_object[0]), background_object[1][2], background_object[1][3])
    #     if background_object[0] == 0.5:
    #         pygame.draw.rect(display, (14,222,150), obj_rect)
    #     else:
    #          pygame.draw.rect(display, (9, 91, 85), obj_rect)

    # Generating chunks
    tile_rects = []
    for y in range(4):
        for x in range(4):
            target_x = x - 1 + int(round(scroll[0] / (CHUNK_SIZE*16)))
            target_y = y - 1 + int(round(scroll[1] / (CHUNK_SIZE*16)))
            target_chunk = str(target_x) + ';' + str(target_y)
            if target_chunk not in game_map:
                if (len(game_map) > 20):
                    player.score += 10
                    player.show_score() 
                game_map[target_chunk] = generate_chunk(target_x, target_y, constant)
                
            for tile in game_map[target_chunk]:
                display.blit(tile_index[tile[1]], (tile[0][0]*16-scroll[0], tile[0][1]*16-scroll[1]))
                tile_object = Tile(tile[1], pygame.Rect(tile[0][0]*16, tile[0][1]*16,16,16), [tile[0][0]*16, tile[0][1]*16])
                tile_rects.append(tile_object)
                # if tile[1] in [1,2]:
                #     tile_rects.append(pygame.Rect(tile[0][0]*16, tile[0][1]*16,16,16))

    # Draw Health Bar
    player.update_health_bar()
    player.show_score()
    player.show_objective()

    # Movement
    player_movement = [0,0]
    if moving_right:
        player_movement[0] += 2 
    if moving_left:
        player_movement[0] -= 2
    player_movement[1] += player_y_momentum
    player_y_momentum += 0.2
    if player_y_momentum > 5:
        player_y_momentum = 5 
    player_rect, collisions = move(player_rect, player_movement, tile_rects)

    # Collision handling
    if collisions['bottom']:
        player_y_momentum = 0
        air_timer = 0
    elif collisions['top']:
        player_y_momentum = 0
        
    else:
        air_timer += 1

    # Drawing player
    display.blit(player_image, (player_rect.x-scroll[0], player_rect.y-scroll[1]))

    if (len(game_map) < 20):
        show_instructions()

    # Event handling
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_d:
                moving_right = True
            if event.key == K_a:
                moving_left = True
            if event.key == K_SPACE:
                if air_timer < 6:
                    player_y_momentum = -5
            # if event.key == K_DOWN:
            #     player.get_damage(10)
            #     print(player.current_health)
            #     player.update_health_bar()
            # if event.key == K_UP:
            #     player.get_health(10)
            #     print(player.current_health)
            #     player.update_health_bar()
        if event.type == KEYUP:
            if event.key == K_d:
                moving_right = False
            if event.key == K_a:
                moving_left = False 
            

    surf = pygame.transform.scale(display, WINDOW_SIZE)
    screen.blit(surf, (0,0))
    pygame.display.update()
    clock.tick(FPS)

