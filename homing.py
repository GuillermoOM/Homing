#Mini homing missiles that follow your mouse!

import math, pygame, os, sys
from random import randint
from pygame.locals import *

WIDTH = 1366
HEIGHT = 768

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, RLEACCEL)
    return image

class Missile(pygame.sprite.Sprite):
    def __init__(self, init_x, init_y, ang):
        pygame.sprite.Sprite.__init__(self)
        self.destroyed = False
        self.imor = load_image("missile.png", -1)
        self.imor = pygame.transform.scale(self.imor, (self.imor.get_width() * 2, self.imor.get_height() * 2))
        self.image = self.imor
        self.rect = self.image.get_rect()
        self.rect.centerx = init_x
        self.rect.centery = init_y
        self.health = 100
        self.angle = ang
        self.theta = self.angle
        self.speed = 3
        self.turn_rate = math.radians(2)
        self.image = pygame.transform.rotate(self.imor, math.degrees(self.angle))
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        mpos = pygame.mouse.get_pos()
        theta = math.atan2((mpos[1] - self.rect.centery), (self.rect.centerx - mpos[0])) + math.pi
        gamma = self.angle - theta
        if gamma >= math.pi or (-math.pi < gamma and gamma < 0):
            self.angle += self.turn_rate
        elif gamma <= -math.pi or (0 < gamma and gamma < math.pi):
            self.angle -= self.turn_rate
        if self.angle > 2*math.pi:
            self.angle -= 2*math.pi
        elif self.angle < 0:
            self.angle += 2*math.pi

        self.image = pygame.transform.rotate(self.imor, math.degrees(self.angle))
        self.rect = self.image.get_rect(center=self.rect.center)

        self.rect.x += int(math.cos(self.angle) * self.speed)
        self.rect.y -= int(math.sin(self.angle) * self.speed)

class Explotion(pygame.sprite.Sprite):
    def __init__(self, init_x, init_y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.images.append(load_image("b1.png", -1))
        self.images.append(load_image("b2.png", -1))
        self.images.append(load_image("b3.png", -1))
        self.images.append(load_image("b4.png", -1))
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.centerx = init_x
        self.rect.centery = init_y
        self.counter = 0

    def update(self):
        if self.index == len(self.images):
            self.kill()
        else:
            if self.counter == 3:
                self.image = self.images[self.index]
                self.index += 1
                self.counter = 0
            self.counter += 1

def main():
    # initialize
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Homing")
    clock = pygame.time.Clock()

    spawn_time = 150

    # content
    missiles = pygame.sprite.Group()
    explotions = pygame.sprite.Group()

    # loop
    while 1:
        clock.tick(60)

        # Event handler
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
        for m in missiles:
            if m.rect.bottom > HEIGHT + 20 or m.rect.right > WIDTH + 20 or m.rect.top < -20 or m.rect.left < -20:
                missiles.remove(m)
            for s in pygame.sprite.spritecollide(m, missiles, False):
                if s != m:
                    explotions.add(Explotion(s.rect.centerx, s.rect.centery))
                    explotions.add(Explotion(m.rect.centerx, m.rect.centery))
                    missiles.remove(m)
                    missiles.remove(s)
        
        # Handle Sprites
        spawn_time -= 1
        if spawn_time <= 0:
            spawn_origin = randint(1, 4)
            if spawn_origin == 1:
                missiles.add(Missile(randint(0, WIDTH), 0, math.pi * 1.5))
            elif spawn_origin == 2:
                missiles.add(Missile(randint(0, WIDTH), HEIGHT, math.pi * 0.5))
            elif spawn_origin == 3:
                missiles.add(Missile(0, randint(0, HEIGHT), 0))
            elif spawn_origin == 4:
                missiles.add(Missile(WIDTH, randint(0, HEIGHT), math.pi))
            spawn_time = 30

        # Draw EEERRRRYTHING
        missiles.update()
        explotions.update()
        pygame.display.update()

        screen.fill((100, 100, 100))
        missiles.draw(screen)
        explotions.draw(screen)

        pygame.display.flip()

if __name__ == '__main__': main()