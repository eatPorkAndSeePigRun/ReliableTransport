# coding: utf-8
import json
import time
import logging

filename = str(int(time.time())) + ".log"
myfile_handler = logging.FileHandler(filename)
fmt = logging.Formatter("%(asctime)s, %(filename)s[line:%(lineno)d]: %(message)s")
myfile_handler.setFormatter(fmt)

mylog = logging.getLogger()
mylog.setLevel(logging.INFO)
mylog.addHandler(myfile_handler)


window_max_size = 10240

class Tcp(object):

    def __init__(self, **kw):
        self.output = None
        # 发送方
        self.mss = 100              # 通常设为1460
        self.snd_buffer = ""
        self.sndpkt_buffer = []     # 缓存已发送未被确认的pkt
        self.max_unconfirmed_pkt_num = 500 

        self.start_timer = 0.0      # 定时器 
        self.estimated_rtt = 0
        self.dev_rtt = 0
        self.timeout_interval = 1

        self.last_byte_sent = 0     # 拥塞控制
        self.last_byte_acked = 0
        self.ssthresh = 0xffff      # 或64KB
        self.cwnd = self.mss
        self.duplicate_ack_count = 0

        # 接收方
        self.rcvpkt_buffer = []     # 缓存已正常接收的pkt
        self.rcv_buffer = ""

        self.last_byte_read = 0     # 流量控制
        self.last_byte_rcvd = 0
        self.rwnd = 0xffff          # 随时间变化，rwnd = rcv_buffer - (last_byte_rcvd - last_byte_read)

    def update(self, timestamp):
        # 发送方
        if timestamp - self.start_timer > self.timeout_interval:
            if not self.sndpkt_buffer:
                return
            # 拥塞控制
            if self.cwnd != 1 * self.mss:
                self.ssthresh = self.cwnd / 2
            self.cwnd = 1 * self.mss
            self.duplicate_ack_count = 0
            # 重新发送
            mylog.info("----------------timeout----------------")
            self.retransmit_missing_segment() 
            mylog.info("---------------------------------------")

    def send(self, binary):
        self.snd_buffer += binary
        # 发送方
        self.rdt_send()
        return 0

    def recv(self, n):
        if self.rcv_buffer:
            binary = self.rcv_buffer[: n]
            self.rcv_buffer = self.rcv_buffer[n: ]
            return binary, 0
        else:
            return "", -1

    def input(self, binary):
        if not binary:
            return
        rcvpkt = json.loads(binary)

        if rcvpkt.has_key("ack"):   # 发送方
            if rcvpkt["ack"] > self.last_byte_acked:    # new ack
                if self.cwnd < self.ssthresh:           # 慢启动
                    self.cwnd *= 2
                else:                                   # 拥塞避免
                    self.cwnd = self.cwnd + self.mss * (self.mss / self.cwnd)

                self.duplicate_ack_count = 0
                self.last_byte_acked = rcvpkt["ack"]
                while self.sndpkt_buffer and rcvpkt["ack"] > self.sndpkt_buffer[0]["seq"]:
                    self.sndpkt_buffer.pop(0)   
                self.update_timeout_interval()
                # 继续发送
                self.rdt_send()
            else:                                       # duplicate ack
                self.duplicate_ack_count += 1
                if self.duplicate_ack_count == 3:
                    self.ssthresh = self.cwnd / 2
                    self.cwnd = self.ssthresh + 3 * self.mss
                    mylog.info("--------duplicate_ack-------------")
                    self.retransmit_missing_segment()
                    mylog.info("----------------------------------")
             
        elif rcvpkt.has_key("seq"): # 接收方
            if rcvpkt["seq"] == self.last_byte_rcvd:
                self.rcv_buffer += str(rcvpkt["data"])
                # 发送ack
                self.last_byte_rcvd += len(rcvpkt["data"])
            self.rwnd = window_max_size - len(self.rcv_buffer)
            sndpkt = {"ack": self.last_byte_rcvd, "rwnd": self.rwnd}
            self.output(json.dumps(sndpkt))
            mylog.info("ack: " + str(sndpkt["ack"]))

    def rdt_send(self):
        N = min(self.rwnd, self.cwnd)
        while self.last_byte_sent < self.last_byte_acked + N:
            if not self.snd_buffer:
                return
            data = self.snd_buffer[0: self.mss]
            sndpkt = {"seq": self.last_byte_sent, "data": data}
            self.output(json.dumps(sndpkt))
            mylog.info("seq: " + str(sndpkt["seq"]))
            if self.last_byte_sent == self.last_byte_acked:
                self.start_timer = time.time()
            self.sndpkt_buffer.append(sndpkt)
            self.snd_buffer = self.snd_buffer[self.mss: ]
            self.last_byte_sent += len(data)

    def update_timeout_interval(self):
        # 重新计算self.timeout_interval
        sample_rtt = time.time() - self.start_timer
        alpha = 0.125
        self.estimated_rtt = (1 - alpha) * self.estimated_rtt + alpha * sample_rtt
        beta = 0.25
        self.dev_rtt = (1 - beta) * self.dev_rtt + beta * abs(sample_rtt - self.estimated_rtt)
        self.timeout_interval = self.estimated_rtt + 4 * self.dev_rtt

    def retransmit_missing_segment(self):
        self.start_timer = time.time()
        self.timeout_interval *= 2
        for sndpkt in self.sndpkt_buffer:
            self.output(json.dumps(sndpkt))
            mylog.info("seq: " + str(sndpkt["seq"]))
