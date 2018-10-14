# coding: utf-8
import json
import time


# window_max_size = 10240

class Tcp(object):
    """ 这里是要你实现的函数 """

    def __init__(self, **kw):
        self.output = None
        self.sndpkt_buffer = []  # 缓存已发送未被确认的pkt
        self.rcvpkt_buffer = []  # 缓存已正常接收的pkt
        self.max_unconfirmed_pkt_num = 500 
        self.start_timer = 0.0  # 定时器 
        self.timeout_interval = 1
        self.mss = 1046
        self.snd_buffer = ""
        self.rcv_buffer = ""
        self.seq = 0
        self.ack = 0
        self.duplicate_ack_num = 0

    def update(self, timestamp):
        """ 这个函数可以看做 操作系统稳定每隔一小段时间调用一次
        可能有一些定时任务 定时器可以放在这里实现
        """
        if timestamp - self.start_timer > self.timeout_interval:
            if not self.sndpkt_buffer:
                return
            sndpkt = self.sndpkt_buffer[0]
            self.output(sndpkt)
            self.start_timer = time.time()
            self.timeout_interval *= 2

    def send(self, binary):
        """ 应用程序要发 一段二进制数据出去
        要求实现这个函数的语义 跟socket.send()一样
        这个函数不能block
        """
        self.snd_buffer += binary
        self.start_timer = time.time()
        while self.snd_buffer is not "" and len(self.sndpkt_buffer) <= self.max_unconfirmed_pkt_num:
            data = self.snd_buffer[0: self.mss]
            sndpkt = json.dumps({"seq": self.seq, "data": data, "checksum": 0})
            self.output(sndpkt)
            self.sndpkt_buffer.append(sndpkt)
            self.snd_buffer = self.snd_buffer[self.mss: ]
            self.seq = self.seq + len(data)
            print sndpkt
        return 0

    def recv(self, n):
        """ 应用程序要收 n个字节的数据
        要求实现这个函数的语义 跟socket.recv()一样
        这个函数不能block

        没有数据可以拿的时候 要求返回 err == -1
        """
        binary = self.rcv_buffer[: n]
        self.rcvpkt_buffer = self.rcvpkt_buffer[n: ]
        err = 0
        if binary is "":
            err = -1
        return binary, err

    def input(self, binary):
        """
        网卡收到数据包 转给给Tcp栈处理 重排乱序包的顺序之类
        """
        rcvpkt = json.loads(binary)
        # if bit_error:
        #   return 
        if rcvpkt.has_key("seq"):   # 接收方
            # 乱序处理
            len_rcvpkt_buffer = len(self.rcvpkt_buffer)
            if len_rcvpkt_buffer is 0:
                self.rcvpkt_buffer.append(rcvpkt)
                self.ack = rcvpkt["seq"] + len(rcvpkt["data"])
            else:
                i = len_rcvpkt_buffer
                while i > 0:
                    if rcvpkt["seq"] > self.rcvpkt_buffer[i - 1]["seq"]:
                        self.rcvpkt_buffer.insert(i, rcvpkt)
                        self.ack = rcvpkt["seq"] + len(rcvpkt["data"])
                        break
                    elif rcvpkt["seq"] is self.rcvpkt_buffer[i - 1]["seq"]:
                        break
                    else:
                        i = i - 1
                if i is 0 and rcvpkt["seq"] < self.rcvpkt_buffer[0]["seq"]:
                    self.rcvpkt_buffer.insert(0, rcvpkt)
                    self.ack = recvpkt["seq"] + len(rcvpkt["data"])
            # 给发送方发送ack
            sndpkt = json.dumps({"ack": self.ack, "checksum": 0})
            self.output(sndpkt)
            # 拆数据包 
            while self.rcvpkt_buffer and self.ack > self.rcvpkt_buffer[0]["seq"]:
                self.rcv_buffer = self.rcv_buffer + self.rcvpkt_buffer.pop(0)["data"]
        elif rcvpkt.has_key("ack"): # 发送方
            if rcvpkt["ack"] > self.sndpkt_buffer[0]["seq"]:
                while len(self.sndpkt_buffer) is not 0 and rcvpkt["ack"] > self.sndpkt_buffer[0]["seq"]:
                    self.sndpkt_buffer.pop(0)
                self.duplicate_ack_num = 0
                # 重新计算self.timeout_interval
                sample_rtt = time.time() - self.start_timer
                alpha = 0.125
                estimated_rtt = (1 - alpha) * estimated_rtt + alpha * sample_rtt
                beta = 0.25
                dev_rtt = (1 - beta) * dev_rtt + beta * abs(sample_rtt - estimated_rtt)
                self.timeout_interval = estimated_rtt + 4 * dev_rtt
            else:
                self.duplicate_ack_num = self.duplicate_ack_num + 1
                if self.duplicate_ack_num == 3:
                    if not self.sndpkt_buffer:
                        return
                    sndpkt = self.sndpkt_buffer[0]
                    self.output(sndpkt)
                    print sndpkt
        else:
            assert(False)
        
