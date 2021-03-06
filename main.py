# clear condition
#
from tetrispieces import tetrispieces as tps
from kickdata import wallkickdata as kd
import time
import random
import pygame
import math


def getunit(x, y):
    magnitude = math.sqrt(x ** 2 + y ** 2)
    return [x / magnitude, y / magnitude] if magnitude != 0 else [0, 0]


class tetris():
    def __init__(self):
        self.hei = 40
        self.wid = 10
        self.field = [[0 for a in range(self.wid)] for a in range(self.hei)]
        self.bag = [0, 1, 2, 3, 4, 5, 6]
        random.shuffle(self.bag)
        self.kickdata = kd()
        self.startx = 3
        self.starty = 18
        self.ps = tps()
        self.ps = self.ps.collated()
        self.ghost = True
        self.lines = 0
        self.goal = 40
        self.points = 0
        self.combo = 0
        self.totallines = 0
        self.v = [0, 0]
        self.h = [-1, -1]
        self.hold = True

    def pygame(self, pg, screen, offset=[200, 100], size=20,
               colors=['#7f7f7f', '#0341AE', '#0000ff', '#ff7f00', '#ffff00', '#00ff00', '#800080', '#ff0000']):
        self.screen = screen
        self.offset = offset
        self.tilesize = size
        self.colors = [pg.Color(x) for x in colors]
        self.pg = pg
        self.combosound = [pygame.mixer.Sound("combo_" + str(a) + '.wav') for a in range(1, 9)]
        self.combobreak = pygame.mixer.Sound('combobreak.wav')

    def newpiece(self):
        self.currentx = self.startx
        self.currenty = self.starty
        self.currentpiece = [self.getnewpiece(), 0]
        if not self.placePiece(self.currentpiece[0], self.currentpiece[1], self.currentx, self.currenty):
            print('blockout')
            return False
        lines = 0
        for line in range(self.hei):
            if not 0 in self.field[line]:
                self.field.pop(line)
                self.field.insert(0, [0 for a in range(self.wid)])
                lines += 1
        if lines > 0:
            self.combo += 1
        else:
            if self.combo > 3:
                self.pg.mixer.Sound.play(self.combobreak)
            self.combo = 0
        if self.combo < 9 and lines > 0:
            self.pg.mixer.Sound.play(self.combosound[self.combo - 1])
        elif lines > 0:
            self.pg.mixer.Sound.play(self.combosound[7])
        self.totallines += lines
        return True

    def move(self, p):
        orig = [self.currentpiece[0], self.currentpiece[1], self.currentx, self.currenty]
        self.removePiece(self.currentpiece[0], self.currentpiece[1], self.currentx, self.currenty)
        if self.placePiece(self.currentpiece[0], self.currentpiece[1], self.currentx + p[0], self.currenty + p[1]):
            self.place(self.currentpiece[0], self.currentpiece[1], self.currentx + p[0], self.currenty + p[1])
            self.currentx = self.currentx + p[0]
            self.currenty = self.currenty + p[1]
            return True
        else:
            if self.placePiece(orig[0], orig[1], orig[2], orig[3]):
                self.place(orig[0], orig[1], orig[2], orig[3])
            return False

    def rotate(self, b):
        self.removePiece(self.currentpiece[0], self.currentpiece[1], self.currentx, self.currenty)
        if b > 0:
            i = 0
            index = self.currentpiece[1]
        else:
            i = 1
            index = self.currentpiece[1] + b
        if self.currentpiece[0] == 0:
            for a in self.kickdata.i[index][i]:
                if self.placePiece(self.currentpiece[0], (self.currentpiece[1] + b) % 4, self.currentx + a[0],
                                   self.currenty + a[1]):
                    self.place(self.currentpiece[0], (self.currentpiece[1] + b) % 4, self.currentx + a[0],
                               self.currenty + a[1])
                    self.currentpiece[1] = (self.currentpiece[1] + b) % 4
                    self.currentx += a[0]
                    self.currenty += a[1]
                    return True
                else:
                    pass
            self.place(self.currentpiece[0], self.currentpiece[1], self.currentx, self.currenty)
            return False
        else:
            for a in self.kickdata.therest[index][i]:
                if self.placePiece(self.currentpiece[0], (self.currentpiece[1] + b) % 4, self.currentx + a[0],
                                   self.currenty + a[1]):
                    self.place(self.currentpiece[0], (self.currentpiece[1] + b) % 4, self.currentx + a[0],
                               self.currenty + a[1])
                    self.currentpiece[1] = (self.currentpiece[1] + b) % 4
                    self.currentx += a[0]
                    self.currenty += a[1]
                    return True
                else:
                    pass
            self.place(self.currentpiece[0], self.currentpiece[1], self.currentx, self.currenty)
            return False

    def getnewpiece(self):
        if len(self.bag) <= 7:
            self.bag += random.sample([0, 1, 2, 3, 4, 5, 6], 6)
        return self.bag.pop(0)

    def setpiece(self, n, r=0):
        self.removePiece(self.currentpiece[0], self.currentpiece[1], self.currentx, self.currenty)
        self.currentx = self.startx
        self.currenty = self.starty
        self.currentpiece = [n, r]
        self.place(self.currentpiece[0], self.currentpiece[1], self.currentx, self.currenty)

    def placePiece(self, n, r, x, y):
        piece = self.ps[n][r]
        return self.check(piece, x, y)

    def removePiece(self, n, r, x, y):
        p = self.ps[n][r]
        l = len(p)
        l2 = len(p[0])
        for ys in range(y, y + l):
            for xs in range(x, x + l2):
                if p[ys - y][xs - x] != 0:
                    self.field[ys][xs] = 0

    def printboard(self):
        for a in self.field[19:]:
            nl = ['#' if x != 0 else '  ' for x in a]
            print(''.join(nl), '|', sep='')

    def printboard2(self):
        if self.ghost and 'self.currentpiece' in locals():
            self.removePiece(self.currentpiece[0], self.currentpiece[1], self.currentx, self.currenty)
            for i in range(self.currenty, 40):
                if not self.placePiece(self.currentpiece[0], self.currentpiece[1], self.currentx, i):
                    g = [
                        self.currentx,
                        i - 1,
                        len(self.ps[self.currentpiece[0]][self.currentpiece[1]]),
                        len(self.ps[self.currentpiece[0]][self.currentpiece[1]][0]),
                        self.currentpiece[0]
                    ]
                    break
            p = self.ps[self.currentpiece[0]][self.currentpiece[1]]
            self.place(self.currentpiece[0], self.currentpiece[1], self.currentx, self.currenty)
        yi = 0
        for y in self.field[20:]:
            xi = 0
            for x in y:
                tx = self.offset[0] + (self.tilesize * xi)
                ty = self.offset[1] + (self.tilesize * yi)
                if x == 0:
                    s = self.pg.Surface((self.tilesize, self.tilesize))
                    s.set_alpha(128)
                    s.fill((200, 200, 200))
                    self.screen.blit(s, (tx, ty))
                    self.pg.draw.rect(self.screen, (10, 10, 10), (tx, ty, self.tilesize, self.tilesize), 1)
                if self.ghost and 'self.currentpiece' in locals():
                    if (xi >= g[0] and
                            xi < g[0] + g[3] and
                            yi + 20 >= g[1] and
                            yi + 20 < g[1] + g[2] and
                            p[(yi + 20) - g[1]][xi - g[0]] != 0):
                        self.pg.draw.rect(self.screen,
                                          tuple([co * 0.7 for co in self.colors[g[4] + 1]]),
                                          (tx, ty, self.tilesize, self.tilesize))
                if x != 0:
                    self.pg.draw.rect(self.screen, self.colors[x], (tx, ty, self.tilesize, self.tilesize))

                #                             self.pg.draw.rect(self.screen,(110,110,110),(tx,ty,self.tilesize, self.tilesize),1)
                xi += 1
            yi += 1
        ys = 0
        for psp in self.bag[:6]:
            p = self.ps[psp][0]
            yi = 0
            for y in p:
                xi = 0
                for x in y:
                    if x != 0:
                        self.pg.draw.rect(self.screen,
                                          self.colors[x],
                                          (self.offset[0] + (self.tilesize * self.wid) + (len(p[0]) * 20) + (
                                                      self.tilesize * xi),
                                           self.offset[1] + (ys * 4 * self.tilesize) + (self.tilesize * yi),
                                           self.tilesize, self.tilesize))
                    xi += 1
                yi += 1
            ys += 1
        if self.h != [-1, -1]:
            p = self.ps[self.h[0]][0]
            yi = 0
            for y in p:
                xi = 0
                for x in y:
                    if x != 0:
                        self.pg.draw.rect(self.screen,
                                          [co * 0.5 if not self.hold else co for co in self.colors[x]],
                                          (self.offset[0] - ((len(p[0]) + 1) * 20) + (self.tilesize * xi),
                                           self.offset[1] + (self.tilesize * yi),
                                           self.tilesize, self.tilesize))
                    xi += 1
                yi += 1
        self.pg.draw.lines(self.screen, (255, 255, 255), False, (
            (T.offset[0], T.offset[1]),
            (T.offset[0], T.offset[1] + (20 * self.tilesize)),
            (T.offset[0] + (self.wid * self.tilesize), T.offset[1] + (20 * self.tilesize)),
            (T.offset[0] + (self.wid * self.tilesize), T.offset[1])
        ), 5)
        f = self.pg.font.SysFont(None, 100)
        cobo = f.render(str(self.goal - self.totallines), True, (0, 0, 0))
        cobo.set_alpha(100)
        self.screen.blit(cobo, cobo.get_rect(
            center=(self.offset[0] + ((self.wid / 2) * self.tilesize), self.offset[1] + ((20 / 2) * self.tilesize))))

    def place(self, n, r, x, y):
        p = self.ps[n][r]
        h = len(p)
        w = len(p[0])
        for ys in range(y, y + h):
            for xs in range(x, x + w):
                p1 = ys - y
                p2 = xs - x
                if p[p1][p2] != 0 and (ys < self.hei and ys >= 0 and xs < self.wid and xs >= 0):
                    self.field[ys][xs] = p[p1][p2]

    def check(self, p, x, y):
        h = len(p)
        w = len(p[0])
        for ys in range(y, y + h):
            for xs in range(x, x + w):
                p1 = ys - y
                p2 = xs - x
                if (p[p1][p2] != 0) and (ys < self.hei and ys >= 0 and xs < self.wid and xs >= 0) and self.field[ys][
                    xs] == 0:
                    pass
                elif p[p1][p2] != 0:
                    return False
                else:
                    pass
        return True

def startanimation(screen):
    starttime=time.time()
    while time.time() - starttime <= 0.5:
        screen.fill(0)
        screen.blit(background_image, [(T.offset[ofs] - originalof[ofs] - 5) / -2 for ofs in range(2)])
        T.printboard2()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.update()
    myfont = pygame.font.Font('./DelaGothicOne-Regular.ttf', 20)
    starttime = time.time()
    while time.time()-starttime<=0.9:
        screen.fill(0)
        screen.blit(background_image, [(T.offset[ofs] - originalof[ofs] - 5) / -2 for ofs in range(2)])
        T.printboard2()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        elp=time.time()-starttime
        myfont = pygame.font.Font('./DelaGothicOne-Regular.ttf', 200-int(200*(elp%0.5)))
        text=myfont.render(str(3-(int(elp/0.3))),False,(255,255,255))
        cente=text.get_rect(center=[wid/2,hei/2])
        screen.blit(text,cente)
        pygame.display.update()


keys = {
    'up': pygame.K_w,
    'down': pygame.K_s,
    'left': pygame.K_a,
    'right': pygame.K_d,
    'rotatec': pygame.K_l,
    'rotatecc': pygame.K_k,
    'hold': pygame.K_SPACE,
    'pause': pygame.K_e
}
T = tetris()
lockingdelay = 0.6
pygame.init()
wid = 800
hei = 600
screen = pygame.display.set_mode([wid, hei])
T.pygame(pygame, screen)
originalof = T.offset
clock = pygame.time.Clock()
running = True
ori = time.time()
timers = [0, 0, 0, 0, 0, 0]
down = 0
hold = True
dire = [True, True]
h = [-1, -1]
das = 0.09
arr = 0.01
velocity = [0, 0]
rotatesound = pygame.mixer.Sound("rotate.wav")
movesound = pygame.mixer.Sound("move.wav")
harddropsound = pygame.mixer.Sound("harddrop.wav")
holdsound = pygame.mixer.Sound("hold.wav")
background_image = pygame.image.load('bg.jpg')
background_image = pygame.transform.scale(background_image, (wid + 10, hei + 10))
getTicksLastFrame = pygame.time.get_ticks()
pygame.font.init()
myfont = pygame.font.Font('./DelaGothicOne-Regular.ttf', 20)
startanimation(screen)
while running:
    screen.fill(0)
    screen.blit(background_image, [(T.offset[ofs] - originalof[ofs] - 5) / -2 for ofs in range(2)])
    cur = time.time()
    t = pygame.time.get_ticks()
    # deltaTime in seconds.
    deltaTime = (t - getTicksLastFrame) / 1000.0
    getTicksLastFrame = t
    clock.tick(30)
    if cur - timers[0] > 0.5:
        timers[0] = cur
        hold = True
        if not T.newpiece():
            running = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYUP:
            if event.key == keys['right']:
                dire[0] == False
                timers[1] = cur
            if event.key == keys['left']:
                dire[1] == False
                timers[1] = cur

        if event.type == pygame.KEYDOWN:
            if event.key == keys['right']:
                dire[0] == True
                if T.move([1, 0]):
                    pygame.mixer.Sound.play(movesound)
                    timers[0] = cur
                    timers[1] = cur


            elif event.key == keys['left']:
                dire[1] == True
                if T.move([-1, 0]):
                    pygame.mixer.Sound.play(movesound)
                    timers[0] = cur
                    timers[2] = cur


            elif event.key == keys['rotatecc']:
                if T.rotate(1):
                    pygame.mixer.Sound.play(rotatesound)
                    timers[0] = cur


            elif event.key == keys['rotatec']:
                if T.rotate(-1):
                    pygame.mixer.Sound.play(rotatesound)
                    timers[0] = cur


            elif event.key == keys['hold']:
                if hold:
                    pygame.mixer.Sound.play(holdsound)
                    hold = False
                    if T.h == [-1, -1]:
                        T.h = T.currentpiece
                        T.setpiece(T.getnewpiece())
                        T.hold = hold
                    else:
                        hold = False
                        T.hold = hold
                        h2 = T.h
                        T.h = T.currentpiece
                        T.setpiece(h2[0])


            elif event.key == keys['up']:
                velocity[1] += (40 - T.currenty) / 2
                while T.move([0, 1]):
                    pass
                if not T.move([0, 1]):
                    pygame.mixer.Sound.play(harddropsound)
                if not T.newpiece():
                    running = False
                hold = True


            elif event.key == keys['pause']:
                pause = True
                pauses = cur
                selected = 0
                while pause:
                    T.printboard2()
                    s = pygame.Surface((wid, hei))
                    s.set_alpha(100)
                    s.fill((0, 0, 0))
                    screen.blit(s, (0, 0))
                    cur = time.time()
                    if cur - pauses < 0.2:
                        percent = (cur - pauses) / 0.2
                    else:
                        percent = 1
                    if not selected == 0:
                        pygame.draw.rect(screen, (100, 100, 100),
                                         (((wid / 2) - 100) * percent, ((hei / 2) - 150), 200 * percent, 100))
                    else:
                        pygame.draw.rect(screen, (100, 100, 100),
                                         (((wid / 2) - 110) * percent, ((hei / 2) - 160), 220 * percent, 120))
                    if not selected == 1:
                        pygame.draw.rect(screen, (100, 100, 100),
                                         (((wid / 2) - 100) * percent, ((hei / 2) + 10), 200 * percent, 100))
                    else:
                        pygame.draw.rect(screen, (100, 100, 100),
                                         (((wid / 2) - 110) * percent, ((hei / 2)), 220 * percent, 120))
                    if not selected == 2:
                        pygame.draw.rect(screen, (100, 100, 100),
                                         (((wid / 2) - 100) * percent, ((hei / 2) + 160), 200 * percent, 100))
                    else:
                        pygame.draw.rect(screen, (100, 100, 100),
                                         (((wid / 2) - 110) * percent, ((hei / 2) + 150), 220 * percent, 120))
                    if cur - pauses > 0.2:
                        resume = myfont.render('Resume', True, (255, 255, 255))
                        text_rect = resume.get_rect(center=((wid / 2), (hei / 2) - 100))
                        screen.blit(resume, text_rect)
                        qu = myfont.render('Restart', True, (255, 255, 255))
                        text_rect = qu.get_rect(center=((wid / 2), (hei / 2) + 60))
                        screen.blit(qu, text_rect)
                        qu = myfont.render('QUIT', True, (255, 255, 255))
                        text_rect = qu.get_rect(center=((wid / 2), (hei / 2) + 160 + 50))
                        screen.blit(qu, text_rect)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_DOWN:
                                selected += 1
                                if selected > 2:
                                    selected = 0
                            if event.key == pygame.K_UP:
                                selected -= 1
                                if selected < 0:
                                    selected = 2
                            if event.key == pygame.K_RETURN:
                                endanimation = cur
                                while cur - endanimation < 0.2:
                                    T.printboard2()
                                    s = pygame.Surface((wid, hei))
                                    s.set_alpha(100)
                                    s.fill((0, 0, 0))
                                    screen.blit(s, (0, 0))
                                    cur = time.time()
                                    percent = 1 - ((cur - endanimation) / 0.2)
                                    if not selected == 0:
                                        pygame.draw.rect(screen, (100, 100, 100), (
                                            ((wid / 2) - 100) * percent, ((hei / 2) - 150), 200 * percent, 100))
                                    else:
                                        pygame.draw.rect(screen, (100, 100, 100), (
                                            ((wid / 2) - 110) * percent, ((hei / 2) - 160), 220 * percent, 120))
                                    if not selected == 1:
                                        pygame.draw.rect(screen, (100, 100, 100), (
                                            ((wid / 2) - 100) * percent, ((hei / 2) + 10), 200 * percent, 100))
                                    else:
                                        pygame.draw.rect(screen, (100, 100, 100),
                                                         (((wid / 2) - 110) * percent, ((hei / 2)), 220 * percent, 120))
                                    if not selected == 2:
                                        pygame.draw.rect(screen, (100, 100, 100), (
                                            ((wid / 2) - 100) * percent, ((hei / 2) + 160), 200 * percent, 100))
                                    else:
                                        pygame.draw.rect(screen, (100, 100, 100), (
                                            ((wid / 2) - 110) * percent, ((hei / 2) + 150), 220 * percent, 120))
                                    for event in pygame.event.get():
                                        if event.type == pygame.QUIT:
                                            running = False
                                    pygame.display.update()
                                if selected == 0:
                                    pause = False
                                elif selected == 1:
                                    h = [-1, -1]
                                    T = tetris()
                                    T.pygame(pygame, screen)
                                    T.newpiece()
                                    hold = True
                                    pause = False
                                    startanimation(screen)
                                elif selected == 2:
                                    running = False
                                    pause = False
                            if event.key == pygame.K_e:
                                endanimation = cur
                                while cur - endanimation < 0.2:
                                    T.printboard2()
                                    s = pygame.Surface((wid, hei))
                                    s.set_alpha(100)
                                    s.fill((0, 0, 0))
                                    screen.blit(s, (0, 0))
                                    cur = time.time()
                                    percent = 1 - ((cur - endanimation) / 0.2)
                                    if not selected == 0:
                                        pygame.draw.rect(screen, (100, 100, 100), (
                                        ((wid / 2) - 100) * percent, ((hei / 2) - 150), 200 * percent, 100))
                                    else:
                                        pygame.draw.rect(screen, (100, 100, 100), (
                                        ((wid / 2) - 110) * percent, ((hei / 2) - 160), 220 * percent, 120))
                                    if not selected == 1:
                                        pygame.draw.rect(screen, (100, 100, 100), (
                                        ((wid / 2) - 100) * percent, ((hei / 2) + 10), 200 * percent, 100))
                                    else:
                                        pygame.draw.rect(screen, (100, 100, 100),
                                                         (((wid / 2) - 110) * percent, ((hei / 2)), 220 * percent, 120))
                                    if not selected == 2:
                                        pygame.draw.rect(screen, (100, 100, 100), (
                                            ((wid / 2) - 100) * percent, ((hei / 2) + 160), 200 * percent, 100))
                                    else:
                                        pygame.draw.rect(screen, (100, 100, 100), (
                                            ((wid / 2) - 110) * percent, ((hei / 2) + 150), 220 * percent, 120))
                                    for event in pygame.event.get():
                                        if event.type == pygame.QUIT:
                                            running = False
                                    pygame.display.update()
                                pause = False
                    pygame.display.update()

    kys = pygame.key.get_pressed()
    if kys[keys['right']] and dire[0]:
        if cur - timers[1] > das and cur - timers[3] > arr:
            timers[3] = cur
            if T.move([1, 0]):
                pygame.mixer.Sound.play(movesound)
            else:
                velocity = [velocity[0] + 2, velocity[1]]

    if kys[keys['left']] and dire[1]:
        if cur - timers[2] > das and cur - timers[4] > arr:
            timers[4] = cur
            if T.move([-1, 0]):
                pygame.mixer.Sound.play(movesound)
            else:
                velocity = [velocity[0] - 2, velocity[1]]

    if (kys[keys['down']] and cur - down > 0.01) or cur - ori > 0.3:
        down = cur
        ori = cur
        if not T.move([0, 1]):
            if kys[keys['down']]:
                velocity[1] += 5
            pass
        else:
            if kys[keys['down']]:
                pygame.mixer.Sound.play(movesound)
            timers[0] = cur

    v2 = ((T.offset[0] - originalof[0]), (T.offset[1] - originalof[1]))
    velocity = [velocity[0] - (deltaTime * (5 * v2[0])), velocity[1] - (deltaTime * (5 * v2[1]))]
    velocity = [nor if abs(nor := velocity[0] * 0.5) > 0.2 else 0,
                nor if abs(nor := velocity[1] * 0.5) > 0.2 else 0]

    T.offset = [T.offset[0] + velocity[0], T.offset[1] + velocity[1]]
    T.hold = hold
    T.printboard2()
    pygame.display.update()

pygame.quit()
