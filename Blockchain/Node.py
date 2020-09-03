from Blockchain import Block
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


