# coding: utf-8
import random


class Random(object):
    """ 这个类的代码不能修改 """
    """ 一个均匀的随机数生成器 """

    def __init__(self, size=100):
        self.size = 0
        self.seeds = []
        for i in range(size):
            self.seeds.append(0)

    def random(self):
        if len(self.seeds) == 0:
            return 0

        if self.size == 0:
            for i in range(len(self.seeds)):
                self.seeds[i] = i
            self.size = len(self.seeds)

        i = random.randint(0, 0xffffffff) % self.size
        x = self.seeds[i]
        self.size -= 1
        self.seeds[i] = self.seeds[self.size]
        return x
