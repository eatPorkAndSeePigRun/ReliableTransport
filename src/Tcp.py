class Tcp(object):
    """ 这里是要你实现的函数 """

    def __init__(self, **kw):
        pass

    def update(self, timestamp):
        """ 这个函数可以看做 操作系统稳定每隔一小段时间调用一次
        可能有一些定时任务 定时器可以放在这里实现
        """

    def send(self, binary):
        """ 应用程序要发 一段二进制数据出去
        要求实现这个函数的语义 跟socket.send()一样
        这个函数不能block
        """
        return n

    def recv(self, n):
        """ 应用程序要收 n个字节的数据
        要求实现这个函数的语义 跟socket.recv()一样
        这个函数不能block

        没有数据可以拿的时候 要求返回 err == -1
        """
        return binary, err

    def input(self, binary):
        """
        网卡收到数据包 转给给Tcp栈处理 重排乱序包的顺序之类
        """
