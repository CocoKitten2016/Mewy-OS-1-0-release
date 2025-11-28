namespace SpriteKind {
    export const Wall = SpriteKind.create()
}
/**
 * ---------- prevent walking through walls ----------
 */
/**
 * ---------- end of file ----------
 */
// ---------- INPUT: menu navigation + unified A handler ----------
controller.up.onEvent(ControllerButtonEvent.Pressed, function () {
    if (currentApp != App.Menu) {
        return
    }
    selected = (selected - 1 + menuItems.length) % menuItems.length
    drawMenu()
})
// convert grid (r,c) to pixel center
function gridToPixel(c: number, r: number) {
    totalW = gridCols * CELL
    totalH = gridRows * CELL
    offsetX = Math.floor((160 - totalW) / 2)
    offsetY = Math.floor((120 - totalH) / 2)
    px = offsetX + c * CELL + Math.floor(CELL / 2)
    py = offsetY + r * CELL + Math.floor(CELL / 2)
    return [px, py]
}
controller.B.onEvent(ControllerButtonEvent.Pressed, function () {
    // back to menu from any game
    if (currentApp != App.Menu) {
        destroyAllKinds()
        currentApp = App.Menu
        drawMenu()
    }
})
// ---------- MAZE: generation (recursive backtracker) ----------
function initMazeGrid() {
    mazeGrid = []
    for (let r = 0; r <= gridRows - 1; r++) {
        mazeGrid[r] = []
        for (let c = 0; c <= gridCols - 1; c++) {
            // wall
            // wall
            mazeGrid[r][c] = 0
        }
    }
}
// ---------- SHOOTER: start ----------
function startShooter() {
    destroyAllKinds()
    currentApp = App.Shooter
    scene.setBackgroundColor(7)
    info.setScore(0)
    info.setLife(3)
    shooterEnemyHP = 3
    shooterPlayer = sprites.create(img`
        . 4 4 . 
        4 4 4 4 
        4 4 4 4 
        . 4 4 . 
        `, SpriteKind.Player)
    shooterPlayer.setPosition(20, 60)
    shooterPlayer.setStayInScreen(true)
    controller.moveSprite(shooterPlayer, 100, 100)
    shooterEnemy = sprites.create(img`
        . 2 2 . 
        2 2 2 2 
        2 2 2 2 
        . 2 2 . 
        `, SpriteKind.Enemy)
    shooterEnemy.setPosition(140, 60)
}
sprites.onOverlap(SpriteKind.Player, SpriteKind.Enemy, function (pl, en) {
    if (currentApp != App.Shooter) {
        return
    }
    info.changeLifeBy(-1)
    scene.cameraShake(4, 200)
    pause(300)
    if (info.life() <= 0) {
        game.over(false)
    }
})
// SINGLE A handler (menu select, shooter shoot, maze no-op)
// MAZE: A does nothing (could be used for auto-solve later)
controller.A.onEvent(ControllerButtonEvent.Pressed, function () {
    // MENU select
    if (currentApp == App.Menu) {
        if (selected == 0) {
            startShooter()
            return
        } else if (selected == 1) {
            startMaze()
            return
        } else {
            currentApp = App.ComingSoon
            return
        }
    }
    // SHOOTER shooting
    if (currentApp == App.Shooter) {
        // cost
        info.changeScoreBy(-1)
        sprites.createProjectileFromSprite(img`
            . 1 .
            1 1 1
            . 1 .
        `, shooterPlayer, 160, 0)
        return
    }
})
function spawnMazeSprites() {
    // destroy old walls
    for (let w of mazeWalls) {
        w.destroy()
    }
    mazeWalls = []
    for (let t = 0; t <= gridRows - 1; t++) {
        for (let e = 0; e <= gridCols - 1; e++) {
            if (mazeGrid[t][e] == 0) {
                pos = gridToPixel(e, t)
                wall = sprites.create(image.create(CELL, CELL), SpriteKind.Wall)
                // fill wall image
                for (let yy = 0; yy <= CELL - 1; yy++) {
                    for (let xx = 0; xx <= CELL - 1; xx++) {
                        wall.image.setPixel(xx, yy, 8)
                    }
                }
                wall.setPosition(pos[0], pos[1])
                wall.setFlag(SpriteFlag.Ghost, false)
                mazeWalls.push(wall)
            }
        }
    }
}
controller.down.onEvent(ControllerButtonEvent.Pressed, function () {
    if (currentApp != App.Menu) {
        return
    }
    selected = (selected + 1) % menuItems.length
    drawMenu()
})
sprites.onOverlap(SpriteKind.Projectile, SpriteKind.Player, function (proj, pl) {
    if (currentApp != App.Shooter) {
        return
    }
    proj.destroy()
    info.changeLifeBy(-1)
    if (info.life() <= 0) {
        game.over(false)
    }
})
// ---------- CLEANUP helpers ----------
function destroyAllKinds() {
    sprites.destroyAllSpritesOfKind(SpriteKind.Player)
    sprites.destroyAllSpritesOfKind(SpriteKind.Enemy)
    sprites.destroyAllSpritesOfKind(SpriteKind.Projectile)
    sprites.destroyAllSpritesOfKind(SpriteKind.Food)
    sprites.destroyAllSpritesOfKind(SpriteKind.Wall)
}
// start at (1,1)
function carveMaze() {
    let stack: number[][] = []
    initMazeGrid()
    sr = 1
    sc = 1
    mazeGrid[sr][sc] = 1
    stack.push([sr, sc])
    while (stack.length > 0) {
        let neighbors: number[][] = []
        top = stack[stack.length - 1]
        s = top[0]
        d = top[1]
        // Up
        if (s - 2 > 0 && mazeGrid[s - 2][d] == 0) {
            neighbors.push([s - 2, d])
        }
        // Down
        if (s + 2 < gridRows && mazeGrid[s + 2][d] == 0) {
            neighbors.push([s + 2, d])
        }
        // Left
        if (d - 2 > 0 && mazeGrid[s][d - 2] == 0) {
            neighbors.push([s, d - 2])
        }
        // Right
        if (d + 2 < gridCols && mazeGrid[s][d + 2] == 0) {
            neighbors.push([s, d + 2])
        }
        if (neighbors.length > 0) {
            n = neighbors[randint(0, neighbors.length - 1)]
            nr = n[0]
            nc = n[1]
            let midR = (s + nr) >> 1
            let midC = (d + nc) >> 1
            mazeGrid[midR][midC] = 1
            mazeGrid[nr][nc] = 1
            stack.push([nr, nc])
        } else {
            stack.pop()
        }
    }
}
// ---------- collision: player reaches goal ----------
sprites.onOverlap(SpriteKind.Player, SpriteKind.Food, function (sprite, otherSprite) {
    if (currentApp != App.Maze) {
        return
    }
    game.splash("TIME: " + mazeTimer + "s")
    if (mazeTimer < mazeBest) {
        mazeBest = mazeTimer
        settings.writeNumber("mazeBest", mazeBest)
        game.splash("NEW RECORD!")
    }
    destroyAllKinds()
    currentApp = App.Menu
    drawMenu()
})
// shooter collisions
sprites.onOverlap(SpriteKind.Projectile, SpriteKind.Enemy, function (proj, en) {
    if (currentApp != App.Shooter) {
        return
    }
    proj.destroy()
    shooterEnemyHP += -1
    music.pewPew.play()
    // refund
    info.changeScoreBy(1)
    if (shooterEnemyHP <= 0) {
        en.destroy(effects.disintegrate, 300)
        info.changeScoreBy(10)
        pause(200)
        // respawn enemy
        shooterEnemy = sprites.create(img`
            . 2 2 . 
            2 2 2 2 
            2 2 2 2 
            . 2 2 . 
            `, SpriteKind.Enemy)
        shooterEnemy.setPosition(140, randint(20, 100))
        shooterEnemyHP = 3
    }
})
// ---------- START MAZE ----------
function startMaze() {
    destroyAllKinds()
    currentApp = App.Maze
    scene.setBackgroundColor(6)
    mazeTimer = 0
    carveMaze()
    spawnMazeSprites()
    // place player at start (1,1)
    startPos = gridToPixel(1, 1)
    mazePlayer = sprites.create(img`
        . 7 7 . 
        7 7 7 7 
        7 7 7 7 
        . 7 7 . 
        `, SpriteKind.Player)
    mazePlayer.setPosition(startPos[0], startPos[1])
    controller.moveSprite(mazePlayer, 80, 80)
    mazePlayer.setStayInScreen(true)
    // place goal at opposite corner (gridRows-2, gridCols-2)
    exitR = gridRows - 2
    exitC = gridCols - 2
    // make sure it's open
    // make sure it's open
    mazeGrid[exitR][exitC] = 1
    exitPos = gridToPixel(exitC, exitR)
    mazeGoal = sprites.create(img`
        . 2 2 . 
        2 2 2 2 
        2 2 2 2 
        . 2 2 . 
        `, SpriteKind.Food)
    mazeGoal.setPosition(exitPos[0], exitPos[1])
    // record previous player pos for wall collision revert
    prevX = mazePlayer.x
    prevY = mazePlayer.y
}
// ---------- MENU ----------
function drawMenu() {
    scene.setBackgroundColor(9)
    screen.fill(9)
    screen.printCenter("MEWY OS", 10, 1)
    for (let i = 0; i <= menuItems.length - 1; i++) {
        y = 40 + i * 18
        if (i == selected) {
            // red selection rectangle (stroke)
            screen.drawRect(18, y - 4, 124, 16, 2)
        }
        screen.print(menuItems[i], 30, y, 1)
    }
    screen.printCenter("A = Select   B = Back", 110, 1)
    screen.printCenter("BEST MAZE: " + mazeBest + "s", 100, 1)
}
let y = 0
let prevY = 0
let prevX = 0
let exitPos: number[] = []
let exitC = 0
let exitR = 0
let startPos: number[] = []
let nc = 0
let nr = 0
let n: number[] = []
let d = 0
let s = 0
let top: number[] = []
let sc = 0
let sr = 0
let wall: Sprite = null
let pos: number[] = []
let mazeWalls: Sprite[] = []
let mazeGrid: number[][] = []
let py = 0
let px = 0
let offsetY = 0
let offsetX = 0
let totalH = 0
let totalW = 0
let selected = 0
let gridRows = 0
let gridCols = 0
let CELL = 0
let shooterEnemyHP = 0
let menuItems: string[] = []
let mazeTimer = 0
let mazeGoal: Sprite = null
// --- global vars for maze ---
let mazePlayer: Sprite = null
let shooterEnemy: Sprite = null
// --- global vars for shooter ---
let shooterPlayer: Sprite = null
enum App {
    Boot,
    Menu,
    Shooter,
    Maze,
    ComingSoon
}
let currentApp = App.Boot
menuItems = ["Shooter", "Maze", "Coming Soon"]
shooterEnemyHP = 3
let mazeBest = settings.readNumber("mazeBest")
if (mazeBest == 0) {
    mazeBest = 9999
}
// Maze grid parameters (odd-grid carving)
// number of cell columns (odd carving grid will be 2*MAZE_CELLS_X+1)
let MAZE_CELLS_X = 11
let MAZE_CELLS_Y = 7
// pixel size per grid cell (small so fits 160x120)
CELL = 6
gridCols = MAZE_CELLS_X * 2 + 1
gridRows = MAZE_CELLS_Y * 2 + 1
// 0 = wall, 1 = path
// ---------- BOOT ----------
scene.setBackgroundColor(1)
let logo = sprites.create(img`
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
    `, SpriteKind.Player)
logo.setPosition(80, 50)
logo.say("Mewy OS", 1200)
let mySprite = sprites.create(img`
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
    `, SpriteKind.Player)
mySprite.setPosition(80, 100)
mySprite.sayText("Powerd By: CocoKitten2016", 1200, false)
music.powerUp.play()
pause(1300)
sprites.destroy(mySprite)
logo.destroy()
currentApp = App.Menu
drawMenu()
game.onPaint(function () {
    if (currentApp == App.Menu) {
        drawMenu()
    } else if (currentApp == App.Shooter) {
        screen.printCenter("SHOOTER", 8, 1)
        screen.print("Enemy HP: " + shooterEnemyHP, 2, 2, 1)
        screen.print("Score:" + info.score(), 2, 12, 1)
    } else if (currentApp == App.Maze) {
        // HUD
        screen.print("TIME: " + mazeTimer + "s", 2, 2, 1)
        screen.print("BEST: " + mazeBest + "s", 2, 12, 1)

        // minimap box top-right
        let mapX = 110
        let mapY = 2
        let mapW = 46
        let mapH = 30
        screen.drawRect(mapX, mapY, mapW, mapH, 1)
        // draw player dot and goal dot scaled to map (scale positions)
        if (mazePlayer) {
            let px2 = mapX + Math.floor((mazePlayer.x / 160) * (mapW - 4)) + 1
            let py2 = mapY + Math.floor((mazePlayer.y / 120) * (mapH - 4)) + 1
            screen.fillRect(px2, py2, 2, 2, 7)
        }
        if (mazeGoal) {
            let gx = mapX + Math.floor((mazeGoal.x / 160) * (mapW - 4)) + 1
            let gy = mapY + Math.floor((mazeGoal.y / 120) * (mapH - 4)) + 1
            screen.fillRect(gx, gy, 2, 2, 2)
        }
    } else if (currentApp == App.ComingSoon) {
        screen.fill(9)
        screen.printCenter("COMING SOON", 60, 2)
        screen.printCenter("Press B", 90, 1)
    }
})
game.onUpdate(function () {
    // move is applied by engine on every frame; after a short delay we'll check collisions in next onUpdate
    if (currentApp == App.Maze && mazePlayer) {
        // store previous
        prevX = mazePlayer.x
        prevY = mazePlayer.y
    }
})
// ---------- Maze timer ----------
game.onUpdateInterval(1000, function () {
    if (currentApp == App.Maze) {
        mazeTimer += 1
    }
})
game.onUpdateInterval(20, function () {
    if (currentApp != App.Maze || !(mazePlayer)) {
        return
    }
    // after movement, check overlap with any wall; if overlapping, revert to previous pos
    for (let a of mazeWalls) {
        if (mazePlayer.overlapsWith(a)) {
            mazePlayer.setPosition(prevX, prevY)
            return
        }
    }
})
// enemy AI: chase
game.onUpdateInterval(200, function () {
    if (currentApp != App.Shooter) {
        return
    }
    if (!(shooterEnemy) || !(shooterPlayer)) {
        return
    }
    shooterEnemy.vx = shooterPlayer.x < shooterEnemy.x ? -40 : 40
    shooterEnemy.vy = shooterPlayer.y < shooterEnemy.y ? -40 : 40
})

