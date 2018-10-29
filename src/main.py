# coding: utf-8
import atexit
from functools import partial
from struct import pack, unpack

from Tcp import *
from LatencySimulator import *


def main():
    log = globals()["log"]
    # log = None
    # interval = 500

    args = locals().copy()
    #args.pop("mode")
    a = Tcp(**args)
    #a.name = "a"
    b = Tcp(**args)
    #b.name = "b"

    vnet = LatencySimulator(a, b, 2, 1, 30, 102400)
    a.output = partial(vnet.send, a)
    b.output = partial(vnet.send, b)

    current = clock()
    slap = current + 0

    while True:

        time.sleep(0.001)

        current = clock()

        a.update(clock())
        b.update(clock())

        # 片段 A1
        while current >= slap:
            packet = "abchina"*1024
            slap += 100000
            assert (a.send(packet) == 0)

        # 片段 A2
        while True:
            hr = vnet.recv(a)
            if hr is None:
                break
            a.input(hr)

        # 片段 A3
        while True:
            hr, err = a.recv(2048)
            if err < 0:
                break

        # 片段 B1
        while True:
            hr = vnet.recv(b)
            if hr is None:
                break
            b.input(hr)

        # 片段 B2
        while True:
            hr, err = b.recv(2048)
            if err < 0:
                break
            #sn, ts = unpack("!II", hr)
            # print "b send %s", sn, ts, current
            #assert (b.send(hr) == 0)

atexit.register(save_log)
main()
