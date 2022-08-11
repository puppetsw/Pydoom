import math

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# globals
res = 1
SW = 160 * res
SH = 120 * res
SW2 = SW / 2
SH2 = SH / 2
pixelScale = 4 / res
GLSW = SW * pixelScale
GLSH = SH * pixelScale
tick = 0
numSect = 4
numWall = 16


class Keys(object):
    def __init__(self, w, s, a,d, sl, sr, m):
        self.w = w
        self.s = s
        self.a = a
        self.d = d
        self.sl = sl
        self.sr = sr
        self.m = m


K = Keys(0, 0, 0, 0, 0, 0, 0)


class Time(object):
    def __init__(self, fr1, fr2):
        self.fr1 = fr1
        self.fr2 = fr2


T = Time(0, 0)


class Math(object):
    def __init__(self):
        self.cos = [0] * int(360)
        self.sin = [0] * int(360)


M = Math()


class Player(object):
    def __init__(self, x, y, z, a, l):
        self.x = x
        self.y = y
        self.z = z
        self.a = a
        self.l = l


P = Player(0, 0, 0, 0, 0)


class Wall(object):
    def __init__(self):
        self.x1 = 0  # wall line 1
        self.y1 = 0  # wall line 1
        self.x2 = 0  # wall line 2
        self.y2 = 0  # wall line 2
        self.c = 0  # wall color


W = [Wall()] * int(30)


class Sector(object):
    def __init__(self):
        self.ws = 0  # wall start
        self.we = 0  # wall end
        self.z1 = 0  # bottom wall
        self.z2 = 0  # top wall
        self.d = 0  # add y distances to sort drawing order
        self.surf = [0] * SW  # to hold points for surface
        self.surface = 0  # is there a surface to draw
        self.c1 = 0  # bottom colour
        self.c2 = 0  # top colour


S = [Sector()] * int(30)


def pixel(x, y, c):
    """Draws a pixel at the given x and y coordinates with the given color."""
    rgb = [0, 0, 0]
    if c == 0:
        rgb = [255, 255, 0]
    if c == 1:
        rgb = [160, 160, 0]
    if c == 2:
        rgb = [0, 255, 0]
    if c == 3:
        rgb = [0, 160, 0]
    if c == 4:
        rgb = [0, 255, 255]
    if c == 5:
        rgb = [0, 160, 160]
    if c == 6:
        rgb = [160, 100, 0]
    if c == 7:
        rgb = [110, 50, 0]
    if c == 8:
        rgb = [0, 60, 130]

    glColor3ub(rgb[0], rgb[1], rgb[2])
    glBegin(GL_POINTS)
    glVertex2i(int(x * pixelScale + 2), int(y * pixelScale + 2))
    glEnd()


def move_player():
    if K.a == 1 and K.m == 0:
        # print("left")
        P.a -= 4
        if P.a < 0:
            P.a += 360
    if K.d == 1 and K.m == 0:
        # print("right")
        P.a += 4
        if P.a > 359:
            P.a -= 360

    dx = M.sin[P.a] * 10
    dy = M.cos[P.a] * 10

    if K.w == 1 and K.m == 0:
        # print("forward")
        P.x += dx
        P.y += dy
    if K.s == 1 and K.m == 0:
        # print("backward")
        P.x -= dx
        P.y -= dy
    if K.sr == 1:
        # print("strafe left")
        P.x += dy
        P.y -= dx
    if K.sl == 1:
        # print("strafe right")
        P.x -= dy
        P.y += dx
    if K.a == 1 and K.m == 1:
        # print("look up")
        P.l -= 1
    if K.d == 1 and K.m == 1:
        # print("look down")
        P.l += 1
    if K.w == 1 and K.m == 1:
        # print("move up")
        P.z -= 4
    if K.s == 1 and K.m == 1:
        # print("move down")
        P.z += 4


def clear_background():
    x = 0
    y = 0
    for y in range(SH):
        for x in range(SW):
            pixel(x, y, 8)


def clip_behind_player(x1, y1, z1, x2, y2, z2):
    da = y1
    db = y2
    d = da-db
    if d == 0:
        d = 1
    s = da / (da - db)

    x1 = x1 + s * (x2 - x1)
    y1 = y1 + s * (y2 - y1)
    if y1 == 0:
        y1 = 1
    z1 = z1 + s * (z2 - z1)

    return x1, y1, z1, x2, y2, z2


def draw_wall(x1, x2, b1, b2, t1, t2, c, s):
    dyb = b2 - b1
    dyt = t2 - t1
    dx = x2 - x1
    if dx == 0:
        dx = 1
    xs = x1

    # clip x
    if x1 < 1:
        x1 = 1
    if x2 < 1:
        x2 = 1
    if x1 > SW - 1:
        x1 = SW - 1
    if x2 > SW - 1:
        x2 = SW - 1

    for x in range(int(x1), int(x2)):
        y1 = dyb * (x - xs + 0.5) / dx + b1
        y2 = dyt * (x - xs + 0.5) / dx + t1

        # clip y
        if y1 < 1:
            y1 = 1
        if y2 < 1:
            y2 = 1
        if y1 > SH - 1:
            y1 = SH - 1
        if y2 > SH - 1:
            y2 = SH - 1

        # surface
        if S[s].surface == 1:
            S[s].surf[x] = y1  # save bottom point
            continue
        if S[s].surface == 2:
            S[s].surf[x] = y2  # save top points
            continue
        if S[s].surface == -1:  # bottom
            for y in range(int(S[s].surf[x]), int(y1)):
                pixel(x, y, S[s].c1)
        if S[s].surface == -2:  # top
            for y in range(int(y2), int(S[s].surf[x])):
                pixel(x, y, S[s].c2)

        for y in range(int(y1), int(y2)):  # normal wall
            pixel(x, y, c)


def dist(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))


# noinspection PyTypeChecker,DuplicatedCode
def draw3d():
    CS = M.cos[P.a]
    SN = M.sin[P.a]

    wx = [0] * 4
    wy = [0] * 4
    wz = [0] * 4

    # order sectors by distance
    for s in range(numSect):
        for w in range(numSect - s - 1):
            if S[w].d < S[w + 1].d:
                temp = S[w]
                S[w] = S[w + 1]
                S[w + 1] = temp

    # draw each sector
    for s in range(numSect):
        # print('Wall Sector:' + str(s))
        S[s].d = 0  # clear distance

        if P.z < S[s].z1:
            S[s].surface = 1  # bottom surface
        elif P.z > S[s].z2:
            S[s].surface = 2  # top surface
        else:
            S[s].surface = 0  # no surface

        for loop in range(2):
            for w in range(S[s].ws, S[s].we):
                # print('Wall Start: ' + str(S[s].ws))
                # print('Wall End: ' + str(S[s].we))

                x1 = W[w].x1 - P.x  # x1 = 40 - P.x
                y1 = W[w].y1 - P.y  # y1 = 10 - P.y
                x2 = W[w].x2 - P.x  # x2 = 40 - P.x
                y2 = W[w].y2 - P.y  # y2 = 290 - P.y

                if loop == 0:
                    swp = x1
                    x1 = x2
                    x2 = swp
                    swp = y1
                    y1 = y2
                    y2 = swp

                # world position x
                wx[0] = x1 * CS - y1 * SN
                wx[1] = x2 * CS - y2 * SN
                wx[2] = wx[0]
                wx[3] = wx[1]

                # world position y
                wy[0] = y1 * CS + x1 * SN
                wy[1] = y2 * CS + x2 * SN
                wy[2] = wy[0]
                wy[3] = wy[1]
                S[s].d += dist(0, 0, (wx[0] + wx[1]) / 2, (wy[0] + wy[1]) / 2)  # store wall distance

                # world position z
                wz[0] = S[s].z1 - P.z + ((P.l * wy[0]) / 32)
                wz[1] = S[s].z1 - P.z + ((P.l * wy[1]) / 32)
                wz[2] = wz[0] + S[s].z2  # wall height
                wz[3] = wz[1] + S[s].z2  # wall height

                # clip behind player
                if wy[0] < 1 and wy[1] < 1:
                    continue

                # point 1 behind player, clip
                if wy[0] < 1:
                    wx0, wy0, wz0, wx1, wy1, wz1 = clip_behind_player(wx[0], wy[0], wz[0], wx[1], wy[1], wz[1])
                    wx2, wy2, wz2, wx3, wy3, wz3 = clip_behind_player(wx[2], wy[2], wz[2], wx[3], wy[3], wz[3])
                    wx[0] = wx0
                    wy[0] = wy0
                    wz[0] = wz0
                    wx[1] = wx1
                    wy[1] = wy1
                    wz[1] = wz1
                    wx[2] = wx2
                    wy[2] = wy2
                    wz[2] = wz2
                    wx[3] = wx3
                    wy[3] = wy3
                    wz[3] = wz3

                # point 2 behind player, clip
                if wy[1] < 1:
                    wx1, wy1, wz1, wx0, wy0, wz0 = clip_behind_player(wx[1], wy[1], wz[1], wx[0], wy[0], wz[0])
                    wx3, wy3, wz3, wx2, wy2, wz2 = clip_behind_player(wx[3], wy[3], wz[3], wx[2], wy[2], wz[2])
                    wx[0] = wx0
                    wy[0] = wy0
                    wz[0] = wz0
                    wx[1] = wx1
                    wy[1] = wy1
                    wz[1] = wz1
                    wx[2] = wx2
                    wy[2] = wy2
                    wz[2] = wz2
                    wx[3] = wx3
                    wy[3] = wy3
                    wz[3] = wz3

                wx[0] = wx[0] * 200 / wy[0] + SW2
                wy[0] = wz[0] * 200 / wy[0] + SH2

                wx[1] = wx[1] * 200 / wy[1] + SW2
                wy[1] = wz[1] * 200 / wy[1] + SH2

                wx[2] = wx[2] * 200 / wy[2] + SW2
                wy[2] = wz[2] * 200 / wy[2] + SH2

                wx[3] = wx[3] * 200 / wy[3] + SW2
                wy[3] = wz[3] * 200 / wy[3] + SH2

                draw_wall(wx[0], wx[1], wy[0], wy[1], wy[2], wy[3], W[w].c, s)

            S[s].d /= (S[s].we - S[s].ws)  # average wall distance
            S[s].surface *= -1  # flip surface


def display():
    if T.fr1-T.fr2 >= 50:
        clear_background()
        move_player()
        draw3d()

        T.fr2 = T.fr1
        glutSwapBuffers()
        glutReshapeWindow(int(GLSW), int(GLSH))

    T.fr1 = glutGet(GLUT_ELAPSED_TIME)
    glutPostRedisplay()


def keys_down(key, x, y):
    pressed_key = key.decode("utf-8")
    if pressed_key == 'w':
        K.w = 1
    if pressed_key == 's':
        K.s = 1
    if pressed_key == 'a':
        K.a = 1
    if pressed_key == 'd':
        K.d = 1
    if pressed_key == 'm':
        K.m = 1
    if pressed_key == ',':
        K.sr = 1
    if pressed_key == '.':
        K.sl = 1


def keys_up(key, x, y):
    key_up = key.decode("utf-8")
    if key_up == 'w':
        K.w = 0
    if key_up == 's':
        K.s = 0
    if key_up == 'a':
        K.a = 0
    if key_up == 'd':
        K.d = 0
    if key_up == 'm':
        K.m = 0
    if key_up == ',':
        K.sr = 0
    if key_up == '.':
        K.sl = 0


# wall start, wall end, z1 height, z2 height, bottom colour, top colour
load_sectors = [0, 4, 0, 40, 2, 3,
                4, 8, 0, 40, 4, 5,
                8, 12, 0, 40, 6, 7,
                12, 16, 0, 40, 0, 1]

# x1, y1, x2, y2, colour
load_walls = [0, 0, 32, 0, 0,
              32, 0, 32, 32, 1,
              32, 32, 0, 32, 0,
              0, 32, 0, 0, 1,

              64, 0, 96, 0, 2,
              96, 0, 96, 32, 3,
              96, 32, 64, 32, 2,
              64, 32, 64, 0, 3,

              64, 64, 96, 64, 4,
              96, 64, 96, 96, 5,
              96, 96, 64, 96, 4,
              64, 96, 64, 64, 5,

              0, 64, 32, 64, 6,
              32, 64, 32, 96, 7,
              32, 96, 0, 96, 6,
              0, 96, 0, 64, 7]


def init():
    for i in range(360):
        M.cos[i] = math.cos(i / 180 * math.pi)
        M.sin[i] = math.sin(i / 180 * math.pi)

    P.x = 70
    P.y = -110
    P.z = 20
    P.a = 0
    P.l = 0

    v1 = 0
    v2 = 0

    # load sectors
    for s in range(numSect):
        S[s] = Sector()
        S[s].ws = load_sectors[v1 + 0]
        # print('Loading sector:' + str(load_sectors[v1 + 0]))
        S[s].we = load_sectors[v1 + 1]
        # print('Loading sector:' + str(load_sectors[v1 + 1]))
        S[s].z1 = load_sectors[v1 + 2]
        # print('Loading sector:' + str(load_sectors[v1 + 2]))
        S[s].z2 = load_sectors[v1 + 3] - load_sectors[v1 + 2]
        # print('Loading sector:' + str(load_sectors[v1 + 3] - load_sectors[v1 + 2]))
        S[s].c1 = load_sectors[v1 + 4]
        S[s].c2 = load_sectors[v1 + 5]
        v1 += 6

        # load walls
        for w in range(S[s].ws, S[s].we):
            W[w] = Wall()
            W[w].x1 = load_walls[v2 + 0]
            # print('Loading wall: ' + str(load_walls[v2 + 0]))
            W[w].y1 = load_walls[v2 + 1]
            # print('Loading wall: ' + str(load_walls[v2 + 1]))
            W[w].x2 = load_walls[v2 + 2]
            # print('Loading wall: ' + str(load_walls[v2 + 2]))
            W[w].y2 = load_walls[v2 + 3]
            # print('Loading wall: ' + str(load_walls[v2 + 3]))
            W[w].c = load_walls[v2 + 4]
            # print('Loading wall: ' + str(load_walls[v2 + 4]))
            v2 += 5


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowPosition(int(GLSW/2), int(GLSH/2))
    glutInitWindowSize(int(GLSW), int(GLSW))
    glutCreateWindow("")
    glPointSize(pixelScale)
    gluOrtho2D(0, GLSW, 0, GLSH)

    init()
    glutDisplayFunc(display)
    glutKeyboardFunc(keys_down)
    glutKeyboardUpFunc(keys_up)
    glutMainLoop()


if __name__ == '__main__':
    main()
