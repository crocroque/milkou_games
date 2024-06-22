import pygame.sprite
import os

pygame.display.init()


class AnimateSprite(pygame.sprite.Sprite):
    def __init__(self, sprite_name: str):
        super().__init__()

        self.animations = {}
        self.animation = False

        self.init_sprite_animations(taille_perso=(128, 128), sprite_name=sprite_name)

        self.image = self.animations.get(sprite_name)["idle"]["droite"][0]
        self.images = self.animations.get(sprite_name)["idle"]["droite"]

        self.current_image = 0

        self.frame_delay = 4
        self.count_delay = self.frame_delay

        print(f"animations ({sprite_name}) : loaded")

    def start_animation(self):
        self.animation = True

    def init_sprite_animations(self, sprite_name, taille_perso: tuple = (128, 128)):
        if sprite_name in ["MaskDude", "NinjaFrog", "PinkMan", "VirtualGuy"]:
            self.animations[sprite_name] = {

                "run":
                    {
                        "droite": load_animation_sprite("Characters", sprite_name, "run", True, taille_perso),
                        "gauche": load_animation_sprite("Characters", sprite_name, "run", False, taille_perso)
                    },

                "idle":
                    {
                        "droite": load_animation_sprite("Characters", sprite_name, "idle", True, taille_perso),
                        "gauche": load_animation_sprite("Characters", sprite_name, "idle", False, taille_perso)
                    },

                "jump":
                    {
                        "droite": load_animation_sprite("Characters", sprite_name, "jump", True, taille_perso),
                        "gauche": load_animation_sprite("Characters", sprite_name, "jump", False, taille_perso)
                    },

                }


        if sprite_name in ["Chameleon"]:
            self.animations[sprite_name] = {
                "idle":
                    {
                        "droite": load_animation_sprite("Characters", sprite_name, "idle", True, (84 * 3, 38 * 3)),
                        "gauche": load_animation_sprite("Characters", sprite_name, "idle", False, (84 * 3, 38 * 3))
                    },
            }

        if sprite_name in ["Apple"]:
            self.animations[sprite_name] = {
                "idle":
                    {
                        "droite": load_animation_sprite("Fruits", sprite_name, "idle", True, (96, 96))
                    },

                "collected":
                    {
                        "droite": load_animation_sprite("Fruits", "Collected", "appear", True, (96, 96))
                    }
            }

    def animate(self):
        self.count_delay -= 1
        if self.animation and self.count_delay == 0:
            self.current_image += 1

            if self.current_image >= len(self.images):
                self.current_image = 0
                self.animation = False

            self.image = self.images[self.current_image]
            self.count_delay = self.frame_delay


def load_animation_sprite(dir_name, sprite_name, animation_name, direction_droite, taille):
    images = []

    dir_path = fr"assets/{dir_name}/{sprite_name}/{animation_name}/"

    if direction_droite:
        for img_name in os.listdir(dir_path):
            image_path = f"{dir_path}{img_name}"

            images.append(pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), taille))

    else:
        for img_name in os.listdir(dir_path):
            image_path = f"{dir_path}{img_name}"

            images.append(pygame.transform.scale(pygame.transform.flip(pygame.image.load(image_path).convert_alpha(), True, False), taille))

    return images
