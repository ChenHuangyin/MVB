from Blockchain import Block
from Blockchain import Transaction
from queue import Queue


class Node:
    def __init__(self, genesisBlock: Block, nodeID: str):
        # initial the first block into genesisBlock
        self.latestBlockTreeNode = Block.BlockTreeNode(None, genesisBlock, None, 1)
        self.ledger = [self.latestBlockTreeNode]  # blocks array, type: List[BlockTreeNode]
        self.id = nodeID
        self.allNodeList = []  # List[Node], all the Nodes in the blockchain network
        self.receivedBlockQueue = Queue()  # storage the received Block from other Node
        self.miningTxQueue = Queue()  # storage the waiting Tx

    def broadcastNewBlock(self, newBlock: Block):
        for node in self.allNodeList:
            node.receivedBlockQueue.put(newBlock)

    def updateNewBlock(self, newBlock: Block):
        pass

    def mining(self, prevBlock: Block, tx: Transaction):
        pass

    def verify(self) -> bool:
        return self.__verifyNumberNotAlreadyExist() & self.__verifyTxStructure() & self.__verifyPow() & self.__verifyPreHash()

    def __verifyNumberNotAlreadyExist(self) -> bool:
        pass

    def __verifyTxStructure(self) -> bool:
        pass

    def __verifyPow(self) -> bool:
        pass

    def __verifyPreHash(self) -> bool:
        pass
