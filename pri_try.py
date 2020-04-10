#  这些模组居然全部可以用
import hashlib
import random
import string
import json
import threading
from decimal import Decimal
from time import time
from threading import Thread


class Block:
    def __init__(self):
        self.index = None
        #  时间戳
        self.time = None
        #  挖矿难度
        self.difficulty = None
        #  自带的随机数
        self.nonce = None
        #  hash值  自己的hash值
        self.hash = None
        #   前一节点的hash值
        self.previousHash = None
        #  交易信息 应当是一个字典
        self.tranData = None

    #  返回每一个区块的所有信息
    def get_block(self):
        return{
            'Index':self.index,
            'Time':self.time,
            'Difficulty':self.difficulty,
            'Nonce':self.nonce,
            'Hash':self.hash,
            'PreviousHash':self.previousHash,
            'TranData':self.tranData
        }


#  多线程的一个类  表示在单独的线程中运行的活动
#  这里的操作会进行多线程操作
#  这里是对子类的重写  这里的函数看不懂。。
#  这个貌似就是一个比较基础的代码而已。。
class MyThread(threading.Thread):
    def __init__(self, target, args=()):
        super(MyThread, self).__init__()
        self.func = target
        self.args = args
    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

class Miner:
    #  挖矿操作
    def mine(self, index, previousHash, tranData):
        beginTime = time()

        block = Block()
        block.time = time()
        # 数组下标值？？
        block.index = index
        block.previousHash = previousHash
        block.tranData = tranData
        block.difficulty, block.hash, block.nonce = self.generate(previousHash, tranData,block.time)
        endTime = time()

        return block, endTime - beginTime

    #  没有动用self里面的数据，所以使用静态方法
    def generate(self, previousHash, tranData,time):
        difficulty = 0
        nonce = random.randrange(0, 99999)
        tmp = f'{previousHash}{nonce}{tranData}{str(time)}'.encode(encoding='UTF-8', errors='strict')
        #  得到的数据返回十六进制数
        hash = hashlib.sha256(tmp).hexdigest()
        #  若得到的16进制数字最后一位部位0   则继续进行挖矿
        #  难度用挖矿的次数来表示  这也是一种工作量证明
        while hash[-1] != '0':
            difficulty += 1
            nonce = random.randrange(0, 99999)
            tmp = f'{previousHash}{nonce}{tranData}{str(time)}'.encode(encoding='UTF-8', errors='strict')
            hash = hashlib.sha256(tmp).hexdigest()
        return difficulty, hash, nonce



class BlockChain:
    #  生成一个区块链
    def __init__(self,Hash):
        # 区块链中的区块
        self.chain=[]
        #  进行挖矿的矿工
        self.miner=[]
        #  初始化5个矿工
        for i in range(5):
            self.miner.append(Miner())
        #  results？？
        self.results=[]

        self.newblock(Hash)

    def last_block(self):
        if(len(self.chain)):
            return self.chain[-1]
        else:
            return None
    def get_trans(self):
        return json.dumps(
            {
                #  random.sample 截取列表指定长度的随机数
                #  string.ascii_letters 表示生成所有字母，从a-z和从A-Z
                #  string.digits表示生成所有的数字
                #  故这行代码是生成a-z,A-Z,0-9随机组合的八位数字。
                'sender':''.join(random.sample(string.ascii_letters+string.digits,8)),

                #  下一行代码同理
                'recipient':''.join(random.sample(string.ascii_letters+string.digits,8)),
                #  交易的虚拟货币数量还是？
                'amount':random.randrange(1,1000),
            }
        )

    #  新区块的生成函数
    def newblock(self,Hash=None):
        #  前一个区块有hash值，则生成的不是创世区块
        if Hash:
            #  生成创世区块

            block=Block()
            #  内部的内容，可以自己确定，可以是任何形式  都将作为hash值的确定依据
            block.index=0
            #  这里的nonce应当由difficulty确定？
            block.nonce=random.randrange(0,99999)
            block.previousHash='0'
            block.difficulty=0
            block.time=time()
            #  生成初始随机交易  这里可以优化
            block.tranData=self.get_trans()
            # 将交易信息、前一区块hash值、随机数、时间戳都作为hash值得生成依据
            #  f-string函数   f"{}{}"可以生成诸多字符串的合集
            #  难度还不知道怎样确定
            #  str.encode  可以指定的方式编码
            tmp = f'{block.previousHash}{block.nonce}{block.tranData}{block.time}'.encode(encoding='UTF-8',errors='strict')
            # 下面生成hash值
            # sha256函数会把输入的任何数据转换成256位01编码  也就是我们需要的hash值
            block.hash = hashlib.sha256(tmp).hexdigest()
            # 将生成的区块装入到区块链之中
            self.chain.append(block)
        else:
            #  创建矿工个数的线程
            for i in range(len(self.miner)):

                pm = MyThread(target=self.miner[i].mine, #线程执行的方法名字
                              #   方法接受的参数
                              args=(
                                    len(self.chain),
                                    #  previousHash
                                    self.last_block().get_block()['Hash'],
                                    #  随机的一次交易信息
                                    self.get_trans()))
                pm.start()
                pm.join()
                self.results.append(pm.get_result())
            #  每个返回都是一个区块和一段时间
            #  所有区块开始挖矿的时间是相同的

            #  展示一下挖一个区块时生成的所有的区块
            print("All Blocks are there")
            for result in self.results:
                print(result[0].get_block())

            #  下面对生成的区块进行筛选

            #  至少有一个的
            first=self.results[0][0]
            #  时间修改为十进制
            mitime=Decimal(self.results[0][1])

            for i in range(1,len(self.results)):
                if Decimal(self.results[i][1])<mitime:
                    first=self.results[i][0]
                    mitime=Decimal(self.results[i][1])
            self.chain.append(first)
            self.results=[]



    def showchain(self):
        for block in self.chain:
            print(block.get_block())



if __name__=='__main__':
    #  第一个区块的hash取了数值1
    chain=BlockChain(1)
    length=5

    for i in range(length):
        chain.newblock()
    chain.showchain()

