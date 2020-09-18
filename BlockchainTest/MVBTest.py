from BlockchainNetwork.MVB import *
from threading import Thread
import random
import time

coloredlogs.install()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)


class MVBTest:
    def __init__(self, initialNodeCnt, initialOutputCnt):
        self.mvb = MVB()
        self.signingKeysList = []
        self.pubKeysList = []
        self.pubKeysByteList = []
        self.__initialSigningKeys(initialOutputCnt)
        self.__initialPubKeys()

        self.mvb.generateGenesisBlock(self.pubKeysByteList)
        self.mvb.initialNodes(initialNodeCnt)

    def doubleSpendTest(self):
        """
            txOutputs is the genesis output.
            txOutputs[0] was used twice in this test.
            Both Tx1 and Tx2 make txOutputs[0] as input.
            When Tx2 is mined, the verification will be failed.
        """
        log.info("--------------------Double spend test now started-------------------")
        Tx1Inputs = [TxInput(self.mvb.genesisBlock.tx.txNumber, self.mvb.genesisBlock.tx.txOutputs[0])]
        Tx1Outputs = [TxOutput(500, self.pubKeysByteList[0]),
                      TxOutput(500, self.pubKeysByteList[1])]
        Tx1 = Transaction(0, Tx1Inputs, Tx1Outputs, None)
        Tx1.sign(self.signingKeysList[0])
        Tx1.getNumber()

        Tx2Inputs = [TxInput(1, self.mvb.genesisBlock.tx.txOutputs[0])]
        Tx2Outputs = [TxOutput(500, self.pubKeysByteList[2]),
                      TxOutput(500, self.pubKeysByteList[3])]
        Tx2 = Transaction(0, Tx2Inputs, Tx2Outputs, None)
        Tx2.sign(self.signingKeysList[0])
        Tx2.getNumber()

        self.mvb.txWaitingPool += [Tx1, Tx2]
        self.mvb.broadcastTxPools()
        for i, node in enumerate(self.mvb.networkNodes):
            nodeThread = Thread(target=self.threadMining, args=(node, 1))
            nodeThread.start()

    def inputOutputSumTest(self):
        log.info("--------------------Input output sum test now started-------------------")
        ledger = self.mvb.networkNodes[0].ledger
        print(len(ledger))

        # sender is 0
        newTx3InputNumber = ledger[1].nowBlock.tx.txNumber
        newTx3InputOutput = ledger[1].nowBlock.tx.txOutputs[0]
        Tx3Inputs = [TxInput(newTx3InputNumber, newTx3InputOutput)]
        Tx3Outputs = [TxOutput(250, self.pubKeysByteList[0]),
                      TxOutput(250, self.pubKeysByteList[14])]

        Tx3 = Transaction(0, Tx3Inputs, Tx3Outputs, None)
        Tx3.sign(self.signingKeysList[0])
        Tx3.getNumber()
        print(Tx3.txNumber)

        # sender is 1
        newTx4InputNumber1 = ledger[0].nowBlock.tx.txNumber
        newTx4InputNumber2 = ledger[1].nowBlock.tx.txNumber
        # 1000 from genesis tx
        newTx4InputOutput1 = ledger[0].nowBlock.tx.txOutputs[1]
        # 500 from tx1
        newTx4InputOutput2 = ledger[1].nowBlock.tx.txOutputs[1]
        # input sum is 1500, output sum is 1400, invalid tx
        Tx4Inputs = [TxInput(newTx4InputNumber1, newTx4InputOutput1),
                     TxInput(newTx4InputNumber2, newTx4InputOutput2)]
        Tx4Outputs = [TxOutput(800, self.pubKeysByteList[4]),
                      TxOutput(600, self.pubKeysByteList[14])]

        Tx4 = Transaction(0, Tx4Inputs, Tx4Outputs, None)
        Tx4.sign(self.signingKeysList[1])
        Tx4.getNumber()

        self.mvb.txWaitingPool += [Tx3, Tx4]
        self.mvb.broadcastTxPools()
        for i, node in enumerate(self.mvb.networkNodes):
            nodeThread = Thread(target=self.threadMining, args=(node, 1))
            nodeThread.start()

    def badStructureTest(self):
        pass

    def broadcastBlockTest(self):
        pass

    def sigVerifyTest(self):
        pass

    def threadMining(self, node: Node, i):
        # nowTime = time.time()
        # while True:
        #     node.receiveBroadcastBlock()
        #     for tx in node.globalTxPool:
        #         node.mineBlock(tx)
        #         node.globalTxPool.remove(tx)
        #     if time.time() - nowTime > 10:
        #         break
        for tx in node.globalTxPool:
            node.mineBlock(tx)
        node.globalTxPool = []
        node.saveToFile()

    def __initialSigningKeys(self, cnt: int) -> None:
        """
            Generate and update signingKeys List for the network
        """
        for _ in range(cnt):
            self.signingKeysList.append(SigningKey.generate())
        log.info(str(cnt) + " signing keys have been generated successfully")
        # sleep(2)

    def __initialPubKeys(self):
        for signingKey in self.signingKeysList:
            verifyKey = signingKey.verify_key
            verifyKeyByte = verifyKey.encode(encoder=HexEncoder)
            self.pubKeysList.append(verifyKey)
            self.pubKeysByteList.append(verifyKeyByte)
        log.info(str(len(self.pubKeysList)) + " public keys have been generated successfully")
        # sleep(2)