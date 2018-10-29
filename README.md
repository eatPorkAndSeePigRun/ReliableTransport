# ReliableTransport

基于LatencySimulator的不可靠投递服务，实现一个可靠的保证送达的数据包有序的协议

`Tcp.py`中主要使用的GBN和拥塞控制

![GBN发送方的FSM描述](./doc/image1.png)

![GBN接收方的FSM描述](./doc/image2.png)

![拥塞控制的FSM描述](./doc/image3.png)

+ 可继续扩展的部分：
    + 三次握手
    + 四次挥手
    + 使用校验和
    + 流量控制
    + GBN换成SR