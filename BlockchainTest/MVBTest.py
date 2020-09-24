import time
import random

from BlockchainNetwork.MVB import *
from threading import Thread

coloredlogs.install()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)


class MVBTest:
    def __init__(self, initialNodeCnt):
        self.mvb = MVB()
        self.signingKeysList = []
        self.pubKeysList = []
        self.pubKeysByteList = []
        self.__initialSigningKeys()
        self.__initialPubKeys()

        self.mvb.generateGenesisBlock(self.pubKeysByteList)
        self.mvb.initialNodes(initialNodeCnt)

        for i, node in enumerate(self.mvb.networkNodes):
            nodeThread = Thread(target=self.threadMining, args=(node, 1))
            nodeThread.start()

    def multipleValidTxTest(self):
        """
            This method tests multiple valid transactions
        """
        log.info("--------------------Multiple valid Tx tests now started-------------------")

        self.mvb.txWaitingPool += self.readTxFromFile('./TxFiles/MultipleValidTestTx.json')
        self.mvb.broadcastTxPools()

    def doubleSpendTest(self):
        """
            txOutputs is the genesis output.
            txOutputs[0] was used twice in this test.
            Both Tx1 and Tx2 make txOutputs[0] as input.
            When Tx2 is mined, the verification will be failed.
        """
        log.info("--------------------Double spend test now started-------------------")
        log.info("A pair of valid and invalid transactions is added into GlobalTx Pool")

        self.mvb.txWaitingPool += self.readTxFromFile('./TxFiles/DoubleSpendTestTx.json')
        self.mvb.broadcastTxPools()

    def inputOutputSumTest(self):
        log.info("--------------------Input output sum test now started-------------------")
        log.info("A pair of valid and invalid Transactions is added into GlobalTx Pool")

        self.mvb.txWaitingPool += self.readTxFromFile('./TxFiles/InputOutputSumTestTx.json')
        self.mvb.broadcastTxPools()

    def sigVerifyTest(self):
        log.info("--------------------Signature verify test now started-------------------")
        log.info("A pair of valid and invalid Transactions is added into GlobalTx Pool")

        self.mvb.txWaitingPool += self.readTxFromFile('./TxFiles/SigVerifyTestTx.json')
        self.mvb.broadcastTxPools()

    def numberHashTest(self):
        log.info("--------------------Number hash test now started-------------------")
        log.info("A pair of valid and invalid Transactions is added into GlobalTx Pool")

        self.mvb.txWaitingPool += self.readTxFromFile('./TxFiles/NumberHashTestTx.json')
        self.mvb.broadcastTxPools()

    def txInputsExistTest(self):
        log.info("--------------------Transaction inputs exist test now started-------------------")
        log.info("A pair of valid and invalid Transactions is added into GlobalTx Pool")

        self.mvb.txWaitingPool += self.readTxFromFile('./TxFiles/TxInputsExistTestTx.json')
        self.mvb.broadcastTxPools()

    def prevHashMatchTest(self):
        log.info("--------------------Prev Hash test now started-------------------")
        log.info("Node 2 broadcast a Block with invalid prev-hash to the other nodes")

        txList = self.readTxFromFile('./TxFiles/PrevHashMatchTestTx.json')
        self.mvb.networkNodes[1].mineInvalidBlock(txList[0], isInvalidPrevHash=True)

    def blockPOWTest(self):
        log.info("--------------------Block POW test now started-------------------")
        log.info("Node 1 broadcast a Block with invalid POW to the other nodes")

        txList = self.readTxFromFile('./TxFiles/BlockPOWTestTx.json')
        self.mvb.networkNodes[0].mineInvalidBlock(txList[0], isInvalidPOW=True)

    def threadMining(self, node: Node, i):
        nowTime = time.time()
        while True:
            sleep(random.uniform(0, 0.1))
            node.receiveBroadcastBlock()
            for tx in node.globalTxPool:
                node.mineBlock(tx)
                if node.globalTxPool:
                    node.globalTxPool.remove(tx)
            if time.time() - nowTime > 15:
                break

        node.saveToFile()

    def createTxJsonFile(self, FILENAME: str, txList: List[Transaction]):
        txListJsonObj = {'txList': []}
        for tx in txList:
            txListJsonObj['txList'].append(tx.getJsonObj())
        with open(FILENAME, 'w', encoding='utf-8') as f:
            f.write(json.dumps(txListJsonObj, indent=4))

    def readTxFromFile(self, FILENAME: str) -> List[Transaction]:
        txList = []
        with open(FILENAME, 'r', encoding='utf-8') as f:
            txListJsonObj = json.load(f)
        for txObj in txListJsonObj['txList']:
            newTx = Transaction(jsonObj=txObj)
            txList.append(newTx)
        return txList

    def __initialSigningKeys(self) -> None:
        """
            Generate and update signingKeys List for the network
        """
        seedStr = '0' * 31
        seedNum = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
        seedList = []
        for i in range(15):
            seed = seedStr + seedNum[i]
            seedList.append(seed.encode('utf-8'))

        for seed in seedList:
            self.signingKeysList.append(SigningKey(seed))
        log.info("15 signing keys have been generated successfully")

    def __initialPubKeys(self):
        for signingKey in self.signingKeysList:
            verifyKey = signingKey.verify_key
            verifyKeyByte = verifyKey.encode(encoder=HexEncoder)
            self.pubKeysList.append(verifyKey)
            self.pubKeysByteList.append(verifyKeyByte)
        log.info(str(len(self.pubKeysList)) + " public keys have been generated successfully")
