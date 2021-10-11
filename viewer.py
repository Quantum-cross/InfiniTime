
import numpy as np
import socket
from struct import unpack
from matplotlib import pyplot as plt
import re

scrdata_re = re.compile(b'SCRDATA,[0-9]+\r\n')

import sys, pygame
pygame.init()
FULLBUF=False

if FULLBUF:
    size = width, height = 240, 320
else:
    size = width, height = 240, 240

screen = pygame.display.set_mode(size)


buffer = np.zeros((320, 240)).astype(np.uint16)
window = buffer[:,:].ravel()

px0 = 0
px1 = 0
py0 = 0
py1 = 0
pi = 0
def pixdecode(pixel):
    pixel2 = (pixel<<8)
    pixel2 = (pixel>>8) | pixel2
    b = (pixel2 & 0b11111)*8 + 7
    g = ((pixel2>>5) & 0b111111)*4 + 3
    r = ((pixel2>>11) & 0b11111)*8 + 7
    return r, g, b

def linesplit(socket):
    #try:
    #    buffer = socket.recv(1024)
    #except BlockingIOError:
    #    yield None
    buffer = b''
    buffering = True
    while buffering:
        #print(b"bufferstate ", buffer)
        is_scr = False
        if scrdata_re.match(buffer):
            is_scr = True
            #print(buffer)
            #try:
            ex_size = buffer.split(b',', 1)[1]
            ex_size = int(ex_size.split(b'\r\n')[0])
            #except:
                #print("EXCEPTION1")
                #print(buffer)
                #print(ex_size)
                #yield None
            #print("checking SCRDATA ", ex_size)
            try:
                head = buffer.split(b'\r\n', 1)[0]
                data = buffer.split(b'\r\n', 1)[1]
            except IndexError:
                #print("EXCEPTION2")
                #print(data)
                #print(ex_size)
                data = b''
            if len(data) >= ex_size:
                return_data = data[:ex_size]
                buffer = data[ex_size:]
                #print(len(data), ex_size)
                yield head
                yield return_data
            else:
                gotmore = False
                while not gotmore:
                    try:
                        more = socket.recv(1024)
                        gotmore = True
                    except BlockingIOError:
                        gotmore = False
                        yield None
                if not more:
                    buffering = False
                else:
                    buffer += more

        elif b"\r\n" in buffer:
            (line, buffer) = buffer.split(b"\r\n", 1)
            yield line
        else:
            gotmore = False
            while not gotmore:
                try:
                    more = socket.recv(1024)
                    gotmore = True
                except BlockingIOError:
                    gotmore = False
                    yield None
            if not more:
                buffering = False
            else:
                buffer += more
    if buffer:
        yield buffer

def getGesture(x, x0, y, y0):
    if (x == x0) and (y == y0):
        gesture = 'tap'
    elif abs(x-x0) < abs(y-y0):
        if (y-y0) > 0:
            gesture = 'down'
        else:
            gesture = 'up'
    elif (x-x0) > 0:
        gesture = 'right'
    else:
        gesture = 'left'

    gmap = {'none':0, 'down':1, 'up':2, 'left':3, 'right':4,
            'tap':5, 'dtap':11, 'long':12}

    return (gmap[gesture]<<1)

'''
        None = 0x00,
        SlideDown = 0x01,
        SlideUp = 0x02,
        SlideLeft = 0x03,
        SlideRight = 0x04,
        SingleTap = 0x05,
        DoubleTap = 0x0B,
        LongPress = 0x0C
'''

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('localhost', 19021))
    s.setblocking(False)
#     print(s)
    mysock = linesplit(s)
    mx0 = 0
    my0 = 0
    vsp = 0
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                x = min(x, 240)
                y = min(y, 240)
                mx0, my0 = x, y
                gesture = getGesture(x, mx0, y, my0)+1
                print("sending ", gesture, x, y)
                s.send(b'T' + bytes([gesture, x, y]))
            elif event.type == pygame.MOUSEBUTTONUP:
                x, y = event.pos
                x = min(x, 240)
                y = min(y, 240)

                gesture = getGesture(x, mx0, y, my0)
                #print(event.button)
                if gesture == 5<<1 and event.button == 3:
                    gesture = 12<<1
                print("sending ", gesture, x, y)
                s.send(b'U' + bytes([gesture, x, y]))
                #print(0, x, y)
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                x = min(x, 240)
                y = min(y, 240)
                if any(event.buttons):
                    gesture = getGesture(x, mx0, y, my0)+1
                    #print("sending ", gesture, x, y)
                    s.send(b'T' + bytes([gesture, x, y]))
                #print(int(any(event.buttons)), x, y)
        oline = next(mysock)
        if oline is None:
            continue

        #print(b"RETURNED BUFFER: ", oline)
#         for line in linesplit(s):
#         print(line)
        line = oline.strip()
#         print(line)
#         continue
#         idx, mat, nbytes = tn.expect([b"WINDOW,(?P<x0>[0-9]+),(?P<y0>[0-9]+),(?P<x1>[0-9]+),(?P<y1>[0-9]+)",
#                                     b"SCRDATA,(?P<size>[0-9]+)\\n(?P<data>.*)\\nEND\\n"])

        if line.startswith(b"WINDOW"):
            #print("adjusting window")
            #print(oline)
            #print(line.split(b',')[-4:])
            px0, py0, px1, py1 = [int(c) for c in line.split(b',')[-4:]]
            px1+=1
            py1+=1
#             px0, px1, py0, py1 = [int(mat.groupdict()[n]) for n in ['x0', 'x1', 'y0', 'y1']]
            #print(px0, py0, px1, py1)
            window = buffer[py0:py1, px0:px1].ravel()
            pi = 0
        elif line.startswith(b"VSP"):
            #print("vsp")
            vsp = int(line.split(b',')[-1])
        elif line.startswith(b"SCRDATA"):
            #print("screen data")
            #print(oline)
            #print(line)
            size = int(line.split(b',')[1])

            data = None
            while data is None:
                data = next(mysock)
            #print(f"expected size: {size}, actual size: {len(data)}")
            #print(data)
            pixels = unpack("H"*(size//2), data)
            pixels = np.array(pixels).astype(np.uint16).ravel()
            try:
                window[pi:pi+(size//2)] = pixels
            except ValueError as e:
                print("EXCEPTION3")
                print(window.shape, pixels.shape)
                raise e
            pi += len(pixels)
            buffer[py0:py1, px0:px1] = window.reshape((py1-py0, px1-px0))
            print(py0, py1, vsp)
            tbuf = np.empty((320,240,3))
            r, g, b = pixdecode(buffer)
            tbuf[:,:,0] = r
            tbuf[:,:,1] = g
            tbuf[:,:,2] = b
            tbuf = tbuf.transpose((1,0,2))
            tbuf = np.roll(tbuf, -vsp, axis=1)

            if FULLBUF:
                surf = pygame.surfarray.make_surface(tbuf[:,:,:])
            else:
                surf = pygame.surfarray.make_surface(tbuf[:240,:,:])
            screen.blit(surf, (0,0))
            pygame.display.update()
        elif b"Logger task started" in line:
            buffer = np.zeros((320, 240)).astype(np.uint16)
            window = buffer[:,:].ravel()

            px0 = 0
            px1 = 0
            py0 = 0
            py1 = 0
            pi = 0

            vsp=0
        else:
            if line.startswith(b"STCMD"):
                print(line)
            elif not( (line == b'') or (line.startswith(b"STCMD"))):
                print(line)
            pass

