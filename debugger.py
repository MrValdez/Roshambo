import socket
import select
from debuggerOpcodes import *

import pygame
import random
import string

# Pygame Init
pygame.init()
screen = pygame.display.set_mode([640, 480])
font = pygame.font.SysFont("timesnewromans", 15)

maxText = font.render(string.ascii_letters, True, (255,255,255))
maxTextSize = maxText.get_size()
rowMargin = 10
rowBorder = maxTextSize[1]
AInumbers = 42
maxAITurns = 1000
#rowWidth = 1000
rowWidth = screen.get_width()
tileWidth = 10
tileHeight = 10
AIrowHeight = ((int(maxAITurns / (rowWidth / tileWidth)) + 1) * max(tileHeight, maxTextSize[1])) + (rowMargin * 2)
resolution = [rowWidth, AIrowHeight * AInumbers]

print(resolution)
brain = pygame.Surface(resolution)
brain.fill([0, 0, 0])

tail = [0, 0]
def AddValue(value):
    global brain
    if value == 0:
        color = pygame.Color(255, 0, 0)
    elif value == 1:
        color = pygame.Color(0, 255, 0)
    elif value == 2:
        color = pygame.Color(0, 0, 255)
    elif value == 3:
        color = pygame.Color(255, 0, 255)
    else:
        print("Value needs to be 0-3")

    # optimization suggestion: use pygame.surfarray
    for x in range(tileWidth):
        for y in range(tileHeight):
            brain.set_at([tail[0] + x, tail[1] + y], color)
        
    tail[0] += tileWidth
    if tail[0] > rowWidth:
        tail[0] = 0
        tail[1] += rowMargin

def NextAI():
    tail[0] = 0
    tail[1] += rowMargin
    
    AIname = font.render("Iocaine Powder", True, (255,255,255))
    brain.blit(AIname, tail)
    tail[0] = AIname.get_width() + rowMargin
    tail[1] += int(AIname.get_height() / 2) - int(tileHeight / 2)

def Reset():
    tail = [0, 0]

def handleOpcode (opcode):
    if opcode == OPCODE_ActivateLayer0:
        AddValue(0)
    elif opcode == OPCODE_ActivateLayer1:
        AddValue(1)
    elif opcode == OPCODE_ActivateLayer2:
        AddValue(2)
    elif opcode == OPCODE_ActivateLayer3:
        AddValue(3)
    elif opcode == OPCODE_NextAI:
        NextAI()
    elif opcode == OPCODE_NewTournament:
        Reset()

def test():
    for i in range(10):
        AddValue(0)
        
    NextAI()

    for i in range(10):
        AddValue(random.randint(0,3))
        
    NextAI()

#test()

# Network init
port = 42
def setupServer():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #serverSocket.bind((socket.gethostname(), port)     # uncomment to allow access outside of localhost
    serverSocket.bind(("", port))
    serverSocket.setblocking(0)
    serverSocket.listen(1)              # listen to just 1 connection
    
    return serverSocket
    
server = setupServer()
print("server ready")
#(conn, address) = server.accept()  # for blocking
inputSockets = [server]

# Update
IsRunning = True
scale = True
x, y = 0, 0
keystate = pygame.key.get_pressed()
while IsRunning:
    screen.fill([128, 128, 128])

    if scale:
        #brainScaled = pygame.transform.scale(brain, [brain.get_width() * scale, brain.get_height() * scale])
        brainScaled = pygame.transform.scale2x(brain)       #optimization
    else:
        brainScaled = brain
        
    screen.blit(brainScaled, [x, y])
    #screen.blit(brain, [x, y])
    
    timeout = 0
    inputs, outputs, errors = select.select(inputSockets, [], [], timeout)
    
    for conn in inputs:
        if conn is server:
            (client, address) = conn.accept()
            print("Connected from", address)        
            inputSockets.append(client)
        else:
            data = conn.recv(1)
            if not data:
                break
            #print(data)    #uncomment to debug
            if len(data) == 1:
                opcode = data
                handleOpcode (opcode)
            else:
                for opcode in data:
                    handleOpcode (opcode)
    
    pygame.display.update()

    events = pygame.event.get()
    prevkeystate = keystate
    keystate = pygame.key.get_pressed()
    if keystate[pygame.K_ESCAPE]:
        pygame.quit()
        IsRunning = False
        
    if keystate[pygame.K_LEFT]:  x += 1
    if keystate[pygame.K_RIGHT]: x -= 1
    if keystate[pygame.K_UP]:    y += 1
    if keystate[pygame.K_DOWN]:  y -= 1

    if keystate[pygame.K_RIGHTBRACKET] and not prevkeystate[pygame.K_RIGHTBRACKET]: 
        scale = not scale
    if keystate[pygame.K_LEFTBRACKET] and not prevkeystate[pygame.K_LEFTBRACKET]:    
        scale = not scale
     
#    if keystate[pygame.K_RIGHTBRACKET] and not prevkeystate[pygame.K_RIGHTBRACKET]: 
#        scale += 1
#    if keystate[pygame.K_LEFTBRACKET] and not prevkeystate[pygame.K_LEFTBRACKET]:
#        scale -= 1
#    scale = 1 if scale < 1 else scale    
    
# Shutdown
conn.close()