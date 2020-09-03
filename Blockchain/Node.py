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

    def broadcastNewBlock(self, newBlock: Block):  # broadcast the new mined block to the whole network
        for node in self.allNodeList:
            node.receivedBlockQueue.put(newBlock)

    def updateNewBlock(self, newBlock: Block):  # put the received new block into the ledger
        pass

    def mineBlock(self, prevBlock: Block, tx: Transaction):  # mine a new block with the only one tx
        pass

    def verifyTx(self) -> bool:  # verify a Tx
        pass

    def verifyBlock(self) -> bool:  # verify a block
        return self.__verifyNumberNotAlreadyExist() & self.__verifyTxStructure() & self.__verifyPow() & self.__verifyPreHash()

    def __verifyNumberNotAlreadyExist(self) -> bool:
        pass

    def __verifyTxStructure(self) -> bool:
        pass

    def __verifyPow(self, newBlock: Block) -> bool:
        return newBlock.pow <= 0x07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

    def __verifyPreHash(self) -> bool:
        pass
