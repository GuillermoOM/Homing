import math, os, sys, pygame
from random import randint
from pygame.locals import *

WIDTH = 1366
HEIGHT = 768

#Player
acc = 10
maxSpeed = 4
maxTurbo = 7
maxTRate = math.radians(4)
tRateAcc = math.radians(0.4)

#Missiles
respawn_time = 50
mMaxSpeed = 5
Der = 0.002
Inte = 20

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    image = image.convert()
    if colorkey != None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, RLEACCEL)
    return image

class Plane(pygame.sprite.Sprite):
    def __init__(self, init_x, init_y):
        pygame.sprite.Sprite.__init__(self)
        self.imor = load_image("plane.png", -1)
        self.imor = pygame.transform.scale(self.imor, (self.imor.get_width() * 2, self.imor.get_height() * 2))
        self.image = self.imor
        self.rect = self.image.get_rect()
        self.rect.centerx = int(init_x)
        self.rect.centery = int(init_y)
        self.x = float(init_x)
        self.y = float(init_y)
        self.angle = 0
        self.speed = 0
        self.turn_rate = 0
        self.turn_right = False
        self.turn_left = False
        self.turbo = False

    def update(self):
        global acc, maxSpeed, maxTurbo, maxTRate, tRateAcc

        if self.turn_left:
            if self.turn_rate < maxTRate:
                self.turn_rate += tRateAcc
            if self.turn_rate > maxTRate:
                self.turn_rate = maxTRate
        
        elif not (self.turn_left or self.turn_right):
            if self.turn_rate > 0:
                self.turn_rate -= self.turn_rate * 0.1

        if self.turn_right:
            if self.turn_rate > -maxTRate:
                self.turn_rate -= tRateAcc
            if self.turn_rate < -maxTRate:
                self.turn_rate = -maxTRate

        elif not (self.turn_left or self.turn_right):
            if self.turn_rate < 0:
                self.turn_rate -= self.turn_rate * 0.1

        if not (self.turn_left or self.turn_right) and self.turn_rate > -0.01 and self.turn_rate < 0.01:
            self.turn_rate = 0
        
        if self.turbo:
            if self.speed < maxTurbo:
                self.speed += acc
            if self.speed > maxTurbo:
                self.speed = maxTurbo
        else:
            if self.speed > maxSpeed:
                self.speed -= self.speed * 0.05
            if self.speed < maxSpeed:
                self.speed = maxSpeed

        self.angle += self.turn_rate

        self.image = pygame.transform.rotate(self.imor, math.degrees(self.angle))
        self.rect = self.image.get_rect(center=self.rect.center)

        self.x += math.cos(self.angle) * self.speed
        self.y -= math.sin(self.angle) * self.speed

        if self.y > HEIGHT + 20:
            self.y = 0
            self.x = WIDTH - self.x
        if self.x > WIDTH + 20:
            self.x = 0
            self.y = HEIGHT - self.y
            
        if self.y < -20:
            self.y = HEIGHT
            self.x = WIDTH - self.x
        if self.x < -20:
            self.x = WIDTH
            self.y = HEIGHT - self.y

        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

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
        self.x = float(init_x)
        self.y = float(init_y)
        self.health = 100
        self.angle = ang
        self.turn_rate = 0
        self.theta = self.angle
        self.image = pygame.transform.rotate(self.imor, math.degrees(self.angle))
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self, ppos):
        global mMaxSpeed, Der, Inte, WIDTH, HEIGHT
        theta = math.atan2((ppos[1] - self.rect.centery), (self.rect.centerx - ppos[0])) + math.pi
        gamma = self.angle - theta
        if gamma >= math.pi or (-math.pi < gamma and gamma < 0):
            self.turn_rate += (abs(gamma) * Der) - self.turn_rate / Inte
        elif gamma <= -math.pi or (0 < gamma and gamma < math.pi):
            self.turn_rate -= (abs(gamma) * Der) + self.turn_rate / Inte

        self.angle += self.turn_rate
       
        if self.angle > 2*math.pi:
            self.angle -= 2*math.pi
        elif self.angle < 0:
            self.angle += 2*math.pi

        self.image = pygame.transform.rotate(self.imor, math.degrees(self.angle))
        self.rect = self.image.get_rect(center=self.rect.center)

        self.x += math.cos(self.angle) * mMaxSpeed
        self.y -= math.sin(self.angle) * mMaxSpeed

        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

        

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
    pygame.joystick.init()
    pygame.font.init()
    if pygame.joystick.get_count():
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Homing")
    clock = pygame.time.Clock()

    spawn_time = 150
    global respawn_time
    Score = 0
    playing = True

    # content
    timeText = pygame.font.Font(None, 30)
    missiles = pygame.sprite.Group()
    explotions = pygame.sprite.Group()
    player = Plane(WIDTH/2, HEIGHT/2)
    playersprite = pygame.sprite.Group(player)

    # loop
    while 1:
        clock.tick(60)
        pygame.display.update()
        screen.fill((100, 100, 100))

        if playing:
            Score = Score + clock.get_time()/1000

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
                spawn_time = respawn_time

            # Event handler
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        player.turbo = True
                    if event.key == K_LEFT:
                        player.turn_left = True
                    elif event.key == K_RIGHT:
                        player.turn_right = True
                if event.type == KEYUP:
                    if event.key == K_SPACE:
                        player.turbo = False
                    if event.key == K_LEFT:
                        player.turn_left = False
                    elif event.key == K_RIGHT:
                        player.turn_right = False
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        player.turbo = True
                if event.type == pygame.JOYBUTTONUP:
                    if event.button == 0:
                        player.turbo = False
                if event.type == pygame.JOYHATMOTION:
                    if event.value == (-1, 0):
                        player.turn_left = True
                    elif event.value == (1, 0):
                        player.turn_right = True
                    elif event.value == (0, 0):
                        player.turn_left = False
                        player.turn_right = False

            for m in missiles:
                if m.rect.bottom > HEIGHT + 20 or m.rect.right > WIDTH + 20 or m.rect.top < -20 or m.rect.left < -20:
                    missiles.remove(m)
                for s in pygame.sprite.spritecollide(m, missiles, False):
                    if s != m:
                        explotions.add(Explotion(s.rect.centerx, s.rect.centery))
                        explotions.add(Explotion(m.rect.centerx, m.rect.centery))
                        missiles.remove(m)
                        missiles.remove(s)

                for s in pygame.sprite.spritecollide(m, playersprite, False):
                    playing = False
            
            playersprite.update()
            missiles.update(player.rect.center)
            explotions.update()
            missiles.draw(screen)
            explotions.draw(screen)
            playersprite.draw(screen)

            if not playing:
                missiles.empty()
                playersprite.empty()
                del player

        else:
            screen.blit(timeText.render("Game Over", True, (255,255,255)), (int(WIDTH/2)-50,int(HEIGHT/2)))
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        Score = 0
                        playing = True
                        player = Plane(WIDTH/2, HEIGHT/2)
                        playersprite.add(player)

        # Draw EEERRRRYTHING


        screen.blit(timeText.render("Time: {}".format(int(Score)), True, (255,255,255)), (20,20))

        pygame.display.flip()

if __name__ == '__main__': main()


# Control Xbox:

# A: 0
# B: 1
# X: 2
# Y: 3
# LB: 4
# RB: 5
# BACK: 6
# START: 7
# LS: 8
# RS: 9
# HAT: (x, y)
# LSA: (AxisX: 0, AxisY: 1)
# RSA: (AxisX: 4, AxisY: 3)
# LT: Axis2+
# RT: Axis2-