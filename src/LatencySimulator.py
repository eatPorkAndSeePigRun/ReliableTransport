# coding: utf-8
import random
from binascii import hexlify

from util import *
from Random import *


l = []


def log(fmt, *args):
    if args:
        msg = fmt % args
    else:
        msg = fmt
    l.append(msg)
    if len(l) >= 10000:
        save_log()
        l[:] = []


def save_log():
    with open("log.txt", "a+") as wf:
        wf.write("\n".join(l))
        wf.write("\n")


class LatencySimulator(object):
    """
    这个类的代码不能修改
    class Tcp只能通过 vnet.send() vnet.recv()和这个虚拟网络收发数据
    """

    def __init__(self, from_, to, lost_ratio=10, min_rtt=60, max_rtt=125, nmax=1000):
        self.from_ = from_
        self.to = to
        self.from_to = []
        self.to_from = []

        self.lost_ratio = lost_ratio
        self.min_rtt = min_rtt / 2
        self.max_rtt = max_rtt / 2
        self.rtt = self.max_rtt - self.min_rtt
        self.nmax = nmax
        print "min rtt", self.min_rtt
        print "max rtt", self.max_rtt
        print "rtt", self.rtt

        self.from_random = Random()
        self.to_random = Random()

    def send(self, who, data):
        if who is self.from_:
            if self.from_random.random() < self.lost_ratio:
                log("%s lost %s", who, hexlify(data))
                return
            l = self.from_to
        else:
            if self.to_random.random() < self.lost_ratio:
                log("%s lost %s", who, hexlify(data))
                return
            l = self.to_from
        if len(l) >= self.nmax:
            return
        l.append((data, u(clock() + self.min_rtt + self.rtt * random.random())))

    def recv(self, who):
        if who is self.from_:
            l = self.to_from
        else:
            l = self.from_to
        if l and l[0][1] < clock():
            return l.pop(0)[0]
        return None
