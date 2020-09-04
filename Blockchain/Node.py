from nacl.signing import VerifyKey
from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError


from Blockchain.Block import *
from Blockchain.Transaction import *
from queue import Queue
from hashlib import sha256


class Node:
    def __init__(self, genesisBlock: Block, nodeID: str):
        # initial the first block into genesisBlock
        self.latestBlockTreeNode = BlockTreeNode(None, genesisBlock, 1)
        self.ledger = [self.latestBlockTreeNode]  # blocks array, type: List[BlockTreeNode]
        self.id = nodeID
        self.allNodeList = []  # all the Nodes in the blockchain network
        self.receivedBlockQueue = Queue()  # storage the received Block from other Node
        self.miningDifficulty = 0x07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

        self.globalTxPool = []

    def broadcastNewBlock(self, newBlock: Block):  # broadcast the new mined block to the whole network
        for networkNode in self.allNodeList:
            if networkNode != self:
                networkNode.receivedBlockQueue.put(newBlock)

    def receiveBroadcastBlock(self):
        if self.receivedBlockQueue.empty():
            return
        else:
            newBlock = self.receivedBlockQueue.get()
            prevBlockTreeNode = None
            for blockTreeNode in self.ledger:
                if self.__verifyBlockPrevHash(blockTreeNode.nowBlock, newBlock):
                    prevBlockTreeNode = blockTreeNode
                    break
            if not prevBlockTreeNode:
                return
            if self.verifyBlock(newBlock):
                newBlockTreeNode = BlockTreeNode(prevBlockTreeNode, newBlock, prevBlockTreeNode.blockHeight + 1)
                self.ledger.append(newBlockTreeNode)
                self.__updateLongestChain(newBlockTreeNode)

    def mineBlock(self, tx: Transaction) -> None:  # mine a new block with the tx
        blockPow = hex(self.miningDifficulty + 1)
        hashTarget = hex(self.miningDifficulty)
        prevBlock = self.latestBlockTreeNode.nowBlock

        prevHash = sha256(prevBlock.toString().encode('utf-8')).hexdigest()
        txAndPrevHashMsg = tx.toString() + prevHash
        nonce = 0
        while blockPow > hashTarget:
            blockMessage = txAndPrevHashMsg + str(nonce)
            blockPow = sha256(blockMessage.encode('utf-8')).hexdigest()
            nonce += 1
        newBlock = Block(tx, prevHash, nonce, blockPow)
        newBlockTreeNode = BlockTreeNode(prevBlock, newBlock, self.latestBlockTreeNode.blockHeight + 1)

        self.__updateNewMinedBlock(newBlock, newBlockTreeNode)

    def verifyTx(self, tx: Transaction) -> bool:  # verify a Tx
        """
            1. Ensure the transaction is not already on the blockchain (included in an existing valid block)
            2. Ensure the transaction is validly structured
        """

        return self.__verifyTxNotOnBlockchain(tx) and self.__verifyTxStructure(tx)

    def verifyBlock(self, newBlock: Block) -> bool:  # verify a block
        """
            1. Verify the proof-of-work
            2. Verify the prev hash
            3. Validate the transaction in the block
        """
        return self.__verifyBlockPow(newBlock) and self.verifyTx(newBlock.tx)

    def __updateNewMinedBlock(self, newBlock: Block, newBlockTreeNode: BlockTreeNode) -> None:
        # update local ledger and broadcast new Block
        self.ledger.append(newBlockTreeNode)
        self.__updateLongestChain(newBlockTreeNode)
        self.broadcastNewBlock(newBlock)

    def __updateLongestChain(self, newBlockTreeNode: BlockTreeNode) -> None:
        if newBlockTreeNode.blockHeight > self.latestBlockTreeNode.blockHeight:
            oldHeadTreeNode = self.latestBlockTreeNode
            self.latestBlockTreeNode = newBlockTreeNode
            if newBlockTreeNode.prevBlockTreeNode != oldHeadTreeNode:
                pBlockTreeNode = oldHeadTreeNode
                intersectionTreeNode = self.__getIntersection(oldHeadTreeNode, newBlockTreeNode)
                while pBlockTreeNode != intersectionTreeNode:
                    self.__broadcastTxPool(pBlockTreeNode.nowBlock.tx)
                    pBlockTreeNode = pBlockTreeNode.prevBlockTreeNode

    def __broadcastTxPool(self, tx: Transaction):
        for networkNode in self.allNodeList:
            networkNode.globalTxPool.append(tx)

    def __getIntersection(self, treeNode1: BlockTreeNode, treeNode2: BlockTreeNode):
        p1, p2 = treeNode1, treeNode2
        if not p1 or not p2:
            return None
        while p1 != p2:
            p1 = p1.prevBlockTreeNode
            p2 = p2.prevBlockTreeNode
            if p1 == p2:
                return p1
            if not p1:
                p1 = treeNode2
            if not p2:
                p2 = treeNode1
        return p1

    def __verifyTxNotOnBlockchain(self, tx: Transaction) -> bool:
        #  Ensure the transaction is not already on the blockchain (included in an existing valid block)
        pBlock = self.latestBlockTreeNode
        while pBlock:
            if tx.txNumber == pBlock.nowBlock.tx.number:
                return False
            pBlock = pBlock.prevBlock
        return True

    def __verifyTxStructure(self, tx: Transaction) -> bool:
        """
            2. Ensure the transaction is validly structured
                i. number hash is correct
                ii. each input is correct
                    - each number in the input exists as a transaction already on the blockchain
                    - each output in the input actually exists in the named transaction
                    - each output in the input has the same public key, and that key can verify the signature on this transaction
                    - that public key is the most recent recipient of that output (i.e. not a double-spend)
                iii. the sum of the input and output values are equal
        """
        return self.__verifyTxNumberHash(tx) and self.__verifyTxInputsNumber(tx) and self.__verifyTxPubKeyAndSig(tx) and \
            self.__verifyTxDoubleSpend(tx) and self.__verifyTxInOutSum(tx)

    def __verifyTxNumberHash(self, tx: Transaction) -> bool:
        #  Ensure number hash is correct
        if not tx.txNumber:
            return False
        numberHash = tx.txNumber
        nowHash = tx.getNumber()
        return nowHash == numberHash

    def __verifyTxInputsNumber(self, tx: Transaction) -> bool:
        #  each number in the input exists as a transaction already on the blockchain
        #  each output in the input actually exists in the named transaction
        validInputCounter = 0
        for txInput in tx.txInputs:
            numberExist = False
            outputCorrect = False
            pBlock = self.latestBlockTreeNode
            while pBlock:
                if txInput.number == pBlock.nowBlock.tx.number:  # find that old transaction in the ledger
                    numberExist = True
                    for pBlockTxOutput in pBlock.nowBlock.tx.txOutputs:
                        if txInput.output.isEqual(pBlockTxOutput):  # verify the output content
                            outputCorrect = True
                            break
                    break
                pBlock = pBlock.prevBlock
            if numberExist and outputCorrect:
                validInputCounter += 1
        return validInputCounter == len(tx.txInputs)

    def __verifyTxPubKeyAndSig(self, tx: Transaction) -> bool:
        #  each output in the input has the same public key, and that key can verify the signature on this transaction
        if not tx.txInputs:
            return False
        senderPubKey = tx.txInputs[0].output.pubKey
        for txInput in tx.txInputs:
            if txInput.output.pubKey != senderPubKey:
                return False

        txMessage = tx.getMessage()
        verifyKey = VerifyKey(senderPubKey, HexEncoder)
        try:
            verifyKey.verify(txMessage, tx.sig, HexEncoder)
            return True
        except BadSignatureError:
            return False

    def __verifyTxDoubleSpend(self, tx: Transaction) -> bool:
        #  public key is the most recent recipient of that output (i.e. not a double-spend)
        for txInput in tx.txInputs:
            pBlock = self.latestBlockTreeNode
            while pBlock:
                for pBlockTxInput in pBlock.nowBlock.tx.txInputs:
                    if txInput.isEqual(pBlockTxInput):
                        return False
                pBlock = pBlock.prevBlock
            return True

    def __verifyTxInOutSum(self, tx: Transaction) -> bool:
        #  the sum of the input and output values are equal
        inputSum, outputSum = 0, 0
        for txInput in tx.txInputs:
            inputSum += txInput.output.value
        for txOutput in tx.txOutputs:
            outputSum += txOutput.value
        return inputSum == outputSum

    def __verifyBlockPow(self, newBlock: Block) -> bool:
        return newBlock.pow <= 0x07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

    def __verifyBlockPrevHash(self, prevBlock: Block, newBlock: Block) -> bool:
        prevEncode = prevBlock.toString().encode('utf-8')
        prevHash = sha256(prevEncode).hexdigest()
        return prevHash == newBlock.prev
