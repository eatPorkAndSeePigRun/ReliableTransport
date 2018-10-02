```
现实世界中 计算机协议实现是一层一层的
互联网提供的IP协议 数据包传输的功能是有限制的
    1. 不保证能发到对端 见LatencySimulator.lost_ratio
    2. 不能保证投递顺序 见LatencySimulator.send()里面数据包发送到达实际的随机
        l.append((data, u(clock() + self.min_rtt + self.rtt * random.random())))
    3. 单个数据包的大小有限制 见LatencySimulator.nmax 
        看LatencySimulator.send()当包过大的时候网络直接丢弃不传递这个包
        if len(l) >= self.nmax:
            return 

这个要求你实现一个Tcp类
基于LatencySimulator的不可靠投递服务
实现一个可靠的保证送达的数据包有序的协议

实际上可以想象成 
要模拟的东西有3个
1 变量a 机器A上的TCP 网络协议栈(你可以把网络协议栈 当做操作系统内核）
2 变量b 机器B上的TCP 网络协议栈
3 变量 vnet virutal network A和B机器之间的虚拟网络

下面的while True 内嵌多个while True
只是为了运行简单 所以全部都合并到一块了

想象机器A运行的代码是
while True:
    片段 A1
    片段 A2
    片段 A3

想象机器B运行的代码是
while True:
    片段 A1
    片段 A2
    片段 A3

机器A通过片段A1 每个1秒发送数据包 "abchina"到虚拟网络
要求虚拟网络传递给机器B

机器B通过片段B1 从虚拟网络里面收到数据包
然后把数据包喂给Tcp协议栈 input()
Tcp协议栈把网络传过来的数据拼凑成完成的包给应用程序
应用程序可以b.recv(n)读出来完成的 "abchina" 也就是代码片段B2

同理的 A2和A3与B1和B2类似
```

```
第一个 作业 完全里面这个模块的所有代码
思考怎么实现下面的功能

把A1改成 A发送数据包 "abchina" * 1024 = 7168个字节 给B
补完Tcp类
最终B的多次b.recv() 能够得到原来的7168个字节
```