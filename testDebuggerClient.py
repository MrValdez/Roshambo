import socket
from debuggerOpcodes import *
import random

port = 42
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", port))
    
    return s
   
def NextAI(conn, name):
    conn.send(OPCODE_NextAI)    
    size = len(name)
    conn.send(bytes([size]))        # we send the length of the string first. This is unnecessary in TCP/IP but it is for UDP.
    conn.send(bytes(name, "utf-8"))
    
conn = connect()
conn.send(OPCODE_NewTournament)

NextAI(conn, "foobar")
for y in range(0,42):
    for x in range(0, 1000):
        opcode = random.choice([OPCODE_ActivateLayer0, OPCODE_ActivateLayer1, OPCODE_ActivateLayer2, OPCODE_ActivateLayer3])
        conn.send(opcode)
    NextAI(conn, "foobar")

conn.close()
