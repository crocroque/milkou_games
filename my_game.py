import pygame
import animation
import os
import json


class Player(animation.AnimateSprite):
    def __init__(self, screen: pygame.Surface, sprite_name: str):
        super().__init__(sprite_name=sprite_name)

        self.sprite_name = sprite_name
        self.animations_dict = self.animations.get(sprite_name)
        self.direction = "droite"

        self.rect = self.image.get_rect()

        self.screen = screen

        self.velocity = 10
        self.vel_y = 0
        self.vel_x = 0

        self.hauteur_saut = 25

        self.gravite = 1 # plus c'est haut plus il est lourd

        self.sol_coor = 100000

        self.droite_touche = pygame.K_RIGHT
        self.gauche_touche = pygame.K_LEFT
        self.saut_touche = pygame.K_UP

        self.is_running = False
        self.is_jumping = True

        self.in_block = False

        self.fruits = 0

    def collide(self, objects: list, dx):
        self.rect.x += dx

        collided_object = None
        for obj in objects:
            if obj.rect.top != self.sol_coor:
                if pygame.sprite.collide_mask(self, obj):
                    collided_object = obj
                    break

        self.rect.x += -dx

        return collided_object

    def loop(self, blocks: list, offset_x: int, offset_y: int):

        keys = pygame.key.get_pressed()

        # ANTI FALL DANS LE VIDE A SUPPR
        if self.rect.y > self.screen.get_width():
            self.rect.y = 0
        # FIN ANTI FALL


        for block in blocks:
            if pygame.sprite.collide_mask(self, block):
                if self.vel_y > 0: # tombe
                    self.sol_coor = block.rect.top
                    self.vel_y = 0 # player sur le block donc on stop la chute

                elif self.vel_y < 0: # monte
                    self.rect.top = block.rect.bottom
                    self.vel_y *= -1 # tete de player touche le bas du block donc on le fait retomber

                self.in_block = True

                break

            self.in_block = False

        if not self.in_block:
            self.sol_coor = 10000

        collide_right = self.collide(blocks, self.velocity)
        collide_left = self.collide(blocks, -self.velocity)


        if keys[self.droite_touche] and not collide_right:
            self.direction = "droite"
            self.vel_x = self.velocity

            if not self.is_jumping:
                self.images = self.animations_dict["run"]["droite"]
                self.start_animation()

                self.is_running = True

        elif keys[self.gauche_touche] and not collide_left:
            self.direction = "gauche"
            self.vel_x = -self.velocity

            if not self.is_jumping:
                self.images = self.animations_dict["run"]["gauche"]
                self.start_animation()

                self.is_running = True

        else:
            self.vel_x = 0
            self.is_running = False

        if keys[self.saut_touche]:
            if self.rect.bottom >= self.sol_coor:
                self.vel_y = -self.hauteur_saut

                self.is_jumping = True

        if not self.is_jumping and not self.is_running: # si le joueur est immobile
            self.images = self.animations_dict["idle"][self.direction]
            self.start_animation()

        if self.is_jumping:
            self.images = self.animations_dict["jump"][self.direction]
            self.start_animation()

        else:
            self.is_jumping = False

        # Mettre à jour la position du joueur

        self.rect.x += self.vel_x

        self.vel_y += self.gravite
        self.rect.y += self.vel_y

        # Assurer que le joueur ne tombe pas en dessous du sol
        if self.rect.bottom > self.sol_coor:
            self.rect.bottom = self.sol_coor + 1
            self.vel_y = 0
            self.is_jumping = False

        self.animate()

        self.screen.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))

    def standing_animation(self, x, y):
        self.images = self.animations_dict["idle"][self.direction]

        self.start_animation()

        self.animate()

        self.rect.x, self.rect.y = (x, y)

        self.screen.blit(self.image, (x, y))


class Fruit(animation.AnimateSprite):
    def __init__(self, screen: pygame.Surface, sprite_name: str, x, y):
        super().__init__(sprite_name=sprite_name)

        self.screen = screen

        self.rect = self.image.get_rect()

        self.rect.x, self.rect.y = (x, y)

        self.collected = False
        self.is_anim_played = False
        self.collected_animations = self.animations.get(sprite_name)["collected"]["droite"]

    def loop(self, offset_x, offset_y, player: Player):
        if not self.is_anim_played:
            self.start_animation()
            self.animate()
            # Dessiner le fruit ou l'animation de collecte si nécessaire
            if not self.collected:
                self.screen.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))
            elif self.collected and not self.is_anim_played:
                self.screen.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))
                # Si l'animation de collecte est terminée, marquer comme jouée
                if self.image == self.images[-1]:
                    self.is_anim_played = True

            # Vérifier la collision avec le joueur
            if self.rect.colliderect(player.rect) and not self.collected:
                self.images = self.collected_animations
                self.collected = True

                player.fruits += 1



class Pnj(animation.AnimateSprite):
    def __init__(self, screen: pygame.Surface, sprite_name: str, x, y):
        super().__init__(sprite_name=sprite_name)
        self.screen = screen

        self.rect = self.image.get_rect()

        self.rect.x, self.rect.y = (x, y)

        self.press_e_img = pygame.image.load("assets/Menu/Buttons/press_e.png")
        self.press_e_rect = self.press_e_img.get_rect()

        self.press_e_rect.x, self.press_e_rect.y = (self.rect.x + 120, self.rect.y + 10)

        self.message = Text(screen=screen, letter_size=(20, 16))
        self.text = "Oh salut camarade !\ncomment vas-tu ?\nil parait que tu veux \nen apprendre plus sur milkou ?\nramene moi mes pommes \net je t'en dirais plus ! "

        self.message_spawn = False

    def loop(self, offset_x, offset_y, player: Player):
        self.start_animation()
        self.animate()

        self.screen.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))

        if self.message_spawn:
            self.message.place(text=self.text, x=self.rect.x, y=self.rect.y - 125, offset_x=offset_x, offset_y=offset_y)

        if self.rect.colliderect(player.rect) and not self.message_spawn:
            self.screen.blit(self.press_e_img, (self.press_e_rect.x - offset_x, self.press_e_rect.y - offset_y))

            if pygame.key.get_pressed()[pygame.K_e]:
                self.message_spawn = True


class Block(pygame.sprite.Sprite):
    def __init__(self, sprite_name: str, size: tuple = (48, 48), block_folder: str = ""):
        super().__init__()


        self.image = pygame.transform.scale(pygame.image.load(f"assets/{block_folder}{sprite_name}.png").convert(), size)
        self.rect = self.image.get_rect()

        self.size = size

        self.collision = True

    def place(self, x, y):
        self.rect.x = self.size[0] * x
        self.rect.y = self.size[0] * y


class Text(pygame.sprite.Sprite):
    def __init__(self, screen: pygame.Surface, letter_size: tuple = (20, 16)):
        super().__init__()

        self.screen = screen

        self.letter_size = letter_size
        self.letters = {}

        for i in os.listdir("assets/Menu/Text"):
            self.letters[i.split(".png")[0]] = pygame.transform.scale(pygame.image.load(f"assets/Menu/Text/{i}"), self.letter_size)


    def blit_char(self, text, x, y, offset_x, offset_y):
        x_coor_mot = 1
        y_coor_mot = 1

        for m in text:
            if m == "\n":
                y_coor_mot += 1
                x_coor_mot = 0

            if m == " ":
                letter = "blank"

            elif m == "?":
                letter = "interrogation"

            elif m == ".":
                letter = "dot"

            elif m == ":":
                letter = "double_dot"

            elif m == "!":
                letter = "exclamation"

            elif m == "+":
                letter = "plus"

            elif m == "-":
                letter = "minus"

            elif m == ")":
                letter = "parenthese_ferme"

            elif m == "(":
                letter = "parenthese_ouvert"

            elif m == ",":
                letter = "virgule"
            else:
                letter = m.upper()

            try:
                self.screen.blit(self.letters[letter], (x + self.letter_size[0] * x_coor_mot - offset_x, y + self.letter_size[1] * y_coor_mot - offset_y))

            except:
                letter = "blank"
                self.screen.blit(self.letters[letter], (x + self.letter_size[0] * x_coor_mot - offset_x, y + self.letter_size[1] * y_coor_mot - offset_y))

            x_coor_mot += 1

    def place(self, text, x, y, offset_x, offset_y):
        self.blit_char(text, x, y, offset_x, offset_y)


class Menu:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen


        self.main_menu_img = pygame.transform.scale(pygame.image.load("assets/Menu/MainMenu.png"), self.screen.get_size())

        self.is_main_menu = True
        self.is_level1 = True

        self.player = Player

        self.blocks = []
        self.bg_blocks = []
        self.visible_blocks = []
        self.size_block = (128, 128)
        self.blocks_distance_spawning = 70

        self.offset_x = 0
        self.scroll_area_width_right = 500
        self.scroll_area_width_left = 200

        self.offset_y = 0
        self.scroll_area_height_top = 100
        self.scroll_area_height_bottom = 300

        self.play_button_img = pygame.transform.scale(pygame.image.load("assets/Menu/Buttons/Play.png"), (100, 100))
        self.play_button_img_hover = pygame.transform.scale(pygame.image.load("assets/Menu/Buttons/Play.png"), (110, 110))

        self.personnages_name = ["PinkMan", "VirtualGuy", "NinjaFrog", "MaskDude"]
        self.personnages = {}

        self.pnjs = []

        self.fruits = []

        for i, m in enumerate(self.personnages_name):
            self.personnages[m] = [Player(screen=self.screen, sprite_name=m), self.play_button_img.get_rect()]

    def update(self):
        if self.is_main_menu:
            self.main_menu()

        elif self.is_level1:
            self.level1(self.player)

        if pygame.key.get_pressed()[pygame.K_a]:
            self.is_main_menu = True

    def main_menu(self):
        self.screen.blit(self.main_menu_img, (0, 0))

        for i, m in enumerate(self.personnages.values()):
            m[0].standing_animation(x=300 * i + 100, y=450)

            m[1].center = m[0].rect.center
            m[1].y = 650

            if m[1].collidepoint(pygame.mouse.get_pos()):
                self.screen.blit(self.play_button_img_hover, m[1])

                if pygame.mouse.get_pressed(3)[0]:
                    self.player = m[0]

                    self.is_level1 = True
                    self.is_main_menu = False

                    self.init_level1(bg_color="Yellow")

            else:
                self.screen.blit(self.play_button_img, m[1])


    def get_offsets(self, player: Player):
        # offset_x
        if (player.rect.right - self.offset_x >= self.screen.get_width() - self.scroll_area_width_right) and player.vel_x > 0:
            self.offset_x += player.vel_x

        elif (player.rect.left - self.offset_x <= self.scroll_area_width_left) and player.vel_x < 0 and self.offset_x >= 0:
            self.offset_x += player.vel_x

        # offset_y
        if (player.rect.top - self.offset_y <= self.scroll_area_height_top) and player.vel_y < 0:
            self.offset_y += player.vel_y

        elif (player.rect.bottom - self.offset_y > self.screen.get_height() - self.scroll_area_height_bottom) and player.vel_y > 0:
            self.offset_y += player.vel_y

        if self.offset_y >= 0:
            self.offset_y = 0

    def get_visible_blocks(self):
        self.visible_blocks = []

        for block in self.blocks:
            if -self.blocks_distance_spawning <= block.rect.centerx - self.offset_x <= self.screen.get_width() + self.blocks_distance_spawning: # x verif
                if (0 <= block.rect.top - self.offset_y <= self.screen.get_height()) or (0 <= block.rect.bottom - self.offset_y <= self.screen.get_height()): # y verif
                    self.screen.blit(block.image, (block.rect.x - self.offset_x, block.rect.y - self.offset_y))
                    if block.collision:
                        self.visible_blocks.append(block)

    def del_all_objects(self):
        self.pnjs = []

        self.fruits = []

        self.offset_x = 0
        self.offset_y = 0
        self.blocks = []
        self.bg_blocks = []


    def load_blocks_json(self, file_name):
        def is_surrounded(pos: tuple, block: Block):
            x, y = pos

            surrounded_blocks = 0

            voisins = [
                (x - 1, y - 1), (x - 1, y), (x - 1, y + 1),
                (x, y - 1),                 (x, y + 1),
                (x + 1, y - 1), (x + 1, y), (x + 1, y + 1)
            ]

            for vx, vy in voisins:
                for i in json_content["layers"][0]["tiles"]:
                    if (i["x"], i["y"]) == (vx, vy):
                        surrounded_blocks += 1
                        break

            if surrounded_blocks == 8:
                block.collision = False

        with open(f"assets/Terrain/json_blocks/{file_name}.json", "r") as file:
            json_content = json.load(file)
            file.close()

            map_height = json_content["mapHeight"]

            blocks_image_name = {
                "2": "terre",
                "4": "brique",
                "3": "terre_sable",
                "0": "terre_sans_bord",
                "1": "sous_terre"
            }

            for i in json_content["layers"][0]["tiles"]:
                block = Block(blocks_image_name[i["id"]], self.size_block, block_folder="Terrain/")

                if map_height > 6: # marche uniquement si size_block = (128, 128)
                    block.place(i["x"], 6 - map_height + i["y"] + 1)

                else:
                    block.place(i["x"], i["y"] + 1)


                is_surrounded(pos=(i["x"], i["y"]), block=block)
                self.blocks.append(block)

    def load_bg_blocks(self, bg_color):
        for x in range(self.screen.get_width() // self.size_block[0] + 1):
            for y in range(self.screen.get_height() // self.size_block[1] + 1):
                bg_block = Block(bg_color, self.size_block, block_folder="Background/")

                bg_block.place(x, y)

                self.bg_blocks.append(bg_block)

    def init_level1(self, bg_color: str = "Blue"):
        self.del_all_objects()

        self.load_blocks_json("map")
        self.load_bg_blocks(bg_color)

        self.pnjs.append(Pnj(self.screen, "Chameleon", 1100, 128*5 + 15))

        self.player.rect.center = (200, -200)

        self.fruits_counter = Text(self.screen)

        for i in range(18):
            self.fruits.append(Fruit(self.screen, "Apple", 10 * i + 50, 128*5))


    def level1(self, player: Player):
        for i in self.bg_blocks:
            self.screen.blit(i.image, i.rect)

        self.fruits_counter.place(f"fruits:{player.fruits}", 0, 30, 0, 0)

        self.get_offsets(player=player)
        self.get_visible_blocks()

        player.loop(blocks=self.visible_blocks, offset_x=self.offset_x, offset_y=self.offset_y)

        for fruit in self.fruits:
            fruit.loop(offset_x=self.offset_x, offset_y=self.offset_y, player=player)
        for pnj in self.pnjs:
            pnj.loop(offset_x=self.offset_x, offset_y=self.offset_y, player=player)



def main():
    pygame.init()

    pygame.display.set_caption("Platformer")
    screen_width, screen_height = 1200, 800
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

    fps = 60
    clock = pygame.time.Clock()

    run = True

    menu = Menu(screen)

    fps_txt = Text(screen)

    while run:
        screen.fill((100, 100, 100))
        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
                run = False
                break


        menu.update()

        fps_txt.place(f"fps:{round(clock.get_fps(), 2)}", 0, 0, 0, 0)

        pygame.display.update()
        clock.tick(fps)

    pygame.quit()
    exit()


if __name__ == "__main__":
    main()