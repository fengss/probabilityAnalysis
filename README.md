# 概率的问题描述  


## 区块链节点插件版本中奖概率计算

```
概率做进区块链,用户抽奖记录存于区块链的交易,交易会打进区块
用户请求抽奖会向某个区块链节点提交一份交易

各个节点要协调中奖的数据,并计算出是否用户中奖的情况
奖品成函数无限收敛,保证一直有奖品或者在规定的时间内一直有奖品,奖品的发放呈高到低递减


奖品发放的实时性难在于节点对等,谁都不知道哪个节点发了,奖品的数据一致性根本没法保证?
解决:实时要有leader节点发放
假如说用户发送抽奖数据交易的节点是上个区块打包的节点,那么允许奖品的发放,如果不是奖品就直接不发放
从而设计二个考虑点:
1:全局按时间分布划分奖品发放的数量
2:实际中奖,根据交易中的抽奖数据来实际操作此次中奖情况

并且改造全节点都可出块..........
```

## 后端服务器中奖概率计算

```
保证一直有奖品或者在规定的时间内一直有奖品,奖品的发放呈高到低递减,数量极限于0

用户提交的数据根据之前的中奖数据参考
```

- 全局概率
    
    由曲线决定

- 局部概率
    
    动态调整发放的数量和时间点........
