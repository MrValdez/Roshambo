import socket
from debuggerOpcodes import *
import random

port = 42
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", port))
    
    return s
    
conn = connect()
conn.send(OPCODE_NewTournament)

for y in range(0,42):
    for x in range(0, 1000):
        opcode = random.choice([OPCODE_ActivateLayer0, OPCODE_ActivateLayer1, OPCODE_ActivateLayer2, OPCODE_ActivateLayer3])
        conn.send(opcode)
    conn.send(OPCODE_NextAI)

conn.close()
