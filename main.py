@namespace
class SpriteKind:
    Wall = SpriteKind.create()
"""

---------- prevent walking through walls ----------

"""
"""

---------- end of file ----------

"""
# ---------- INPUT: menu navigation + unified A handler ----------

def on_up_pressed():
    global selected
    if currentApp != App.Menu:
        return
    selected = (selected - 1 + len(menuItems)) % len(menuItems)
    drawMenu()
controller.up.on_event(ControllerButtonEvent.PRESSED, on_up_pressed)

# convert grid (r,c) to pixel center
def gridToPixel(c: number, r: number):
    global totalW, totalH, offsetX, offsetY, px, py
    totalW = gridCols * CELL
    totalH = gridRows * CELL
    offsetX = Math.floor((160 - totalW) / 2)
    offsetY = Math.floor((120 - totalH) / 2)
    px = offsetX + c * CELL + Math.floor(CELL / 2)
    py = offsetY + r * CELL + Math.floor(CELL / 2)
    return [px, py]

def on_b_pressed():
    global currentApp
    # back to menu from any game
    if currentApp != App.Menu:
        destroyAllKinds()
        currentApp = App.Menu
        drawMenu()
controller.B.on_event(ControllerButtonEvent.PRESSED, on_b_pressed)

# ---------- MAZE: generation (recursive backtracker) ----------
def initMazeGrid():
    global mazeGrid
    mazeGrid = []
    s = 0
    while s <= gridRows - 1:
        mazeGrid[s] = []
        d = 0
        while d <= gridCols - 1:
            # wall
            # wall
            mazeGrid[s][d] = 0
            d += 1
        s += 1
# ---------- SHOOTER: start ----------
def startShooter():
    global currentApp, shooterEnemyHP, shooterPlayer, shooterEnemy
    destroyAllKinds()
    currentApp = App.Shooter
    scene.set_background_color(7)
    info.set_score(0)
    info.set_life(3)
    shooterEnemyHP = 3
    shooterPlayer = sprites.create(img("""
            . 4 4 .
            4 4 4 4
            4 4 4 4
            . 4 4 .
            """),
        SpriteKind.player)
    shooterPlayer.set_position(20, 60)
    shooterPlayer.set_stay_in_screen(True)
    controller.move_sprite(shooterPlayer, 100, 100)
    shooterEnemy = sprites.create(img("""
            . 2 2 .
            2 2 2 2
            2 2 2 2
            . 2 2 .
            """),
        SpriteKind.enemy)
    shooterEnemy.set_position(140, 60)

def on_on_overlap(pl, en):
    if currentApp != App.Shooter:
        return
    info.change_life_by(-1)
    scene.camera_shake(4, 200)
    pause(300)
    if info.life() <= 0:
        game.over(False)
sprites.on_overlap(SpriteKind.player, SpriteKind.enemy, on_on_overlap)

# SINGLE A handler (menu select, shooter shoot, maze no-op)
# MAZE: A does nothing (could be used for auto-solve later)

def on_a_pressed():
    global currentApp
    # MENU select
    if currentApp == App.Menu:
        if selected == 0:
            startShooter()
            return
        elif selected == 1:
            startMaze()
            return
        else:
            currentApp = App.ComingSoon
            return
    # SHOOTER shooting
    if currentApp == App.Shooter:
        # cost
        info.change_score_by(-1)
        sprites.create_projectile_from_sprite(img("""
                . 1 .
                1 1 1
                . 1 .
                """),
            shooterPlayer,
            160,
            0)
        return
controller.A.on_event(ControllerButtonEvent.PRESSED, on_a_pressed)

def spawnMazeSprites():
    global mazeWalls, pos, wall
    # destroy old walls
    for w in mazeWalls:
        w.destroy()
    mazeWalls = []
    t = 0
    while t <= gridRows - 1:
        e = 0
        while e <= gridCols - 1:
            if mazeGrid[t][e] == 0:
                pos = gridToPixel(e, t)
                wall = sprites.create(image.create(CELL, CELL), SpriteKind.Wall)
                # fill wall image
                yy = 0
                while yy <= CELL - 1:
                    xx = 0
                    while xx <= CELL - 1:
                        wall.image.set_pixel(xx, yy, 8)
                        xx += 1
                    yy += 1
                wall.set_position(pos[0], pos[1])
                wall.set_flag(SpriteFlag.GHOST, False)
                mazeWalls.append(wall)
            e += 1
        t += 1

def on_down_pressed():
    global selected
    if currentApp != App.Menu:
        return
    selected = (selected + 1) % len(menuItems)
    drawMenu()
controller.down.on_event(ControllerButtonEvent.PRESSED, on_down_pressed)

def on_on_overlap2(proj, pl2):
    if currentApp != App.Shooter:
        return
    proj.destroy()
    info.change_life_by(-1)
    if info.life() <= 0:
        game.over(False)
sprites.on_overlap(SpriteKind.projectile, SpriteKind.player, on_on_overlap2)

# ---------- CLEANUP helpers ----------
def destroyAllKinds():
    sprites.destroy_all_sprites_of_kind(SpriteKind.player)
    sprites.destroy_all_sprites_of_kind(SpriteKind.enemy)
    sprites.destroy_all_sprites_of_kind(SpriteKind.projectile)
    sprites.destroy_all_sprites_of_kind(SpriteKind.food)
    sprites.destroy_all_sprites_of_kind(SpriteKind.Wall)
# start at (1,1)
def carveMaze():
    global sr, sc, top, u, f, n, nr, nc
    stack: List[List[number]] = []
    initMazeGrid()
    sr = 1
    sc = 1
    mazeGrid[sr][sc] = 1
    stack.append([sr, sc])
    while len(stack) > 0:
        neighbors: List[List[number]] = []
        top = stack[len(stack) - 1]
        u = top[0]
        f = top[1]
        # Up
        if u - 2 > 0 and mazeGrid[u - 2][f] == 0:
            neighbors.append([u - 2, f])
        # Down
        if u + 2 < gridRows and mazeGrid[u + 2][f] == 0:
            neighbors.append([u + 2, f])
        # Left
        if f - 2 > 0 and mazeGrid[u][f - 2] == 0:
            neighbors.append([u, f - 2])
        # Right
        if f + 2 < gridCols and mazeGrid[u][f + 2] == 0:
            neighbors.append([u, f + 2])
        if len(neighbors) > 0:
            n = neighbors[randint(0, len(neighbors) - 1)]
            nr = n[0]
            nc = n[1]
            midR = (u + nr) >> 1
            midC = (f + nc) >> 1
            mazeGrid[midR][midC] = 1
            mazeGrid[nr][nc] = 1
            stack.append([nr, nc])
        else:
            stack.pop()
# ---------- collision: player reaches goal ----------

def on_on_overlap3(sprite, otherSprite):
    global mazeBest, currentApp
    if currentApp != App.Maze:
        return
    game.splash("TIME: " + str(mazeTimer) + "s")
    if mazeTimer < mazeBest:
        mazeBest = mazeTimer
        settings.write_number("mazeBest", mazeBest)
        game.splash("NEW RECORD!")
    destroyAllKinds()
    currentApp = App.Menu
    drawMenu()
sprites.on_overlap(SpriteKind.player, SpriteKind.food, on_on_overlap3)

# shooter collisions

def on_on_overlap4(proj2, en2):
    global shooterEnemyHP, shooterEnemy
    if currentApp != App.Shooter:
        return
    proj2.destroy()
    shooterEnemyHP += -1
    music.pew_pew.play()
    # refund
    info.change_score_by(1)
    if shooterEnemyHP <= 0:
        en2.destroy(effects.disintegrate, 300)
        info.change_score_by(10)
        pause(200)
        # respawn enemy
        shooterEnemy = sprites.create(img("""
                . 2 2 .
                2 2 2 2
                2 2 2 2
                . 2 2 .
                """),
            SpriteKind.enemy)
        shooterEnemy.set_position(140, randint(20, 100))
        shooterEnemyHP = 3
sprites.on_overlap(SpriteKind.projectile, SpriteKind.enemy, on_on_overlap4)

# ---------- START MAZE ----------
def startMaze():
    global currentApp, mazeTimer, startPos, mazePlayer, exitR, exitC, exitPos, mazeGoal, prevX, prevY
    destroyAllKinds()
    currentApp = App.Maze
    scene.set_background_color(6)
    mazeTimer = 0
    carveMaze()
    spawnMazeSprites()
    # place player at start (1,1)
    startPos = gridToPixel(1, 1)
    mazePlayer = sprites.create(img("""
            . 7 7 .
            7 7 7 7
            7 7 7 7
            . 7 7 .
            """),
        SpriteKind.player)
    mazePlayer.set_position(startPos[0], startPos[1])
    controller.move_sprite(mazePlayer, 80, 80)
    mazePlayer.set_stay_in_screen(True)
    # place goal at opposite corner (gridRows-2, gridCols-2)
    exitR = gridRows - 2
    exitC = gridCols - 2
    # make sure it's open
    # make sure it's open
    mazeGrid[exitR][exitC] = 1
    exitPos = gridToPixel(exitC, exitR)
    mazeGoal = sprites.create(img("""
            . 2 2 .
            2 2 2 2
            2 2 2 2
            . 2 2 .
            """),
        SpriteKind.food)
    mazeGoal.set_position(exitPos[0], exitPos[1])
    # record previous player pos for wall collision revert
    prevX = mazePlayer.x
    prevY = mazePlayer.y
# ---------- MENU ----------
def drawMenu():
    global y
    scene.set_background_color(9)
    screen.fill(9)
    screen.print_center("MEWY OS", 10, 1)
    i = 0
    while i <= len(menuItems) - 1:
        y = 40 + i * 18
        if i == selected:
            # red selection rectangle (stroke)
            screen.draw_rect(18, y - 4, 124, 16, 2)
        screen.print(menuItems[i], 30, y, 1)
        i += 1
    screen.print_center("A = Select   B = Back", 110, 1)
    screen.print_center("BEST MAZE: " + str(mazeBest) + "s", 100, 1)
y = 0
prevY = 0
prevX = 0
exitPos: List[number] = []
exitC = 0
exitR = 0
startPos: List[number] = []
nc = 0
nr = 0
n: List[number] = []
f = 0
u = 0
top: List[number] = []
sc = 0
sr = 0
wall: Sprite = None
pos: List[number] = []
mazeWalls: List[Sprite] = []
mazeGrid: List[List[number]] = []
py = 0
px = 0
offsetY = 0
offsetX = 0
totalH = 0
totalW = 0
selected = 0
gridRows = 0
gridCols = 0
CELL = 0
shooterEnemyHP = 0
menuItems: List[str] = []
mazeTimer = 0
mazeGoal: Sprite = None
# --- global vars for maze ---
mazePlayer: Sprite = None
shooterEnemy: Sprite = None
# --- global vars for shooter ---
shooterPlayer: Sprite = None
class App(Enum):
    Boot = 0
    Menu = 1
    Shooter = 2
    Maze = 3
    ComingSoon = 4
currentApp = App.Boot
menuItems = ["Shooter", "Maze", "Coming Soon"]
shooterEnemyHP = 3
mazeBest = settings.read_number("mazeBest")
if mazeBest == 0:
    mazeBest = 9999
# Maze grid parameters (odd-grid carving)
# number of cell columns (odd carving grid will be 2*MAZE_CELLS_X+1)
MAZE_CELLS_X = 11
MAZE_CELLS_Y = 7
# pixel size per grid cell (small so fits 160x120)
CELL = 6
gridCols = MAZE_CELLS_X * 2 + 1
gridRows = MAZE_CELLS_Y * 2 + 1
# 0 = wall, 1 = path
# ---------- BOOT ----------
scene.set_background_color(1)
logo = sprites.create(img("""
        . . f f . . . . . . . . . f f . .
        . . f 1 f . . . . . . . f 1 f . .
        . . f 1 1 f . . . . . f 1 1 f . .
        . . f 1 1 1 f f f f f 1 1 1 f . .
        . . f 1 1 1 1 1 1 1 1 1 1 1 f . .
        . f 1 1 1 1 1 1 1 1 1 1 1 1 1 f .
        . f 1 1 f 9 1 1 1 1 1 f 9 1 1 f .
        . f 1 1 f 9 1 1 1 1 1 f 9 1 1 f .
        . f 1 1 1 1 1 1 1 1 1 1 1 1 1 f .
        . f 1 1 1 1 1 1 3 1 1 1 1 1 1 f .
        . . f 1 1 1 1 1 1 1 1 1 1 1 f . .
        . . . f 1 1 1 1 1 1 1 1 1 f . . .
        . . . . f f f f f f f f f . . . .
        """),
    SpriteKind.player)
logo.set_position(80, 50)
logo.say("Mewy OS", 1200)
mySprite = sprites.create(img("""
        . . . . . . . . . . . . . . . .
        . . . . . . . . . . . . . . . .
        . . . . . . . . . . . . . . . .
        . . . . . . . . . . . . . . . .
        . . . . . . . . . . . . . . . .
        . . . . . . . . . . . . . . . .
        . . . . . . . . . . . . . . . .
        . . . . . . . . . . . . . . . .
        . . . . . . . . . . . . . . . .
        . . . . . . . . . . . . . . . .
        . . . . . . . . . . . . . . . .
        . . . . . . . . . . . . . . . .
        . . . . . . . . . . . . . . . .
        . . . . . . . . . . . . . . . .
        . . . . . . . . . . . . . . . .
        . . . . . . . . . . . . . . . .
        """),
    SpriteKind.player)
mySprite.set_position(80, 100)
mySprite.say_text("Powerd By: CocoKitten2016", 1200, False)
music.power_up.play()
pause(1300)
sprites.destroy(mySprite)
logo.destroy()
currentApp = App.Menu
drawMenu()

def on_on_paint():
    if currentApp == App.Menu:
        drawMenu()
    elif currentApp == App.Shooter:
        screen.print_center("SHOOTER", 8, 1)
        screen.print("Enemy HP: " + str(shooterEnemyHP), 2, 2, 1)
        screen.print("Score:" + str(info.score()), 2, 12, 1)
    elif currentApp == App.Maze:
        # HUD
        screen.print("TIME: " + str(mazeTimer) + "s", 2, 2, 1)
        screen.print("BEST: " + str(mazeBest) + "s", 2, 12, 1)
        # minimap box top-right
        mapX = 110
        mapY = 2
        mapW = 46
        mapH = 30
        screen.draw_rect(mapX, mapY, mapW, mapH, 1)
        # draw player dot and goal dot scaled to map (scale positions)
        if mazePlayer:
            px2 = mapX + Math.floor((mazePlayer.x / 160) * (mapW - 4)) + 1
            py2 = mapY + Math.floor((mazePlayer.y / 120) * (mapH - 4)) + 1
            screen.fill_rect(px2, py2, 2, 2, 7)
        if mazeGoal:
            gx = mapX + Math.floor((mazeGoal.x / 160) * (mapW - 4)) + 1
            gy = mapY + Math.floor((mazeGoal.y / 120) * (mapH - 4)) + 1
            screen.fill_rect(gx, gy, 2, 2, 2)
    elif currentApp == App.ComingSoon:
        screen.fill(9)
        screen.print_center("COMING SOON", 60, 2)
        screen.print_center("Press B", 90, 1)
game.on_paint(on_on_paint)

def on_on_update():
    global prevX, prevY
    # move is applied by engine on every frame; after a short delay we'll check collisions in next onUpdate
    if currentApp == App.Maze and mazePlayer:
        # store previous
        prevX = mazePlayer.x
        prevY = mazePlayer.y
game.on_update(on_on_update)

# ---------- Maze timer ----------

def on_update_interval():
    global mazeTimer
    if currentApp == App.Maze:
        mazeTimer += 1
game.on_update_interval(1000, on_update_interval)

def on_update_interval2():
    if currentApp != App.Maze or not (mazePlayer):
        return
    # after movement, check overlap with any wall; if overlapping, revert to previous pos
    for a in mazeWalls:
        if mazePlayer.overlaps_with(a):
            mazePlayer.set_position(prevX, prevY)
            return
game.on_update_interval(20, on_update_interval2)

# enemy AI: chase

def on_update_interval3():
    if currentApp != App.Shooter:
        return
    if not (shooterEnemy) or not (shooterPlayer):
        return
    shooterEnemy.vx = -40 if shooterPlayer.x < shooterEnemy.x else 40
    shooterEnemy.vy = -40 if shooterPlayer.y < shooterEnemy.y else 40
game.on_update_interval(200, on_update_interval3)
