import socket
import select
import pygame
import random
from debuggerOpcodes import *

# Pygame Init
pygame.init()
screen = pygame.display.set_mode([100, 2000])

brain = pygame.Surface([42, 1000])
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
    brain.set_at(tail, color)
    tail[1] += 1

def NextRow():
    tail[1] = 0
    tail[0] += 1

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
        NextRow()
    elif opcode == OPCODE_NewTournament:
        Reset()

def test():
    for i in range(10):
        AddValue(0)
        
    NextRow()

    for i in range(10):
        AddValue(random.randint(0,3))
        
    NextRow()

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
while IsRunning:
    screen.fill([0, 0, 0])

    brainScaled = pygame.transform.scale(brain, screen.get_size())
    screen.blit(brainScaled, [0,0])
    
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
    keystate = pygame.key.get_pressed()
    if keystate[pygame.K_ESCAPE]:
        pygame.quit()
        IsRunning = False

# Shutdown
conn.close()