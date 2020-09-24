import logging
import coloredlogs

from nacl.signing import VerifyKey
from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError

from Blockchain.Block import *
from Blockchain.Transaction import Transaction
from queue import Queue
from hashlib import sha256
from typing import List

coloredlogs.install()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)


class Node:
    def __init__(self, genesisBlock: Block = None, nodeID: str = None) -> None:
        # initial the first block into genesisBlock
        self.latestBlockTreeNode: BlockTreeNode = BlockTreeNode(None, genesisBlock, 1)
        self.ledger: List[BlockTreeNode] = [self.latestBlockTreeNode]  # blocks array, type: List[BlockTreeNode]
        self.id: str = nodeID
        self.allNodeList: List[Node] = []  # all the Nodes in the Blockchain network
        self.receivedBlockQueue = Queue()  # storage the received Block from other Node
        self.miningDifficulty = 0x07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
        self.globalTxPool: List[Transaction] = []

    def broadcastNewBlock(self, newBlock: Block) -> None:  # broadcast the new mined block to the whole network
        for networkNode in self.allNodeList:
            if networkNode.id != self.id:
                networkNode.receivedBlockQueue.put(newBlock)

    def receiveBroadcastBlock(self) -> None:
        if self.receivedBlockQueue.empty():
            return
        else:
            while not self.receivedBlockQueue.empty():
                newBlock = self.receivedBlockQueue.get()
                for blockTreeNode in self.ledger:
                    if self.__verifyBlockPrevHash(blockTreeNode.nowBlock, newBlock):
                        prevBlockTreeNode = blockTreeNode
                        break
                else:
                    log.error("Node " + self.id + " :" + "Block Verification Failed! Prev Hash is not satisfied")
                    return
                if not prevBlockTreeNode:
                    log.error("Node " + self.id + " :" + "Block Verification Failed! No pre hash found!")
                    return
                if not self.__verifyTxNotOnBlockchain(newBlock.tx):
                    log.error("Node " + self.id + " :" + "Block Verification Failed! Received block is already on the ledger")
                    return
                if self.verifyBlock(newBlock):
                    newBlockTreeNode = BlockTreeNode(prevBlockTreeNode, newBlock, prevBlockTreeNode.blockHeight + 1)
                    self.ledger.append(newBlockTreeNode)
                    self.__updateLongestChain(newBlockTreeNode)

    def mineInvalidBlock(self, tx: Transaction, isInvalidPrevHash = False, isInvalidPOW = False) -> None:
        """
            This function is only used for testing.
            mine a new invalid block with the tx, either prev_hash or pow is invalid
        """
        if not isInvalidPrevHash and not isInvalidPOW:
            return
        # tx not valid
        if not self.verifyTx(tx):
            # because this transaction is already in the ledger
            if not self.__verifyTxNotOnBlockchain(tx):
                log.error("Node " + self.id + " :" + "Tx Verification Failed! This Tx is already on the ledger")
            return
        blockPow = str(self.miningDifficulty + 1)
        hashTarget = self.miningDifficulty
        prevBlock = self.latestBlockTreeNode

        prevHash = sha256(prevBlock.nowBlock.toString().encode('utf-8')).hexdigest()
        txAndPrevHashMsg = tx.toString() + prevHash
        nonce = 0
        while int(blockPow, base=16) > hashTarget:
            blockMessage = txAndPrevHashMsg + str(nonce)
            blockPow = sha256(blockMessage.encode('utf-8')).hexdigest()
            nonce += 1
        nonce -= 1

        newBlock = Block(tx, prevHash, nonce, blockPow)

        if isInvalidPrevHash:
            newBlock.prev += "1"  # make the prev hash invalid
        elif isInvalidPOW:
            newBlock.pow = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
        newBlockTreeNode = BlockTreeNode(prevBlock, newBlock, self.latestBlockTreeNode.blockHeight + 1)
        self.__updateNewMinedBlock(newBlock, newBlockTreeNode)

    def mineBlock(self, tx: Transaction) -> None:  # mine a new block with the tx
        # tx not valid
        if not self.verifyTx(tx):
            # because this transaction is already in the ledger
            if not self.__verifyTxNotOnBlockchain(tx):
                log.error("Node " + self.id + " :" + "Tx Verification Failed! This Tx is already on the ledger")
            return
        blockPow = str(self.miningDifficulty + 1)
        hashTarget = self.miningDifficulty
        prevBlock = self.latestBlockTreeNode

        prevHash = sha256(prevBlock.nowBlock.toString().encode('utf-8')).hexdigest()
        txAndPrevHashMsg = tx.toString() + prevHash
        nonce = 0
        while int(blockPow, base=16) > hashTarget:
            blockMessage = txAndPrevHashMsg + str(nonce)
            blockPow = sha256(blockMessage.encode('utf-8')).hexdigest()
            nonce += 1
        nonce -= 1

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
            2. Validate the transaction in the block
        """
        return self.__verifyBlockPow(newBlock) and self.verifyTx(newBlock.tx)

    def getJson(self):
        jsonObj = {"Blocks": []}
        for treeNode in self.ledger:
            jsonObj["Blocks"].append(treeNode.nowBlock.getJsonObj())
        return json.dumps(jsonObj, indent=4)

    def saveToFile(self):
        nodeJson = self.getJson()
        with open("./NodesLedger/Node-" + str(self.id) + '.json', 'w', encoding='utf-8') as f:
            f.write(nodeJson)

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

    def __broadcastTxPool(self, tx: Transaction) -> None:
        for networkNode in self.allNodeList:
            if networkNode != self:
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
            if tx.txNumber == pBlock.nowBlock.tx.txNumber:
                # log.error("Verification Failed! Tx is already on the blockchain")
                return False
            pBlock = pBlock.prevBlockTreeNode
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

        flags = [self.__verifyTxNumberHash(tx), self.__verifyTxInputsNumber(tx), self.__verifyTxPubKeyAndSig(tx),
                 self.__verifyTxDoubleSpend(tx), self.__verifyTxInOutSum(tx)]
        __flag = True
        for flag in flags:
            __flag = __flag and flag
        return __flag

    def __verifyTxNumberHash(self, tx: Transaction) -> bool:
        #  Ensure number hash is correct
        numberHash = tx.txNumber
        nowHash = tx.getNumber()
        __flag = tx.txNumber != '' and nowHash == numberHash
        if not __flag:
            log.error("Node " + self.id + " :" + "Tx Verification Failed! Number hash is not correct")
        return __flag

    def __verifyTxInputsNumber(self, tx: Transaction) -> bool:
        #  each number in the input exists as a transaction already on the blockchain
        #  each output in the input actually exists in the named transaction
        validInputCounter = 0
        for txInput in tx.txInputs:
            numberExist = False
            outputCorrect = False
            pBlock = self.latestBlockTreeNode
            while pBlock:
                if txInput.number == pBlock.nowBlock.tx.txNumber:  # find that old transaction in the ledger
                    numberExist = True
                    for pBlockTxOutput in pBlock.nowBlock.tx.txOutputs:
                        if txInput.output.isEqual(pBlockTxOutput):  # verify the output content
                            outputCorrect = True
                            break
                    break
                pBlock = pBlock.prevBlockTreeNode
            if numberExist and outputCorrect:
                validInputCounter += 1
        __flag = validInputCounter == len(tx.txInputs)
        if not __flag:
            log.error("Node " + self.id + " :" + "Tx Verification Failed! Inputs are not correct")
        return __flag

    def __verifyTxPubKeyAndSig(self, tx: Transaction) -> bool:
        #  each output in the input has the same public key, and that key can be used to verify the signature of the transaction
        if not tx.txInputs:
            return False
        senderPubKey: bytes = tx.txInputs[0].output.pubKey
        for txInput in tx.txInputs:
            if txInput.output.pubKey != senderPubKey:
                log.error("Node " + self.id + " :" + "Tx Verification Failed! Input pubKey is not unique")
                return False

        verifyKey = VerifyKey(senderPubKey, HexEncoder)
        try:
            verifyKey.verify(tx.sig.encode('utf-8'), encoder=HexEncoder)
            return True
        except BadSignatureError:
            log.error("Node " + self.id + " :" + "Tx Verification Failed! Signature verification failed")
            return False

    def __verifyTxDoubleSpend(self, tx: Transaction) -> bool:
        #  public key is the most recent recipient of that output (i.e. not a double-spend)
        for txInput in tx.txInputs:
            pBlock = self.latestBlockTreeNode
            while pBlock:
                for pBlockTxInput in pBlock.nowBlock.tx.txInputs:
                    if txInput.isEqual(pBlockTxInput):
                        log.error("Node " + self.id + " :" + "Tx Verification Failed! Double spend detected")
                        return False
                pBlock = pBlock.prevBlockTreeNode
            return True

    def __verifyTxInOutSum(self, tx: Transaction) -> bool:
        #  the sum of the input and output values are equal
        inputSum, outputSum = 0, 0
        for txInput in tx.txInputs:
            inputSum += txInput.output.value
        for txOutput in tx.txOutputs:
            outputSum += txOutput.value
        __flag = inputSum == outputSum
        if not __flag:
            log.error("Node " + self.id + " :" + "Tx Verification Failed! Tx Inputs val sum is not equal to outputs sum")
        return __flag

    def __verifyBlockPow(self, newBlock: Block) -> bool:
        blockMsg = newBlock.tx.toString() + newBlock.prev + str(newBlock.nonce)
        blockPow = sha256(blockMsg.encode('utf-8')).hexdigest()
        if newBlock.pow != str(blockPow):
            log.error("Node " + self.id + " :" + "Block Verification Failed! The pow does not match the message")
            return False
        __flag = int(newBlock.pow, base=16) <= 0x07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
        if not __flag:
            log.error("Node " + self.id + " :" + "Block Verification Failed! The pow is not satisfied")
        return __flag

    def __verifyBlockPrevHash(self, prevBlock: Block, newBlock: Block) -> bool:
        prevEncode = prevBlock.toString().encode('utf-8')
        prevHash = sha256(prevEncode).hexdigest()
        __flag = prevHash == newBlock.prev
        return __flag
