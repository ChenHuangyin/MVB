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
        pass

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
        node.saveToFile()

    def __initialSigningKeys(self, cnt: int) -> None:
        """
            Generate and update signingKeys List for the network
        """
        for _ in range(cnt):
            self.signingKeysList.append(SigningKey.generate())
        log.info(str(cnt) + " signing keys have been generated successfully")
        sleep(2)

    def __initialPubKeys(self):
        for signingKey in self.signingKeysList:
            verifyKey = signingKey.verify_key
            verifyKeyByte = verifyKey.encode(encoder=HexEncoder)
            self.pubKeysList.append(verifyKey)
            self.pubKeysByteList.append(verifyKeyByte)
        log.info(str(len(self.pubKeysList)) + " public keys have been generated successfully")
        sleep(2)