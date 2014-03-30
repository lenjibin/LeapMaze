from graphics3d import *
import Leap

WALL_HEIGHT = 2
SPRINT_SPEED = .3
WALK_SPEED = .05
TURN_SPEED = 3
FAST_TURN_SPEED = 6
ROTATION_LIMIT = 70

makeGraphicsWindow(1280, 800,True)

class Controller:
    def __init__(self):
        self.objects = []
        self.nextLevel = False
        self.level = 0
        self.spectate = False
        
    def move(self, world, frame):
        
        if len(frame.hands) > 0:
            hand = frame.hands[0]
            (ax,ay,az) = getCameraRotation()
            distance = hand.sphere_center.z*.0005
            deltax = distance * math.sin(math.radians(ay))
            deltaz = distance * math.cos(math.radians(ay))
            deltay = -distance * math.sin(math.radians(ax))

            distance2 = hand.sphere_center.x * .0003
            deltax += distance2 * math.sin(math.radians(ay+90))
            deltaz += distance2 * math.cos(math.radians(ay+90))
            deltay += -distance2 * math.sin(math.radians(az))
                        
            if world.flight == False:
                deltay = 0
            (x,y,z) = getCameraPosition()

            
            adjustCameraPosition(deltax, deltay, deltaz)
            
            if self.collision() == "win":
                self.nextLevel = True
            elif self.collision():
                collisionX = self.collision2(x+deltax, y, z)
                collisionZ = self.collision2(x, y, z+deltaz)
                if collisionX:
                    adjustCameraPosition(-deltax, 0, 0)
                if collisionZ:
                    adjustCameraPosition(0,0, -deltaz)

            collisionY = y+deltay <= .5
            if collisionY:
                adjustCameraPosition(0,-deltay, 0)
            
        
    def rotate(self, frame):
        
        if len(frame.hands) > 0:
            hand = frame.hands[0]
            # Get the hand's normal vector and direction
            direction = hand.direction
            normal = hand.palm_normal
            adjustCameraRotation(direction.pitch* Leap.RAD_TO_DEG*.05, normal.roll* Leap.RAD_TO_DEG*.04 - direction.yaw* Leap.RAD_TO_DEG*.05, 0)

        (ax,ay,az) = getCameraRotation()
        if ax > 30:
            setCameraRotation(30, ay, az)
        elif ax < -30:
            setCameraRotation(-30, ay, az)

    def collision(self):
        import math
        for eachObject in self.objects:
            (x,y,z) = getCameraPosition()
            (objectX,objectZ,objectType) = (eachObject[0], eachObject[1], eachObject[2])
            if self.spectate == False:
                if objectType == 'w':
                    if abs(x-objectX) <= .6 and abs(z-objectZ) <= .6:
                        return True
                if objectType == 'i':
                    if abs(x-objectX) <= .6 and abs(z-objectZ) <= .6:
                        eachObject[3] = True
                        return "invisWall"
                    else:
                        eachObject[3] = False
                if objectType == 'e':
                    if abs(x-objectX) <= .6 and abs(z-objectZ) <= .6:
                        return "win"

    def collision2(self, x, y, z):
        import math
        for eachObject in self.objects:
            (objectX,objectZ,objectType) = (eachObject[0], eachObject[1], eachObject[2])
            if abs(x-objectX) <= .6 and abs(z-objectZ) <= .6:
                if objectType == 'w':
                    return True
                if objectType == 'i':
                    return "invisWall"
                if objectType == 'e':
                    return "win"

    def drawObjects(self, world):
        for eachObject in self.objects:
            (objectX,objectZ,objectType) = (eachObject[0], eachObject[1], eachObject[2])
            if objectType == 'w':
                draw3D(world.wall, eachObject[0], WALL_HEIGHT/2, eachObject[1])
            elif objectType == 'e':
                draw3D(world.exit, eachObject[0], WALL_HEIGHT/2, eachObject[1])
            elif objectType == 'g':
                draw3D(world.goo, eachObject[0], WALL_HEIGHT/2, eachObject[1])
            elif objectType == 'f':
                draw3D(world.wall, eachObject[0], WALL_HEIGHT/2, eachObject[1])
            elif objectType == 'i':
                if self.spectate == False:
                    if eachObject[3] == True:
                        draw3D(world.glassWall, eachObject[0], WALL_HEIGHT/2, eachObject[1])
                else:
                    draw3D(world.glassWall, eachObject[0], WALL_HEIGHT/2, eachObject[1])


    def changeLevels(self,world):
        if self.nextLevel == True:
            world.mapWidth = 0
            world.mapLength = 0
            self.objects = []
            
            if self.level == 0:
                self.level += 1
                loadMap = open("Maps/rahul's map.txt", 'r')
                lines = loadMap.readlines()
                loadMap.close()
                for line in lines:
                    world.mapWidth = 0
                    for letter in line:
                        world.mapWidth += 1
                    world.mapLength += 1
                    
                world.column = 0
                world.row = 0
                for line in lines:
                    for letter in line:
                        if letter == 'w':
                            self.objects.append((world.row, world.column, 'w'))
                        elif letter == 'p':
                            setCameraPosition(world.row, 1, world.column)
                        elif letter == 'e':
                            self.objects.append((world.row, world.column, 'e'))
                        elif letter == 'i':
                            self.objects.append([world.row, world.column, 'i', False])
                        elif letter == 'g':
                            self.objects.append((world.row, world.column, 'g'))
                        elif letter == 'f':
                            self.objects.append((world.row, world.column, 'f'))
                        world.row += 1
                    world.row = 0
                    world.column += 1
                self.nextLevel = False
                world.floor = Rect3D(world.mapWidth, world.mapLength, texture = "Textures/floor tile.jpg", textureRepeat = world.mapWidth)
                if world.mapWidth > world.mapLength:
                    world.sky = Sphere3D(3 * world.mapWidth, 12, texture = "Textures/sky texture.jpg")
                    setProjection(45,0.01,6 * world.mapWidth)
                    world.sky.angle = 0
                else:
                    world.sky = Sphere3D(3 * world.mapLength, 12, texture = "Textures/sky texture.jpg")
                    setProjection(45,0.01,6 * mapLength)
                    world.sky.angle = 0

            elif self.level == 1:
                self.level += 1
                loadMap = open("Maps/hard map.txt", 'r')
                lines = loadMap.readlines()
                loadMap.close()
                for line in lines:
                    world.mapWidth = 0
                    for letter in line:
                        world.mapWidth += 1
                    world.mapLength += 1
                    
                world.column = 0
                world.row = 0
                for line in lines:
                    for letter in line:
                        if letter == 'w':
                            self.objects.append((world.row, world.column, 'w'))
                        elif letter == 'p':
                            setCameraPosition(world.row, 1, world.column)
                        elif letter == 'e':
                            self.objects.append((world.row, world.column, 'e'))
                        elif letter == 'i':
                            self.objects.append([world.row, world.column, 'i', False])
                        elif letter == 'g':
                            self.objects.append((world.row, world.column, 'g'))
                        elif letter == 'f':
                            self.objects.append((world.row, world.column, 'f'))
                        world.row += 1
                    world.row = 0
                    world.column += 1
                self.nextLevel = False
                world.floor = Rect3D(world.mapWidth, world.mapLength, texture = "Textures/floor tile.jpg", textureRepeat = world.mapWidth)
                if world.mapWidth > world.mapLength:
                    world.sky = Sphere3D(3 * world.mapWidth, 12, texture = "Textures/sky texture.jpg")
                    setProjection(45,0.01,6 * world.mapWidth)
                    world.sky.angle = 0
                else:
                    world.sky = Sphere3D(3 * world.mapLength, 12, texture = "Textures/sky texture.jpg")
                    setProjection(45,0.01,6 * world.mapLength)
                    world.sky.angle = 0
                


def sw(world):

    world.leap_controller = Leap.Controller()
    world.frames = []*10

    world.flight = False
    world.win = False
    
    #makeFog(.3,(1,1,1), 1)
    world.textCanvas = Canvas2D(710,145,1)
    world.controller = Controller()
    world.mapWidth = 0
    world.mapLength = 0
    loadMap = open("Maps/Open Map.txt", 'r')
    lines = loadMap.readlines()
    loadMap.close()
    for line in lines:
        world.mapWidth = 0
        for letter in line:
            world.mapWidth += 1
        world.mapLength += 1
        
    world.column = 0
    world.row = 0
    for line in lines:
        for letter in line:
            if letter == 'w':
                world.controller.objects.append((world.row, world.column, 'w'))
            elif letter == 'p':
                setCameraPosition(world.row, 1, world.column)
            elif letter == 'e':
                world.controller.objects.append((world.row, world.column, 'e'))
            elif letter == 'i':
                world.controller.objects.append([world.row, world.column, 'i', False])
            elif letter == 'g':
                world.controller.objects.append((world.row, world.column, 'g'))
            elif letter == 'f':
                world.controller.objects.append((world.row, world.column, 'f'))
            world.row += 1
        world.row = 0
        world.column += 1

    world.floor = Rect3D(world.mapWidth, world.mapLength, texture = "Textures/floor tile.jpg", textureRepeat = world.mapWidth)
    world.wall = Box3D(1,WALL_HEIGHT,1, texture = "Textures/wall texture.jpg")
    world.glassWall = Box3D(1,WALL_HEIGHT,1, texture = "Textures/glass wall.jpg")
    world.goo = Box3D(1,WALL_HEIGHT,1, texture = "Textures/goo.jpg")
    world.exit = Box3D(1,WALL_HEIGHT,1, texture = "Textures/door.jpg")
    if world.mapWidth > world.mapLength:
        world.sky = Sphere3D(3 * world.mapWidth, 12, texture = "Textures/sky texture.jpg")
        setProjection(45,0.01,6 * world.mapWidth)
        world.sky.angle = 0
    else:
        world.sky = Sphere3D(3 * world.mapLength, 12, texture = "Textures/sky texture.jpg")
        setProjection(45,0.01,6 * mapLength)
        world.sky.angle = 0
    (world.previousX, world.previousY, world.previousZ) = getCameraPosition()
    (world.previousAX, world.previousAY, world.previousAZ) = getCameraRotation()

    world.ball1 = Sphere3D(2, 20, texture='textures/moonmap2k.jpg')
    world.ball2 = Sphere3D(2, 5, colors=["red", "blue", "yellow"])
    world.box1 = Box3D(3, 3, 3, texture='textures/wood116.jpg')
    world.box2 = Box3D(3, 3, 3, colors=["red", "blue", "yellow", "green", "orange", "violet"] )
    world.earth = Sphere3D(2, 36, texture='textures/earthmap1k.jpg')
    world.angle = 0.0
    world.ball3 = Sphere3D(3,12,["red","pink","purple"])
    
    return world

def uw(world):

    world.frames = [world.leap_controller.frame()] + world.frames[:-1]
    currentFrame = world.frames[0]
    
    world.controller.move(world,currentFrame)
    world.controller.rotate(currentFrame)
    world.controller.changeLevels(world)
    world.sky.angle += .2

    world.angle += 1
    
    return world

def kpl(world, key):
    if key == pygame.K_SPACE:
        world.flight = not world.flight
    if key == pygame.K_r and world.win == True:
        sw(world)
    if key == pygame.K_n:
        world.controller.nextLevel = True

addKeyPressedListener(kpl)

def dw(world):
    (x,y,z)= getCameraPosition()
    world.controller.drawObjects(world)
    draw3D(world.sky, x,y,z,45,0,world.sky.angle,1)
    draw3D(world.floor, world.mapWidth/2,0,world.mapLength/2,90,0,0,1)
    if world.controller.level == 0:
        drawString2D(world.textCanvas, "Use the leap motion to get through the mazes!", 5, 5)
        drawString2D(world.textCanvas, "Hold your hand over the device and point your fingers in the direction", 5, 25)
        drawString2D(world.textCanvas, "you want to look! Like you're flying your hand :)", 5, 45)
        drawString2D(world.textCanvas, "Move your hand towards the top of the device to accelerate forwards...", 5, 65)
        drawString2D(world.textCanvas, "backwards to go backwards...", 5, 85)
        drawString2D(world.textCanvas, "and side to side for strafing!", 5, 105)
        drawString2D(world.textCanvas, "Beware the invisible walls! You wont see them till you hit 'em!", 5, 125)
        draw2D(world.textCanvas, 0,0)
    if world.controller.level == 1:
        clearCanvas2D(world.textCanvas)
    if world.controller.level > 1 and world.controller.nextLevel:
        if not world.win:
            adjustCameraRotation(0,180, 0)
            world.win = True
        draw3D(world.ball1, 5, 3, 6, world.angle/3, world.angle, 0)
        draw3D(world.ball2, -5, 9, 7, world.angle, world.angle/5)
        draw3D(world.earth, -3, 7, -8, 0, world.angle, 0)
        draw3D(world.box1, -5, 3, -7, world.angle/5, world.angle, 0)
        draw3D(world.box2, 0, 5, 0, world.angle, world.angle/3, world.angle/5)
        drawString2D(world.textCanvas, "YOU WIN!!!", 5,5, size=70)
        drawString2D(world.textCanvas, "Press space to toggle flight mode and enjoy flying around!", 5,55, size=30)
        drawString2D(world.textCanvas, "Want to play again? Press 'R'", 5, 80, size=30)
        draw2D(world.textCanvas, 0,0)

runGraphics(sw,uw,dw)

